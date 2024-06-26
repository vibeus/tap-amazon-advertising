import json
import singer

from dateutil.parser import parse

LOGGER = singer.get_logger()


def get_last_record_value_for_table(state, table, country_code):
    last_value = state.get('bookmarks', {}) \
                      .get(table, {}) \
                      .get(country_code)

    if last_value is None:
        return None

    return parse(last_value).date()


def incorporate(state, table, field, value, country_code):
    if value is None:
        return state

    new_state = state.copy()

    parsed = parse(value).strftime("%Y-%m-%dT%H:%M:%SZ")

    if 'bookmarks' not in new_state:
        new_state['bookmarks'] = {}

    if(new_state['bookmarks'].get(table, {}).get(country_code) is None or
       new_state['bookmarks'].get(table, {}).get(country_code) < value):
        new_state['bookmarks'][table] = {
            'field': field,
            country_code: parsed,
        }

    return new_state


def save_state(state):
    if not state:
        return

    LOGGER.info('Updating state.')

    singer.write_state(state)


def load_state(filename):
    if filename is None:
        return {}

    try:
        with open(filename) as handle:
            return json.load(handle)
    except:
        LOGGER.fatal("Failed to decode state file. Is it valid json?")
        raise RuntimeError
