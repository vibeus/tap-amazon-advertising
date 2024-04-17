from tap_amazon_advertising.streams.base import BaseStream

# import singer
import json

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

from dateutil.parser import parse

# from tap_framework.streams import BaseStream as base


LOGGER = singer.get_logger()  # noqa

# use BASE_URL[self.config['region']]
BASE_URL = {
    'NA': 'https://advertising-api.amazon.com',
    'EU': 'https://advertising-api-eu.amazon.com',
    'FE': 'https://advertising-api-fe.amazon.com'
}

class BaseAttributionReportStream(BaseStream):
    API_METHOD = 'POST'

    @property
    def recordType(self):
        raise RuntimeError("not implemented")

    @property
    def api_path(self):
        return '/attribution/report'

    def get_body(self, day):
        return {
            "reportType": "PERFORMANCE",
            "endDate": "20220920",
            "count": 1000,
            "startDate": "20220901",
            "groupBy":"CAMPAIGN",
            "metrics":"Click-throughs",
            "advertiserIds": "592479597184783006"
        }


    def get_stream_data(self, result):
        for record in result:
            record['date'] = parse(record['date']).isoformat()

        return [
            self.transform_record(record)
            for record in result
        ]

    def sync_data(self):
        table = self.TABLE
        LOGGER.info('Syncing data for entity {}'.format(table))

        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        WINDOW_start = datetime.date.today() - datetime.timedelta(days=365)

        with singer.metrics.record_counter(endpoint=table) as counter:
            for profile in self.config.get('profiles'):
                state_date = get_last_record_value_for_table(self.state, table, profile['country_code'])
                if state_date is None:
                    state_date = get_config_start_date(self.config)

                # Add a lookback to refresh attribution metrics for more recent orders
                # If the sync_date is over 60 days ago from today, use the date 60 days ago from today instead.
                start_date = max(state_date - datetime.timedelta(days=self.config.get('lookback_v3', 30)), WINDOW_start)
                end_date = self.config.get('end_date', min(yesterday, start_date + datetime.timedelta(days=60)))

                if profile['country_code'] == "AU":
                    LOGGER.info('No sponsored display report avalible for marketplace AU -- moving on')
                    continue

                LOGGER.info('Syncing data for profile with country code {}'.format(profile['country_code']))

                self.set_profile(profile['profile_id'], profile['country_code'])

                LOGGER.info("Syncing {} for date {} to {}".format(table, start_date, yesterday))
                url = self.get_url(self.api_path)
                body = self.get_body(start_date, yesterday)
                reports = self.client.make_request(url, 'POST', body=body)

                data = self.get_stream_data(reports["reports"])

                for obj in data:
                    singer.write_records(
                        table,
                        [obj])

                    counter.increment()

                self.state = incorporate(self.state, self.TABLE,
                                        'last_record', yesterday.isoformat(), profile['country_code'])
                save_state(self.state)

        return self.state


# Campaign Performance
class AttributionReportCampaignPerformanceStream(BaseAttributionReportStream):
    TABLE = 'attribution_report_campaign_performance'
    KEY_PROPERTIES = ['date', 'campaignId', 'profileId']

    @property
    def recordType(self):
        return "PERFORMANCE"

    def get_body(self, start, end):
        return {
            "reportType": self.recordType,
            "endDate": end.strftime('%Y%m%d'),
            "count": 1000,
            "startDate": start.strftime('%Y%m%d'),
            "groupBy": "CAMPAIGN",
            "metrics": ",".join([
                "Click-throughs",
                "attributedDetailPageViewsClicks14d",
                "attributedAddToCartClicks14d",
                "attributedPurchases14d",
                "unitsSold14d",
                "attributedSales14d",
                "attributedTotalDetailPageViewsClicks14d",
                "attributedTotalAddToCartClicks14d",
                "attributedTotalPurchases14d",
                "totalUnitsSold14d",
                "totalAttributedSales14d",
                "brb_bonus_amount",
            ])
        }
