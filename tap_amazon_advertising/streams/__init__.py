
from tap_amazon_advertising.streams.portfolios import PortfoliosStream
from tap_amazon_advertising.streams.sponsored_display_campaigns import SponsoredDisplayCampaignsStream
from tap_amazon_advertising.streams.sponsored_products_campaigns import SponsoredProductsCampaignsStream
from tap_amazon_advertising.streams.sponsored_brands_campaigns import SponsoredBrandsCampaignsStream
from tap_amazon_advertising.streams.ad_groups import AdGroupsStream
from tap_amazon_advertising.streams.biddable_keywords import BiddableKeywordsStream
from tap_amazon_advertising.streams.negative_keywords import NegativeKeywordsStream
from tap_amazon_advertising.streams.campaign_negative_keywords import CampaignNegativeKeywordsStream
from tap_amazon_advertising.streams.product_ads import ProductAdsStream

from tap_amazon_advertising.streams.sponsored_display_report import SponsoredDisplayReportProductAdsStream, \
        SponsoredDisplayReportCampaignsStream, \
        SponsoredDisplayReportAdGroupsStream, \
        SponsoredDisplayReportTargetingStream, \
        SponsoredDisplayReportAsinsStream

from tap_amazon_advertising.streams.sponsored_products_report import SponsoredProductsReportProductAdsStream, \
        SponsoredProductsReportCampaignsStream, \
        SponsoredProductsReportAdGroupsStream, \
        SponsoredProductsReportKeywordsStream, \
        SponsoredProductsReportTargetingStream, \
        SponsoredProductsReportAsinsStream

from tap_amazon_advertising.streams.sponsored_brands_report import SponsoredBrandsReportKeywordsStream, \
        SponsoredBrandsReportCampaignsStream, \
        SponsoredBrandsReportAdGroupsStream, \
        SponsoredBrandsReportSearchTermStream

from tap_amazon_advertising.streams.sponsored_brands_video_report import SponsoredBrandsVideoReportKeywordsStream, \
        SponsoredBrandsVideoReportSearchTermStream, \
        SponsoredBrandsVideoReportCampaignsStream

from tap_amazon_advertising.streams.attribution_report import AttributionReportCampaignPerformanceStream


AVAILABLE_STREAMS = [
    AttributionReportCampaignPerformanceStream,
    PortfoliosStream,
    SponsoredDisplayCampaignsStream,
    SponsoredProductsCampaignsStream,
    SponsoredBrandsCampaignsStream,
    AdGroupsStream,
    BiddableKeywordsStream,
    NegativeKeywordsStream,
    CampaignNegativeKeywordsStream,
    ProductAdsStream,

    # SB Video Reports
    SponsoredBrandsVideoReportKeywordsStream,
    SponsoredBrandsVideoReportSearchTermStream,
    SponsoredBrandsVideoReportCampaignsStream,

    # SD Reports (PART 1)
    SponsoredDisplayReportProductAdsStream,
    SponsoredDisplayReportCampaignsStream,
    SponsoredDisplayReportAdGroupsStream,

    # SP Reports (PART 1)
    SponsoredProductsReportProductAdsStream,
    SponsoredProductsReportCampaignsStream,
    SponsoredProductsReportAdGroupsStream,

    # SB Reports
    SponsoredBrandsReportKeywordsStream,
    SponsoredBrandsReportCampaignsStream,
    SponsoredBrandsReportAdGroupsStream,
    SponsoredBrandsReportSearchTermStream,

    # SD Reports (PART 2)
    SponsoredDisplayReportTargetingStream,
    SponsoredDisplayReportAsinsStream,

    # SP Reports (PART 2)
    SponsoredProductsReportKeywordsStream,
    SponsoredProductsReportTargetingStream,
    SponsoredProductsReportAsinsStream
]

__all__ = [
    'AttributionReportCampaignPerformanceStream'
    'PortfoliosStream',
    'SponsoredProductsCampaignsStream',
    'SponsoredBrandsCampaignsStream',
    'AdGroupsStream',
    'BiddableKeywordsStream',
    'NegativeKeywordsStream',
    'CampaignNegativeKeywordsStream',
    'ProductAdsStream',

    'SponsoredDisplayReportProductAdsStream',
    'SponsoredDisplayReportCampaignsStream',
    'SponsoredDisplayReportAdGroupsStream',
    'SponsoredDisplayReportTargetingStream',
    'SponsoredDisplayReportAsinsStream', 

    'SponsoredProductsReportProductAdsStream',
    'SponsoredProductsReportCampaignsStream',
    'SponsoredProductsReportAdGroupsStream',
    'SponsoredProductsReportKeywordsStream',
    'SponsoredProductsReportTargetingStream',
    'SponsoredProductsReportAsinsStream',

    'SponsoredBrandsReportKeywordsStream',
    'SponsoredBrandsReportCampaignsStream',
    'SponsoredBrandsReportAdGroupsStream',
    'SponsoredBrandsReportSearchTermStream',

    'SponsoredBrandsVideoReportKeywordsStream',
    'SponsoredBrandsVideoReportSearchTermStream',
    'SponsoredBrandsVideoReportCampaignsStream'
]
