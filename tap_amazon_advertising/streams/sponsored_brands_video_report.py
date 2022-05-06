from tap_amazon_advertising.streams.sponsored_brands_report import BaseSponsoredBrandsReportStream

# Keyword report
class SponsoredBrandsVideoReportKeywordsStream(BaseSponsoredBrandsReportStream):
    TABLE = 'sponsored_brands_video_report_keywords'
    KEY_PROPERTIES = ['keywordId', 'day', 'profileId']

    def get_body(self, day):
        return {
            "reportDate": day.strftime('%Y%m%d'),
            "metrics": ",".join([
              "campaignId", 
              "campaignName", 
              "campaignStatus", 
              "campaignBudget", 
              "campaignBudgetType", 
              "adGroupId", 
              "adGroupName", 
              "clicks", 
              "cost", 
              "impressions", 
              "keywordStatus",
              "keywordText", 
              "matchType", 
              "vtr",
              "vctr", 
              "video5SecondViewRate", 
              "video5SecondViews", 
              "videoCompleteViews", 
              "videoFirstQuartileViews",
              "videoMidpointViews", 
              "videoThirdQuartileViews", 
              "videoUnmutes", 
              "viewableImpressions", 
              "attributedConversions14d", 
              "attributedConversions14dSameSKU", 
              "attributedSales14d", 
              "attributedSales14dSameSKU", 
              "attributedDetailPageViewsClicks14d",
            ]),
            "creativeType": "video"
        }


    @property
    def recordType(self):
        return "keywords"

# Search term report
class SponsoredBrandsVideoReportSearchTermStream(BaseSponsoredBrandsReportStream):
    TABLE = 'sponsored_brands_video_report_search_term'
    KEY_PROPERTIES = ['keywordId', 'day', 'profileId']

    def get_body(self, day):
        return {
            "reportDate": day.strftime('%Y%m%d'),
            "metrics": ",".join([
              "campaignBudget", 
              "campaignBudgetType", 
              "campaignStatus", 
              "adGroupId", 
              "adGroupName", 
              "impressions",
              "clicks", 
              "cost", 
              "keywordStatus", 
              "keywordText", 
              "matchType", 
              "vtr",
              "vctr", 
              "video5SecondViewRate", 
              "video5SecondViews", 
              "videoCompleteViews", 
              "videoFirstQuartileViews", 
              "videoMidpointViews", 
              "videoThirdQuartileViews", 
              "videoUnmutes", 
              "viewableImpressions",
              "attributedConversions14d", 
              "attributedSales14d",
            ]),
            "segment": "query",
            "creativeType": "video"
        }


    @property
    def recordType(self):
        return "keywords"

# Campaign report / Campaign placement report
class SponsoredBrandsVideoReportCampaignsStream(BaseSponsoredBrandsReportStream):
    TABLE = 'sponsored_brands_video_report_campaigns'
    KEY_PROPERTIES = ['campaignId', 'day', 'profileId']

    def get_body(self, day):
        return {
            "reportDate": day.strftime('%Y%m%d'),
            "metrics": ",".join([
              "campaignName", 
              "campaignStatus", 
              "campaignBudget", 
              "campaignBudgetType", 
              "impressions", 
              "clicks", 
              "cost", 
              "vtr",
              "vctr", 
              "video5SecondViewRate", 
              "video5SecondViews", 
              "videoCompleteViews", 
              "videoFirstQuartileViews", 
              "videoMidpointViews", 
              "videoThirdQuartileViews", 
              "videoUnmutes", 
              "viewableImpressions", 
              "attributedConversions14d", 
              "attributedConversions14dSameSKU", 
              "attributedSales14d", 
              "attributedSales14dSameSKU",
              "attributedDetailPageViewsClicks14d", 
            ]),
            "segment": "placement",
            "creativeType": "video"
        }

    @property
    def recordType(self):
        return "campaigns"
