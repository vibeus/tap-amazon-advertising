from tap_amazon_advertising.streams.base import ReportStream, BaseStream

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

from tap_framework.streams import BaseStream as base

LOGGER = singer.get_logger()  # noqa

# use BASE_URL[self.config['region']]
BASE_URL = {
    'NA': 'https://advertising-api.amazon.com',
    'EU': 'https://advertising-api-eu.amazon.com',
    'FE': 'https://advertising-api-fe.amazon.com'
}
class BaseSponsoredProductsReportV3Stream(BaseStream):
    API_METHOD = 'GET'

    @property
    def recordType(self):
        raise RuntimeError("not implemented")

    @property
    def api_path(self):
        return '/v2/sp/{}/report'.format(self.recordType)

    def get_body(self, day):
        return {
            "reportDate": day.strftime('%Y%m%d'),
            "metrics": ",".join([
                "campaignName",
                "campaignId",
                "adGroupName",
                "adGroupId",
                "impressions",
                "clicks",
                "cost",
                "currency",
                "asin",
                "sku",
                "attributedConversions1d",
                "attributedConversions7d",
                "attributedConversions14d",
                "attributedConversions30d",
                "attributedConversions1dSameSKU",
                "attributedConversions7dSameSKU",
                "attributedConversions14dSameSKU",
                "attributedConversions30dSameSKU",
                "attributedUnitsOrdered1d",
                "attributedUnitsOrdered7d",
                "attributedUnitsOrdered14d",
                "attributedUnitsOrdered30d",
                "attributedSales1d",
                "attributedSales7d",
                "attributedSales14d",
                "attributedSales30d",
                "attributedSales1dSameSKU",
                "attributedSales7dSameSKU",
                "attributedSales14dSameSKU",
                "attributedSales30dSameSKU",
            ])
        }

    def get_stream_data(self, result, day):
        for record in result:
            record['day'] = day.isoformat()

        return [
            self.transform_record(record)
            for record in result
        ]

# Advertised product report
class SponsoredProductsReportProductAdsStream(BaseSponsoredProductsReportV3Stream):
    TABLE = 'sponsored_products_report_product_ads'
    KEY_PROPERTIES = ['adId', 'day', 'profileId']

    @property
    def recordType(self):
        return "productAds"

    def get_body(self, day):
        return {
            "reportDate": day.strftime('%Y%m%d'),
            "metrics": ",".join([
                "campaignName",
                "campaignId",
                "adGroupName",
                "adGroupId",
                "impressions",
                "clicks",
                "cost",
                "currency",
                "asin",
                "sku", # Not supported for vendors?
                "attributedConversions1d",
                "attributedConversions7d",
                "attributedConversions14d",
                "attributedConversions30d",
                "attributedConversions1dSameSKU",
                "attributedConversions7dSameSKU",
                "attributedConversions14dSameSKU",
                "attributedConversions30dSameSKU",
                "attributedUnitsOrdered1d",
                "attributedUnitsOrdered7d",
                "attributedUnitsOrdered14d",
                "attributedUnitsOrdered30d",
                "attributedSales1d",
                "attributedSales7d",
                "attributedSales14d",
                "attributedSales30d",
                "attributedSales1dSameSKU",
                "attributedSales7dSameSKU",
                "attributedSales14dSameSKU",
                "attributedSales30dSameSKU",
            ])
        }

# Campaign report / Placement report
class SponsoredProductsReportCampaignsStream(BaseSponsoredProductsReportV3Stream):
    TABLE = 'sponsored_products_report_campaigns'
    KEY_PROPERTIES = ['campaignId', 'day', 'profileId', "placement"]

    @property
    def recordType(self):
        return "campaigns"

    def get_body(self, day):
        return {
            "reportDate": day.strftime('%Y%m%d'),
            "metrics": ",".join([
                "bidPlus",
                "campaignName",
                "campaignId",
                "campaignStatus",
                "campaignBudget",
                "impressions",
                "clicks",
                "cost",
                "portfolioId",
                "portfolioName",
                "attributedConversions1d",
                "attributedConversions7d",
                "attributedConversions14d",
                "attributedConversions30d",
                "attributedConversions1dSameSKU",
                "attributedConversions7dSameSKU",
                "attributedConversions14dSameSKU",
                "attributedConversions30dSameSKU",
                "attributedUnitsOrdered1d",
                "attributedUnitsOrdered7d",
                "attributedUnitsOrdered14d",
                "attributedUnitsOrdered30d",
                "attributedSales1d",
                "attributedSales7d",
                "attributedSales14d",
                "attributedSales30d",
                "attributedSales1dSameSKU",
                "attributedSales7dSameSKU",
                "attributedSales14dSameSKU",
                "attributedSales30dSameSKU",
            ]),
            "segment": "placement"
        }

# get performance data at the ad group level by creating an adGroups report
class SponsoredProductsReportAdGroupsStream(BaseSponsoredProductsReportV3Stream):
    TABLE = 'sponsored_products_report_ad_groups'
    KEY_PROPERTIES = ['adGroupId', 'day', 'profileId']

    @property
    def recordType(self):
        return "adGroups"

    def get_body(self, day):
        return {
            "reportDate": day.strftime('%Y%m%d'),
            "metrics": ",".join([
                "campaignName",
                "campaignId",
                "adGroupName",
                "adGroupId",
                "impressions",
                "clicks",
                "cost",
                "attributedConversions1d",
                "attributedConversions7d",
                "attributedConversions14d",
                "attributedConversions30d",
                "attributedConversions1dSameSKU",
                "attributedConversions7dSameSKU",
                "attributedConversions14dSameSKU",
                "attributedConversions30dSameSKU",
                "attributedUnitsOrdered1d",
                "attributedUnitsOrdered7d",
                "attributedUnitsOrdered14d",
                "attributedUnitsOrdered30d",
                "attributedSales1d",
                "attributedSales7d",
                "attributedSales14d",
                "attributedSales30d",
                "attributedSales1dSameSKU",
                "attributedSales7dSameSKU",
                "attributedSales14dSameSKU",
                "attributedSales30dSameSKU",
            ])
        }

# Search term report
class SponsoredProductsReportKeywordsStream(BaseSponsoredProductsReportV3Stream):
    TABLE = 'sponsored_products_report_keywords'
    KEY_PROPERTIES = ['keywordId', 'day', 'profileId', "query"]

    @property
    def recordType(self):
        return "keywords"

    def get_body(self, day):
        return {
            "reportDate": day.strftime('%Y%m%d'),
            "metrics": ",".join([
                "adGroupName",
                "adGroupId",
                "campaignName",
                "campaignId",
                "currency",
                "keywordId",
                "keywordText",
                "matchType",
                "impressions",
                "clicks",
                "cost",
                # "attributedConversions1d",
                # "attributedConversions7d",
                "attributedConversions14d",
                "attributedConversions30d",
                # "attributedConversions1dSameSKU",
                # "attributedConversions7dSameSKU",
                "attributedConversions14dSameSKU",
                "attributedConversions30dSameSKU",
                # "attributedUnitsOrdered1d",
                # "attributedUnitsOrdered7d",
                "attributedUnitsOrdered14d",
                "attributedUnitsOrdered30d",
                # "attributedSales1d",
                # "attributedSales7d",
                "attributedSales14d",
                "attributedSales30d",
                # "attributedSales1dSameSKU",
                # "attributedSales7dSameSKU",
                "attributedSales14dSameSKU",
                "attributedSales30dSameSKU",
            ]),
            "segment": "query"
        }

# Targeting report
class SponsoredProductsReportTargetingStream(BaseSponsoredProductsReportV3Stream):
    TABLE = 'sponsored_products_report_targeting'
    KEY_PROPERTIES = ['targetId', 'day', 'profileId', "query"]

    @property
    def recordType(self):
        return "targets"

    def get_body(self, day):
        return {
            "reportDate": day.strftime('%Y%m%d'),
            "metrics": ",".join([
                "adGroupId",
                "adGroupName",
                "campaignId",
                "campaignName",
                "campaignBudget",
                "campaignBudgetType",
                "campaignStatus",
                "clicks",
                "cost",
                "impressions",
                "targetingExpression",
                "targetingText",
                "targetingType",
                # "attributedConversions1d",
                # "attributedConversions7d",
                "attributedConversions14d",
                "attributedConversions30d",
                # "attributedConversions1dSameSKU",
                # "attributedConversions7dSameSKU",
                "attributedConversions14dSameSKU",
                "attributedConversions30dSameSKU",
                # "attributedUnitsOrdered1d",
                # "attributedUnitsOrdered7d",
                "attributedUnitsOrdered14d",
                "attributedUnitsOrdered30d",
                # "attributedSales1d",
                # "attributedSales7d",
                "attributedSales14d",
                "attributedSales30d",
                # "attributedSales1dSameSKU",
                # "attributedSales7dSameSKU",
                "attributedSales14dSameSKU",
                "attributedSales30dSameSKU",
            ]),
            "segment": "query"
        }

# Purchased product report:
# To get the full set of purchased products,
# send both request one with targetId and one with keywordId in the metric list.
class SponsoredProductsReportAsinsStream(BaseSponsoredProductsReportV3Stream):
    TABLE = 'sponsored_products_report_asins'
    KEY_PROPERTIES = ['campaignId', 'day', 'profileId']

    @property
    def recordType(self):
        return "asins"

    def get_body(self, day, limitied_metrics):
        return {
            "reportDate": day.strftime('%Y%m%d'),
            "metrics": ",".join(limitied_metrics + [
                "campaignId",
                "campaignName",
                "adGroupId",
                "adGroupName",
                "currency",
                "matchType",
                "sku",
                "asin",
                "otherAsin",
                # "attributedSales1dOtherSKU",
                # "attributedSales7dOtherSKU",
                "attributedSales14dOtherSKU",
                "attributedSales30dOtherSKU",
                # "attributedUnitsOrdered1d",
                # "attributedUnitsOrdered7d",
                "attributedUnitsOrdered14d",
                "attributedUnitsOrdered30d",
                # "attributedUnitsOrdered1dOtherSKU",
                # "attributedUnitsOrdered7dOtherSKU",
                "attributedUnitsOrdered14dOtherSKU",
                "attributedUnitsOrdered30dOtherSKU",
            ]),
            "campaignType": "sponsoredProducts"
        }

    def create_report(self, url, day, limitied_metrics):
        body = self.get_body(day, limitied_metrics)

        # Create a report
        report = self.client.make_request(url, 'POST', body=body)
        report_id = report['reportId']

        # If we don't sleep here, then something funky happens and the API
        # takes _significantly_ longer to return a SUCCESS status
        time.sleep(10)
        LOGGER.info("Polling")
        report_url = '{}/v2/reports/{}'.format(BASE_URL[self.config['region']], report_id)

        num_polls = 7 # extended from 7 to 10， in case the network is slow
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

        LOGGER.info("Unable to sync from {} by {} for day {}-- moving on".format(url, limitied_metrics[0], day))

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
                limitied_metrics = [
                    ["targetId", "targetingExpression", "targetingText", "targetingType"],
                    ["keywordId", "keywordText"]
                ]

                for sync_date_copy in sync_dates:
                    LOGGER.info("Syncing {} for date {}".format(table, sync_date_copy))

                    for limitied in limitied_metrics:
                        url = self.get_url(self.api_path)
                        report_url = self.create_report(url, sync_date_copy, limitied)

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

                    if sync_date_copy == end_date and end_date < datetime.date.today() - datetime.timedelta(days=30) :
                        self.state = incorporate(self.state, self.TABLE,
                                        'last_record', sync_date_copy.isoformat(), profile['country_code'])
                    save_state(self.state)

                    # sync_date_copy += datetime.timedelta(days=1)
                time.sleep(30)

        return self.state
