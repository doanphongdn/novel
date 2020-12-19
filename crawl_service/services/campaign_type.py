class BaseCrawlCampaignType(object):
    type_name = "base"
    model_class = None
    required_fields = ()
    optional_fields = ()

    def __init__(self, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)

    def handle(self):
        pass


class CrawlCampaignType(object):
    type_mapping = {}
    list_types = [(_type, _name.type_name) for _type, _name in type_mapping.items()]
