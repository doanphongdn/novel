class BaseCrawlCampaignType(object):
    type_name = "base"
    model_class = None
    update_by_fields = []

    def __init__(self, crawled_data):
        self.crawled_data = crawled_data
        self.update_values = {}
        if self.update_by_fields:
            self.update_values = {f: {} for f in self.update_by_fields}
            objects = self.model_class.objects.all()
            for obj in objects:
                for key, value in self.update_values.items():
                    val = getattr(obj, key, None)
                    if val:
                        value[val] = obj
