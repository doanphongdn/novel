from crawl_service.campaigns.action import ReverseAction, FormatChapterContent, GroupItem, JoinItem
from crawl_service.campaigns.novel import NovelCampaignType, NovelInfoCampaignType, NovelChapterCampaignType


class BaseMapping(object):
    __campaign_list = []


class CampaignMapping(BaseMapping):
    __campaign_list = [
        NovelCampaignType,
        NovelInfoCampaignType,
        NovelChapterCampaignType,
    ]
    type_mapping = {cam.name: cam for cam in __campaign_list}
    list_types = [(_type, _name.name) for _type, _name in type_mapping.items()]


class ActionMapping(BaseMapping):
    __campaign_list = [
        ReverseAction,
        FormatChapterContent,
        GroupItem,
        JoinItem,
    ]
    action_mapping = {cam.name: cam for cam in __campaign_list}
    list_types = [(_type, _name.name) for _type, _name in action_mapping.items()]
