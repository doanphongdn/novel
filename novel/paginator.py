from cms.paginator import ModelPaginator
from novel.models import NovelChapter, Novel


class ChapterPaginator(ModelPaginator):
    model = NovelChapter


class NovelPaginator(ModelPaginator):
    model = Novel

    def get_data(self, **kwargs):
        return self.model.get_available_novel().filter(**kwargs).prefetch_related("novel_flat") \
                   .order_by(self.order_by).all()[self.offset:self.offset + self.per_page]
