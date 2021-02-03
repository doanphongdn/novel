from math import ceil

from django.core.paginator import PageNotAnInteger, EmptyPage


class ModelPaginator:
    model = None

    def __init__(self, per_page, number, order_by='-id', **kwargs):
        self.per_page = per_page
        self.order_by = order_by
        self.count = self.model.objects.filter(**kwargs).count()
        self.number = self.validate_number(number)
        self.offset = per_page * (self.number - 1)
        self.data = self.get_data(**kwargs)

    def get_data(self, **kwargs):
        limit = self.offset + self.per_page
        return self.model.objects.filter(**kwargs).order_by(self.order_by).all()[self.offset:limit]

    def __repr__(self):
        return '<Page %s of %s>' % (self.number, self.num_pages)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        if not isinstance(index, (int, slice)):
            raise TypeError(
                'Page indices must be integers or slices, not %s.'
                % type(index).__name__
            )
        # The object_list is converted to a list so that if it was a QuerySet
        # it won't be a database hit per __getitem__.
        if not isinstance(self.data, list):
            self.data = list(self.data)
        return self.data[index]

    def validate_number(self, number):
        """Validate the given 1-based page number."""
        try:
            if isinstance(number, float) and not number.is_integer():
                raise ValueError
            number = int(number)
        except (TypeError, ValueError):
            raise PageNotAnInteger('That page number is not an integer')
        if number < 1:
            raise EmptyPage('That page number is less than 1')
        if number > self.num_pages:
            if number == 1:
                pass
            else:
                raise EmptyPage('That page contains no results')
        return number

    @property
    def num_pages(self):
        """Return the total number of pages."""
        if self.count == 0:
            return 0
        hits = max(1, self.count)
        return ceil(hits / self.per_page)

    def has_next(self):
        return self.number < self.num_pages

    def has_previous(self):
        return self.number > 1

    @property
    def page_range(self):
        """
        Return a 1-based range of pages for iterating through within
        a template for loop.
        """
        return range(1, self.num_pages + 1)
