import math
import pytz
import singer
import singer.utils
import singer.metrics
import time
import datetime

from tap_amazon_advertising.config import get_config_start_date
from tap_amazon_advertising.state import incorporate, save_state, \
    get_last_record_value_for_table

from tap_framework.streams import BaseStream as base

LOGGER = singer.get_logger()

# use BASE_URL[self.config['region']]
BASE_URL = {
    'NA': 'https://advertising-api.amazon.com',
    'EU': 'https://advertising-api-eu.amazon.com',
    'FE': 'https://advertising-api-fe.amazon.com'
}

class BaseStream(base):
    KEY_PROPERTIES = ['id']
    profile_id = None
    country_code = None

    def set_profile(self, profile_id, country_code):
        self.profile_id = profile_id
        self.country_code = country_code
        self.client.set_profile_id(profile_id)

    def get_params(self):
        return {}

    def get_body(self):
        return {}

    def get_url(self, path):
        return '{}{}'.format(BASE_URL[self.config['region']], path)

    def transform_record(self, record, inject_profile=True):
        if inject_profile:
            if not self.profile_id:
                raise RuntimeError("Stream profile_id is None!")
            if not self.country_code:
                raise RuntimeError("Stream country_code is None!")
            record['profileId'] = self.profile_id
            record['countryCode'] = self.country_code
        transformed = base.transform_record(self, record)

        return transformed

    def sync_data(self):
        table = self.TABLE
        LOGGER.info('Syncing data for entity {}'.format(table))

        url = self.get_url(self.api_path)
        params = self.get_params()
        body = self.get_body()

        with singer.metrics.record_counter(endpoint=table) as counter:
            for profile in self.config.get('profiles'):
                LOGGER.info('Syncing data for profile with country code {}'.format(profile['country_code']))

                self.set_profile(profile['profile_id'], profile['country_code'])

                result = self.client.make_request(
                    url, self.API_METHOD, params=params, body=body)
                data = self.get_stream_data(result)

                for obj in data:
                    singer.write_records(
                        table,
                        [obj])

                    counter.increment()

        return self.state

class PaginatedStream(BaseStream):
    def get_params(self, index, count):
        return {
            "startIndex": index,
            "count": count
        }

    def sync_data(self):
        table = self.TABLE
        LOGGER.info('Syncing data for entity {}'.format(table))

        url = self.get_url(self.api_path)
        body = self.get_body()

        index = 0
        count = 5000
        with singer.metrics.record_counter(endpoint=table) as counter:
            for profile in self.config.get('profiles'):
                LOGGER.info('Syncing data for profile with country code {}'.format(profile['country_code']))

                self.set_profile(profile['profile_id'], profile['country_code'])

                while True:
                    LOGGER.info('Syncing {} rows from index {}'.format(count, index))

                    params = self.get_params(index, count)
                    result = self.client.make_request(
                        url, self.API_METHOD, params=params, body=body)

                    data = self.get_stream_data(result)
                    if len(data) == 0:
                        break
                    else:
                        index += count

                    for obj in data:
                        singer.write_records(
                            table,
                            [obj])

                        counter.increment()

        return self.state


class ReportStream(BaseStream):
    def create_report(self, url, day):
        body = self.get_body(day)

        # Create a report
        report = self.client.make_request(url, 'POST', body=body)
        report_id = report['reportId']

        # If we don't sleep here, then something funky happens and the API
        # takes _significantly_ longer to return a SUCCESS status
        time.sleep(10)
        LOGGER.info("Polling")
        report_url = '{}/v2/reports/{}'.format(BASE_URL[self.config['region']], report_id)

        num_polls = 7
        for i in range(num_polls):
            poll = self.client.make_request(report_url, 'GET')
            status = poll['status']
            LOGGER.info("Poll {} of {}, status={}".format(i+1, num_polls, status))

            if status == 'SUCCESS':
                return poll['location']
            else:
                timeout = (1 + i) ** 2
                LOGGER.info("In state: {}, Sleeping for {} seconds".format(status, timeout))
                time.sleep(timeout)

        LOGGER.info("Unable to sync from {} for day {}-- moving on".format(url, day))

    def sync_data(self):
        table = self.TABLE
        LOGGER.info('Syncing data for entity {}'.format(table))

        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        WINDOW_start = datetime.date.today() - datetime.timedelta(days=60)
        lookback = self.config.get('lookback', [1, 7, 14, 30])
        sync_dates = set()

        with singer.metrics.record_counter(endpoint=table) as counter:
            for profile in self.config.get('profiles'):
                sync_date = get_last_record_value_for_table(self.state, table, profile['country_code'])
                if sync_date is None:
                    sync_date = get_config_start_date(self.config)

                # Add a lookback to refresh attribution metrics for more recent orders
                # If the sync_date is over 60 days ago from today, use the date 60 days ago from today instead.
                if len(lookback) == 1:
                    sync_date = max(sync_date - datetime.timedelta(days=lookback), WINDOW_start)
                    end_date = self.config.get('end_date', min(yesterday, sync_date + datetime.timedelta(days=5)))
                    sync_date_copy = sync_date
                    while sync_date_copy <= end_date:
                        sync_dates.add(sync_date_copy)
                        sync_date_copy += datetime.timedelta(days=1)
                    sync_dates.add(WINDOW_start)
                else:
                    sync_dates = set([max(datetime.date.today() - datetime.timedelta(days=i), WINDOW_start) for i in lookback] + [WINDOW_start])


                LOGGER.info('Syncing data for profile with country code {}'.format(profile['country_code']))

                self.set_profile(profile['profile_id'], profile['country_code'])

                for sync_date_copy in sync_dates:
                    LOGGER.info("Syncing {} for date {}".format(table, sync_date_copy))

                    url = self.get_url(self.api_path)
                    report_url = self.create_report(url, sync_date_copy)

                    if report_url is not None:
                        result = self.client.download_gzip(report_url)
                        data = self.get_stream_data(result, sync_date_copy)

                        for obj in data:
                            singer.write_records(
                                table,
                                [obj])

                            counter.increment()

                        self.state = incorporate(self.state, self.TABLE,
                                                'last_record', sync_date_copy.isoformat(), profile['country_code'])
                        save_state(self.state)

                    else:
                        if sync_date_copy == max(sync_dates) and sync_date_copy < datetime.date.today() - datetime.timedelta(days=30):
                                self.state = incorporate(self.state, self.TABLE,
                                                'last_record', sync_date_copy.isoformat(), profile['country_code'])
                                save_state(self.state)

        return self.state
