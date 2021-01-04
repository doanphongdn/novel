from crawl_service.campaigns.base import BaseAction


class ReverseAction(BaseAction):
    name = 'Reverse'

    @classmethod
    def handle(cls, obj):
        super().handle(obj)

        if isinstance(obj, list):
            obj.reverse()

        return obj
