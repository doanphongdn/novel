from crawl_service.campaigns.action import ReverseAction, FormatChapterContent, GroupItem, JoinItem, ReplaceString
from crawl_service.campaigns.novel import NovelCampaignType, NovelInfoCampaignType, NovelChapterCampaignType


class BaseMapping(object):
    _campaign_list = []

    @classmethod
    def get_mapping(cls, name):
        mapping = {cam.__name__: cam for cam in cls._campaign_list}
        return mapping.get(name)


class CampaignMapping(BaseMapping):
    _campaign_list = [
        NovelCampaignType,
        NovelInfoCampaignType,
        NovelChapterCampaignType,
    ]


class ActionMapping(BaseMapping):
    _campaign_list = [
        ReverseAction,
        FormatChapterContent,
        GroupItem,
        JoinItem,
        ReplaceString,
    ]
