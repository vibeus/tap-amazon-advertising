from tap_amazon_advertising.streams.base import ReportStream

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

class BaseSponsoredDisplayReportStream(ReportStream):
    API_METHOD = 'POST'

    @property
    def recordType(self):
        raise RuntimeError("not implemented")

    @property
    def api_path(self):
        return '/sd/{}/report'.format(self.recordType)

    def get_body(self, day, tactic):
        return {
            "reportDate": day.strftime('%Y%m%d'),
            "tactic": tactic,
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
    
    def create_report(self, url, day, tactic):
        body = self.get_body(day, tactic)

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

        LOGGER.info("Unable to sync from {} with tactic {} for day {}-- moving on".format(url, tactic, day))

    def sync_data(self):
        table = self.TABLE
        LOGGER.info('Syncing data for entity {}'.format(table))

        tactics = ['T00020', 'T00030']

        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        WINDOW_start = datetime.date.today() - datetime.timedelta(days=60)

        with singer.metrics.record_counter(endpoint=table) as counter:
            for profile in self.config.get('profiles'):
                sync_date = get_last_record_value_for_table(self.state, table, profile['country_code'])
                if sync_date is None:
                    sync_date = get_config_start_date(self.config)

                # Add a lookback to refresh attribution metrics for more recent orders
                # If the sync_date is over 60 days ago from today, use the date 60 days ago from today instead.
                sync_date = max(sync_date - datetime.timedelta(days=self.config.get('lookback', 30)), WINDOW_start)
                end_date = self.config.get('end_date', min(yesterday, sync_date + datetime.timedelta(days=5)))

                if profile['country_code'] == "SG":
                    LOGGER.info('No sponsored display report avalible for marketplace SG -- moving on')
                    continue

                LOGGER.info('Syncing data for profile with country code {}'.format(profile['country_code']))

                self.set_profile(profile['profile_id'], profile['country_code'])

                sync_date_copy = sync_date
                while sync_date_copy <= end_date:
                    LOGGER.info("Syncing {} for date {}".format(table, sync_date_copy))

                    for tactic in tactics:
                        url = self.get_url(self.api_path)
                        report_url = self.create_report(url, sync_date_copy, tactic)

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
            
                    sync_date_copy += datetime.timedelta(days=1)
                
        return self.state    

# Advertised product report
class SponsoredDisplayReportProductAdsStream(BaseSponsoredDisplayReportStream):
    TABLE = 'sponsored_display_report_product_ads'
    KEY_PROPERTIES = ['adId', 'day', 'profileId']

    @property
    def recordType(self):
        return "productAds"

    def get_body(self, day, tactic):
        return {
            "reportDate": day.strftime('%Y%m%d'),
            "tactic": tactic,
            "metrics": ",".join([
                "campaignName",
                "campaignId",
                "adGroupName",
                "adGroupId",
                "adId",
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
                "attributedDetailPageView14d",
            ])
        }

# Campaign report
class SponsoredDisplayReportCampaignsStream(BaseSponsoredDisplayReportStream):
    TABLE = 'sponsored_display_report_campaigns'
    KEY_PROPERTIES = ['campaignId', 'day', 'profileId']

    @property
    def recordType(self):
        return "campaigns"

    def get_body(self, day, tactic):
        return {
            "reportDate": day.strftime('%Y%m%d'),
            "tactic": tactic,
            "metrics": ",".join([
                "campaignName",
                "campaignId",
                "campaignStatus",
                "campaignBudget",
                "impressions",
                "clicks",
                "cost",
                "costType",
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
                "attributedDetailPageView14d",
                "attributedUnitsOrderedNewToBrand14d", 
                "attributedOrdersNewToBrand14d", 
            ])
        }


class SponsoredDisplayReportAdGroupsStream(BaseSponsoredDisplayReportStream):
    TABLE = 'sponsored_display_report_ad_groups'
    KEY_PROPERTIES = ['adGroupId', 'day', 'profileId']

    @property
    def recordType(self):
        return "adGroups"

    def get_body(self, day, tactic):
        return {
            "reportDate": day.strftime('%Y%m%d'),
            "tactic": tactic,
            "metrics": ",".join([
                "campaignName",
                "campaignId",
                "adGroupName",
                "adGroupId",
                "impressions",
                "clicks",
                "cost",
                "bidOptimization",
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
                "attributedDetailPageView14d",
                "attributedUnitsOrderedNewToBrand14d", 
                "attributedOrdersNewToBrand14d", 
            ])
        }

# Targeting report
class SponsoredDisplayReportTargetingStream(BaseSponsoredDisplayReportStream):
    TABLE = 'sponsored_display_report_targeting'
    KEY_PROPERTIES = ['targetId', 'day', 'profileId']

    @property
    def recordType(self):
        return "targets"

    def get_body(self, day, tactic):
        return {
            "reportDate": day.strftime('%Y%m%d'),
            "tactic": tactic,
            "metrics": ",".join([
                "adGroupId", 
                "adGroupName", 
                "campaignId", 
                "campaignName", 
                "clicks", 
                "cost", 
                "currency", 
                "impressions", 
                "targetId",
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
                # "attributedSales1d", 
                # "attributedSales7d", 
                "attributedSales14d", 
                "attributedSales30d", 
                # "attributedSales1dSameSKU", 
                # "attributedSales7dSameSKU", 
                "attributedSales14dSameSKU", 
                "attributedSales30dSameSKU", 
                # "attributedUnitsOrdered1d", 
                # "attributedUnitsOrdered7d", 
                "attributedUnitsOrdered14d", 
                "attributedUnitsOrdered30d", 
                "attributedDetailPageView14d", 
                "attributedSalesNewToBrand14d", 
                "attributedOrdersNewToBrand14d", 
                "attributedUnitsOrderedNewToBrand14d", 
            ])
        }

# Purchased product report
class SponsoredDisplayReportAsinsStream(BaseSponsoredDisplayReportStream):
    TABLE = 'sponsored_display_report_asins'
    KEY_PROPERTIES = ['campaignId', 'day', 'profileId']

    @property
    def recordType(self):
        return "asins"

    def get_body(self, day, tactic):
        return {
            "reportDate": day.strftime('%Y%m%d'),
            "tactic": tactic,
            "metrics": ",".join([
                "campaignId", 
                "campaignName", 
                "adGroupId", 
                "adGroupName", 
                "currency", 
                "asin", 
                "otherAsin", 
                "sku", 
                "attributedSales14dOtherSKU", 
                # "attributedSales1dOtherSKU", 
                "attributedSales30dOtherSKU", 
                # "attributedSales7dOtherSKU", 
                "attributedUnitsOrdered14dOtherSKU", 
                # "attributedUnitsOrdered1dOtherSKU", 
                "attributedUnitsOrdered30dOtherSKU", 
                # "attributedUnitsOrdered7dOtherSKU", 
            ])
        }
