from django_cms.utils.paginator import ModelPaginator
from novel.models import Novel, Comment


class ChapterPaginator(ModelPaginator):
    def __init__(self, novel, per_page, number, order_by='-id', **kwargs):
        self.novel_flat = novel.novel_flat
        super().__init__(per_page, number, order_by, **kwargs)

    def calc_total(self, **kwargs):
        if not self.novel_flat:
            return 0

        return self.novel_flat.chapters.get("total", 0)

    def get_data(self, **kwargs):
        if not self.novel_flat:
            return []
        chap_list = self.novel_flat.chapters.get("list", [])
        chap_list.reverse()
        return chap_list[self.offset:self.offset + self.per_page]


class CommentPaginator(ModelPaginator):
    def __init__(self, novel, per_page, number, order_by='-id', **kwargs):
        self.novel = novel
        super().__init__(per_page, number, order_by, **kwargs)

    def calc_total(self, **kwargs):
        if not self.novel:
            return 0

        return Comment.objects.filter(novel=self.novel).count()

    def get_data(self, **kwargs):
        if not self.novel:
            return []
        comment_data = []
        comment_list = Comment.objects.filter(novel=self.novel, **kwargs).prefetch_related('chapter', 'user').order_by(
            self.order_by).all()[self.offset:self.offset + self.per_page]
        for cmt in comment_list:
            child_comments = Comment.objects.filter(parent_id=cmt.id)
            comment_data.append(cmt)
            comment_data.extend(list(child_comments))
        return comment_data


class NovelPaginator(ModelPaginator):
    model = Novel

    def calc_total(self, **kwargs):
        return len(self.custom_data) or self.model.get_available_novel().filter(**kwargs).count()

    def get_data(self, **kwargs):
        return self.custom_data[self.offset:self.offset + self.per_page] or self.model.get_available_novel().filter(
            **kwargs).prefetch_related("novel_flat").order_by(self.order_by).all()[
                                                                            self.offset:self.offset + self.per_page]
