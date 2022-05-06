#!/usr/bin/env python3

import singer
import re
import os
import time

import argparse
from argparse import Namespace
from singer.catalog import Catalog
import tap_framework

from tap_amazon_advertising.client import AmazonAdvertisingClient
from tap_amazon_advertising.streams import AVAILABLE_STREAMS

LOGGER = singer.get_logger()  # noqa

REQUIRED_CONFIG_KEYS = ['client_id', 'client_secret', 'refresh_token', 'redirect_uri', 'start_date', 'profiles', 'region']

''' MODIFIED singer.utils.parse_args() to handle multi-region (NA, EU, FE) '''
def parse_args_list(required_config_keys):
    '''Parse standard command-line args.
    Parses the command-line arguments mentioned in the SPEC and the
    BEST_PRACTICES documents:
    -c,--config     Config file
    -s,--state      State file
    -d,--discover   Run in discover mode
    -p,--properties Properties file: DEPRECATED, please use --catalog instead
    --catalog       Catalog file
    Returns the parsed args object from argparse. For each argument that
    point to JSON files (config, state, properties), we will automatically
    load and parse the JSON file.
    '''
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-c', '--config',
        help='Config file',
        required=True)

    parser.add_argument(
        '-s', '--state',
        help='State file')

    parser.add_argument(
        '-p', '--properties',
        help='Property selections: DEPRECATED, Please use --catalog instead')

    parser.add_argument(
        '--catalog',
        help='Catalog file')

    parser.add_argument(
        '-d', '--discover',
        action='store_true',
        help='Do schema discovery')

    parsed_args = parser.parse_args()

    if parsed_args.config:
        setattr(parsed_args, 'config_path', parsed_args.config)
        config_list = singer.utils.load_json(parsed_args.config)
        if not isinstance(config_list, list):
            raise Exception("Config SHOULD be a LIST!")

    args_list = []
    for config in config_list:
        singer.utils.check_config(config, required_config_keys)
        new_arg = Namespace(config=config)

        if parsed_args.state:
            setattr(parsed_args, 'state_path', parsed_args.state)
            new_arg.state = singer.utils.load_json(parsed_args.state)
        else:
            new_arg.state = {}
        if parsed_args.properties:
            setattr(parsed_args, 'properties_path', parsed_args.properties)
            new_arg.properties = singer.utils.load_json(parsed_args.properties)
        if parsed_args.catalog:
            setattr(parsed_args, 'catalog_path', parsed_args.catalog)
            new_arg.catalog = Catalog.load(parsed_args.catalog)
        else:
            new_arg.catalog = parsed_args.catalog
        
        new_arg.discover = parsed_args.discover
        
        args_list.append(new_arg)

    return args_list

def expand_env(config):
    assert isinstance(config, dict)

    def repl(match):
        env_key = match.group(1)
        return os.environ.get(env_key, "")

    def expand(v):
        assert not isinstance(v, dict)
        if isinstance(v, str):
            return re.sub(r"env\[(\w+)\]", repl, v)
        else:
            return v

    copy = {}
    for k, v in config.items():
        if isinstance(v, dict):
            copy[k] = expand_env(v)
        elif isinstance(v, list):
            copy[k] = [expand_env(x) if isinstance(
                x, dict) else expand(x) for x in v]
        else:
            copy[k] = expand(v)

    return copy

class AmazonAdvertisingRunner(tap_framework.Runner):
    pass


@singer.utils.handle_top_exception(LOGGER)
def main():
    args_list = parse_args_list(required_config_keys=REQUIRED_CONFIG_KEYS)
    LOGGER.info(f"start_time: {time.time()}")
    for args in args_list:
        if not args.discover:
            args.config = expand_env(args.config)

        client = AmazonAdvertisingClient(args.config)

        runner = AmazonAdvertisingRunner(
            args, client, AVAILABLE_STREAMS)

        if args.discover:
            runner.do_discover()
            break
        else:
            runner.do_sync()


if __name__ == '__main__':
    main()
