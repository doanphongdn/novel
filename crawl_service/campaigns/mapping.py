from crawl_service.campaigns.novel import NovelCampaignType, NovelInfoCampaignType, NovelChapterCampaignType


class CampaignMapping(object):
    __campaign_list = [
        NovelCampaignType,
        NovelInfoCampaignType,
        NovelChapterCampaignType,
    ]
    type_mapping = {cam.type_name: cam for cam in __campaign_list}
    list_types = [(_type, _name.type_name) for _type, _name in type_mapping.items()]
