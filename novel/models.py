import hashlib
import zlib
from datetime import datetime

from autoslug import AutoSlugField
from autoslug.utils import slugify
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.safestring import mark_safe
from unidecode import unidecode

from crawl_service import settings
from crawl_service.models import CrawlCampaignSource


def datetime2string(value):
    """ Convert updated_at to friendly string
    :return: string - ex: 1 hour ago, 1 month ago, phút
    """
    diff_timestamp = datetime.timestamp(datetime.now()) - datetime.timestamp(value)

    if diff_timestamp / 60 < 60:
        updated_at = "%s minute(s) ago" % (int(diff_timestamp / 60) + 1)
    elif diff_timestamp / 3600 < 24:
        updated_at = "%s hour(s) ago" % int(diff_timestamp / 3600)
    elif diff_timestamp / 3600 / 24 < 30:
        updated_at = "%s day(s) ago" % int(diff_timestamp / 3600 / 24)
    else:
        updated_at = value.strftime("%Y/%m/%d")

    return updated_at


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
        ordering = ["name"]

    name = models.CharField(max_length=250, unique=True)
    slug = AutoSlugField(populate_from='name', slugify=unicode_slugify,
                         max_length=250, blank=True, unique=True, null=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def novel_count(self):
        return Novel.get_available_novel().filter(categories=self).count()

    def get_absolute_url(self):
        return f"/{settings.NOVEL_GENRE_URL}/{self.slug}"

    @classmethod
    def get_available_genre(cls):
        return cls.objects.filter(active=True)


class Novel(models.Model):
    class Meta:
        db_table = "novel_novels"
        ordering = ['id']

    name = models.CharField(max_length=250, db_index=True, unique=True)
    slug = AutoSlugField(populate_from='name', slugify=unicode_slugify, db_index=True,
                         max_length=250, blank=True, unique=True, null=True)
    url = models.TextField(unique=True)
    thumbnail_image = models.TextField(blank=True, null=True)
    descriptions = models.TextField(blank=True, null=True)

    genres = models.ManyToManyField(Genre, db_table="novel_novel_genres_rel", blank=True)
    authors = models.ManyToManyField(Author, db_table="novel_novel_authors_rel", blank=True)

    status = models.ForeignKey(Status, on_delete=models.CASCADE, blank=True, null=True)
    novel_updated = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    publish = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    follow = models.IntegerField(default=0)
    vote = models.FloatField(default=5)
    vote_total = models.IntegerField(default=1)
    view_daily = models.IntegerField(default=0)
    view_monthly = models.IntegerField(default=0)
    view_total = models.IntegerField(default=0)

    latest_chapter_url = models.CharField(max_length=250, blank=True, null=True)
    latest_updated_time = models.DateTimeField(auto_now_add=True)

    attempt = models.SmallIntegerField(default=0)
    campaign_source = models.ForeignKey(CrawlCampaignSource, on_delete=models.CASCADE)

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
        deactive_ids = cls.objects.filter(genres__active=False).values_list('id', flat=True).distinct()
        available_novels = cls.objects.filter(~Q(id__in=deactive_ids),
                                              active=True, publish=True).distinct()

        return available_novels

    @property
    def chapters(self):
        return NovelChapter.objects.filter(novel=self, chapter_updated=True, active=True)

    @property
    def novel_first_chapter_url(self):
        first_chap_url = None
        chapter = self.chapters.last()
        if chapter:
            first_chap_url = chapter.get_absolute_url()

        return first_chap_url

    @property
    def novel_latest_chapter_url(self):
        last_chapter_url = None
        chapter = self.chapters.first()
        if chapter:
            last_chapter_url = chapter.get_absolute_url()

        return last_chapter_url

    def get_absolute_url(self):
        return reverse("novel", args=[self.slug])

    @property
    def rating_classes(self):
        vote = int(round(self.vote)) or 5
        classes = []
        classes.extend(['rating_current'] * vote)
        classes.extend(['rating_none'] * (5 - vote))

        return classes

    @property
    def latest_updated_at_str(self):
        return datetime2string(self.latest_updated_time)

    @property
    def stream_thumbnail_image(self):
        return "/thumbnail_images/%s_%s.jpg" % (self.id, hashlib.md5(self.thumbnail_image.encode()).hexdigest())


class NovelChapter(models.Model):
    class Meta:
        db_table = "novel_chapters"
        unique_together = [('name', 'novel'), ('slug', 'novel'), ('url', 'novel')]
        ordering = ['-id']

    novel = models.ForeignKey(Novel, on_delete=models.CASCADE)
    name = models.CharField(max_length=250, db_index=True)
    url = models.TextField()
    slug = AutoSlugField(populate_from='name', slugify=unicode_slugify, max_length=250, blank=True, null=True,
                         db_index=True)

    view_total = models.IntegerField(default=0, null=True)

    chapter_updated = models.BooleanField(default=False)
    binary_content = models.BinaryField(blank=True, null=True)
    images_content = models.TextField(blank=True, null=True)

    # Datetime
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    active = models.BooleanField(default=True)
    attempt = models.SmallIntegerField(default=0)

    def __str__(self):
        return self.name

    @classmethod
    def get_available_chapter(cls):
        return cls.objects.filter(active=True, chapter_updated=True)

    @property
    def images(self):
        images = []
        if self.images_content:
            images = self.images_content.split('\n')
        return images

    @property
    def stream_images(self):
        novel_setting = NovelSetting.get_setting()
        img_ignoring = []
        if novel_setting and novel_setting.img_ignoring:
            img_ignoring = novel_setting.img_ignoring.split(",")
        images = self.images
        stream_images = []
        for i in range(len(images)):
            # Not allow img url contains any sub-string from a list configuration's string
            if len(img_ignoring) and any(sub_str in images[i] for sub_str in img_ignoring):
                continue
            stream_images.append("/images/%s_%s_%s.jpg" % (self.id, i, hashlib.md5(images[i].encode()).hexdigest()))
        return stream_images

    @property
    def created_at_str(self):
        return datetime2string(self.created_at)

    @property
    def next_chapter(self):
        next_chap = NovelChapter.objects.filter(novel_id=self.novel_id, pk__gt=self.id).last()
        return next_chap

    @property
    def prev_chapter(self):
        prev_chap = NovelChapter.objects.filter(novel_id=self.novel_id, pk__lt=self.id).first()
        return prev_chap

    @property
    def decompress_content(self):
        if self.binary_content and len(self.binary_content) > 0:
            decompresed = zlib.decompress(self.binary_content).decode()
            return decompresed

        return None

    def get_absolute_url(self):
        return reverse("chapter", args=[self.novel.slug, self.slug])


class NovelSetting(models.Model):
    class Meta:
        db_table = "novel_settings"

    title = models.CharField(max_length=250)
    favicon = models.ImageField(upload_to="images", null=True, blank=True)
    logo = models.ImageField(upload_to="images", null=True, blank=True)
    meta_keywords = models.TextField(null=True, blank=True)
    meta_description = models.TextField(null=True, blank=True)
    meta_copyright = models.TextField(null=True, blank=True)
    meta_author = models.TextField(null=True, blank=True)
    # facebook
    meta_og_type = models.CharField(max_length=250, null=True, blank=True)
    meta_img = models.ImageField(upload_to="images", null=True, blank=True)
    meta_og_description = models.TextField(null=True, blank=True)
    meta_fb_app_id = models.CharField(max_length=250, blank=True)
    # others
    img_ignoring = models.TextField(null=True, blank=True)
    google_analystics_id = models.TextField(null=True, blank=True)
    novel_type = models.CharField(max_length=250, choices=[('COMIC', 'Comic'), ('TEXT', 'Text')])

    def logo_tag(self):
        return mark_safe('<img src="%s" width="300"/>' % self.logo.url)

    def favicon_tag(self):
        return mark_safe('<img src="%s" width="100" height="100"/>' % self.favicon.url)

    def meta_img_tag(self):
        return mark_safe('<img src="%s" width="250" height="250"/>' % self.meta_img.url)

    logo_tag.short_description = 'logo'
    favicon_tag.short_description = 'favicon'
    meta_img_tag.short_description = 'novel'

    @classmethod
    def get_setting(cls):
        return cls.objects.first()
