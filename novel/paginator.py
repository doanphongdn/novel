from cms.paginator import ModelPaginator
from novel.models import Novel


class ChapterPaginator(ModelPaginator):
    def __init__(self, novel, per_page, number, order_by='-id', **kwargs):
        self.novel_flat = novel.novel_flat
        super().__init__(per_page, number, order_by, **kwargs)

    def calc_total(self, **kwargs):
        return self.novel_flat.chapters.get("total", 0)

    def get_data(self, **kwargs):
        return self.novel_flat.chapters.get("list", [])[self.offset:self.offset + self.per_page]


class NovelPaginator(ModelPaginator):
    model = Novel

    def calc_total(self, **kwargs):
        return self.model.get_available_novel().filter(**kwargs).count()

    def get_data(self, **kwargs):
        return self.model.get_available_novel().filter(**kwargs).prefetch_related("novel_flat") \
                   .order_by(self.order_by).all()[self.offset:self.offset + self.per_page]
