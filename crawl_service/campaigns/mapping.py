from crawl_service.campaigns.action import ReverseAction, FormatChapterContent, GroupItem, JoinItem
from crawl_service.campaigns.novel import NovelCampaignType, NovelInfoCampaignType, NovelChapterCampaignType


class BaseMapping(object):
    __campaign_list = []
    mapping = {cam.__name__: cam for cam in __campaign_list}


class CampaignMapping(BaseMapping):
    __campaign_list = [
        NovelCampaignType,
        NovelInfoCampaignType,
        NovelChapterCampaignType,
    ]


class ActionMapping(BaseMapping):
    __campaign_list = [
        ReverseAction,
        FormatChapterContent,
        GroupItem,
        JoinItem,
    ]
