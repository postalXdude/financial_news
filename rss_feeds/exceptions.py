from rest_framework.exceptions import APIException


class YahooRSSFeedError(APIException):
    default_detail = 'Error while fetching Yahoo feeds.'
    default_code = 'yahoo_rss_feed_error'
