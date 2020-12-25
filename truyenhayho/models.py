import zlib

from autoslug import AutoSlugField
from autoslug.utils import slugify
from django.db import models
from unidecode import unidecode


def unicode_slugify(name):
    return slugify(unidecode(name).replace(".", "-")).strip("-")


class Status(models.Model):
    class Meta:
        db_table = 'novel_status'

    name = models.CharField(max_length=250, unique=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Author(models.Model):
    class Meta:
        db_table = 'novel_authors'

    name = models.CharField(max_length=250, unique=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Genre(models.Model):
    class Meta:
        db_table = 'novel_genres'

    name = models.CharField(max_length=250, unique=True)
    slug = AutoSlugField(populate_from='name', slugify=unicode_slugify,
                         max_length=250, blank=True, unique=True, null=True)
    active = models.BooleanField(default=True)

    def novel_count(self):
        return Novel.get_available_novel().filter(categories=self).count()

    def get_absolute_url(self):
        return f"/genre/{self.slug}"


class Novel(models.Model):
    class Meta:
        db_table = "novel_novels"

    name = models.CharField(max_length=250, db_index=True, unique=True)
    slug = AutoSlugField(populate_from='name', slugify=unicode_slugify, db_index=True,
                         max_length=250, blank=True, unique=True, null=True)
    url = models.TextField()
    thumbnail_image = models.CharField(max_length=250, blank=True, null=True)

    status = models.ForeignKey(Status, on_delete=models.CASCADE, blank=True, null=True)
    authors = models.ManyToManyField(Author, db_table="novel_novel_authors_rel", blank=True)
    genres = models.ManyToManyField(Genre, db_table="novel_novel_genres_rel", blank=True)
    descriptions = models.TextField(blank=True, null=True)

    chapter_updated = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    follow = models.IntegerField(default=0)
    vote = models.FloatField(default=5)
    vote_total = models.IntegerField(default=1)
    view_daily = models.IntegerField(default=0)
    view_monthly = models.IntegerField(default=0)
    view_total = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    @property
    def authors_name(self):
        return ", ".join([str(p.name) for p in self.authors.all()])

    @property
    def genres_name(self):
        return ", ".join([str(p.name) for p in self.genres.all()])

    @classmethod
    def get_available_novel(cls):
        return cls.objects.filter(active=True)

    @property
    def chapters(self):
        return NovelChapter.objects.filter(novel=self)


class NovelChapter(models.Model):
    class Meta:
        db_table = "novel_chapters"
        unique_together = [('url', 'novel'), ('slug', 'novel')]
        ordering = ['-id']

    name = models.CharField(max_length=250, db_index=True)
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE)
    url = models.TextField()
    slug = AutoSlugField(populate_from='name', slugify=unicode_slugify, max_length=250, blank=True, null=True,
                         db_index=True)

    view_total = models.IntegerField(default=0, null=True)

    content_updated = models.BooleanField(default=False)
    binary_content = models.BinaryField()
    # Datetime
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

