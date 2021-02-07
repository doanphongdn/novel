import hashlib
import json
import zlib
from datetime import datetime, timedelta
from urllib.parse import urlparse

from autoslug import AutoSlugField
from autoslug.utils import slugify
from django.contrib.sites.models import Site
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from unidecode import unidecode

from crawl_service import settings
from crawl_service.models import CDNServer, CrawlCampaignSource


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

    def get_absolute_url(self):
        return f"/{settings.NOVEL_GENRE_URL}/{self.slug}"


def default_novel_flat():
    return {}


class NovelFlat(models.Model):
    class Meta:
        db_table = "novel_novels_flat"

    latest_chapter = models.JSONField(null=True, blank=True, default=default_novel_flat)
    first_chapter = models.JSONField(null=True, blank=True, default=default_novel_flat)
    chapters = models.JSONField(null=True, blank=True, default=default_novel_flat)


class Novel(models.Model):
    class Meta:
        db_table = "novel_novels"

    novel_flat = models.ForeignKey(NovelFlat, on_delete=models.CASCADE, unique=True, null=True)
    name = models.CharField(max_length=250, db_index=True, unique=True)
    slug = AutoSlugField(populate_from='name', slugify=unicode_slugify, db_index=True,
                         max_length=250, blank=True, unique=True, null=True)

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

    latest_updated_time = models.DateTimeField(auto_now_add=True)
    src_url = models.TextField(unique=True)
    src_latest_chapter_url = models.CharField(max_length=250, blank=True, null=True)
    src_campaign = models.ForeignKey(CrawlCampaignSource, on_delete=models.CASCADE)

    attempt = models.SmallIntegerField(default=0)

    def __str__(self):
        return self.name

    @property
    def structured_data(self):
        """
        This property cached in html template
        :return:
        """
        first_chapter = self.first_chapter
        latest_chapter = self.latest_chapter
        site_url = "https://" + Site.objects.get_current().domain
        url = site_url + self.get_absolute_url()
        data = {
            '@id': '#novel',
            '@type': 'Book',
            'name': self.name,
            'genre': [
                site_url + genre.get_absolute_url()
                for genre in self.genres.all()
            ],
            'author': [{
                '@type': 'Person',
                'name': author.name,
            } for author in self.authors.all()],
            'dateModified': self.latest_updated_time.strftime('%Y-%m-%d'),
            'url': url,
            "aggregateRating": {
                "@type": "AggregateRating",
                "ratingValue": self.vote,
                "reviewCount": self.vote_total or 1,
            },
            'hasPart': [
            ]

        }

        if self.thumbnail_image:
            data['image'] = self.thumbnail_image

        if first_chapter:
            data['hasPart'].append({
                '@id': '#first',
                "@type": [
                    "Book",
                    "PublicationVolume"
                ],
                "name": first_chapter.name,
                "url": site_url + first_chapter.get_absolute_url(),
                "isPartOf": "#novel",
                "inLanguage": "vi",
                "volumeNumber": "1",
            })
        if latest_chapter:
            data['hasPart'].append({
                '@id': '#latest',
                "@type": [
                    "Book",
                    "PublicationVolume"
                ],
                "name": latest_chapter.name,
                "url": site_url + latest_chapter.get_absolute_url(),
                "isPartOf": "#novel",
                "inLanguage": "vi",
                "volumeNumber": self.chapter_total,
            })

        return data

    @cached_property
    def authors_name(self):
        return ", ".join([str(p.name) for p in self.authors.all()])

    @cached_property
    def genres_name(self):
        return ", ".join([str(p.name) for p in self.genres.all()])

    @cached_property
    def status_name(self):
        return self.status and self.status.name or None

    @cached_property
    def genre_all(self):
        return self.genres.all()

    @classmethod
    def get_available_novel(cls):
        deactive_ids = cls.objects.filter(genres__active=False).values_list('id', flat=True).distinct()
        available_novels = cls.objects.filter(~Q(id__in=deactive_ids),
                                              active=True, publish=True).distinct()
        return available_novels

    @property
    def novel_chapter_condition(self):
        return {
            "novel_id": self.id,
            "chapter_updated": True,
            "active": True
        }

    def update_flat_info(self):
        chapter_total = len(self.chapters)
        if chapter_total == 0:
            return False

        if not self.novel_flat:
            self.novel_flat = NovelFlat()

        self.novel_flat.first_chapter = self.chapters[0].flat_info()
        self.novel_flat.latest_chapter = self.chapters[chapter_total - 1].flat_info()
        self.novel_flat.chapters = {
            "total": chapter_total,
            "list": [chap.flat_info() for chap in self.chapters]
        }
        self.novel_flat.save()

    @cached_property
    def chapter_total(self):
        return NovelChapter.objects.filter(**self.novel_chapter_condition).count()

    @cached_property
    def chapters(self):
        return NovelChapter.objects.filter(**self.novel_chapter_condition).all()

    @cached_property
    def first_chapter(self):
        return NovelChapter.objects.filter(**self.novel_chapter_condition).last()

    @cached_property
    def latest_chapter(self):
        return NovelChapter.objects.filter(**self.novel_chapter_condition).first()

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

    @cached_property
    def stream_thumbnail_image(self):
        if not self.thumbnail_image:
            return "#"

        if self.thumbnail_image.startswith('/static'):
            return self.thumbnail_image

        referer = urlparse(self.src_url)
        referer_url = referer.scheme + "://" + referer.netloc
        origin_url = (self.thumbnail_image or "").strip()

        if origin_url.strip().startswith('//'):
            origin_url = referer.scheme + ":" + origin_url
        elif origin_url.strip().startswith('/'):
            origin_url = referer_url.strip('/') + "/" + origin_url

        if 'blogspot.com' in self.thumbnail_image:
            referer_url = None

        json_str = json.dumps({
            "origin_url": origin_url,
            "referer": referer_url,
        })
        image_hash = hashlib.md5(json_str.encode()).hexdigest()
        if not settings.redis_image.get(image_hash):
            settings.redis_image.set(image_hash, json_str)

        return "/images/thumbnail/%s.jpg" % image_hash


class NovelChapter(models.Model):
    class Meta:
        db_table = "novel_chapters"
        unique_together = [('name', 'novel'), ('slug', 'novel'), ('src_url', 'novel')]
        ordering = ["id"]

    novel = models.ForeignKey(Novel, on_delete=models.CASCADE)
    name = models.CharField(max_length=250, db_index=True)

    novel_slug = models.CharField(max_length=250, blank=True, null=True)
    slug = AutoSlugField(populate_from='name', slugify=unicode_slugify, max_length=250, blank=True, null=True,
                         db_index=True)

    view_total = models.IntegerField(default=0, null=True)

    chapter_updated = models.BooleanField(default=False)
    binary_content = models.BinaryField(blank=True, null=True)
    images_content = models.TextField(blank=True, null=True)

    # Datetime
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    src_url = models.TextField()

    active = models.BooleanField(default=True)
    attempt = models.SmallIntegerField(default=0)

    def __str__(self):
        return self.name

    def flat_info(self):
        return {
            "id": self.id,
            "name": self.name,
            "url": self.get_absolute_url(),
            "source_url": self.src_url,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }

    @classmethod
    def get_undownloaded_images_chapters(cls):
        return cls.objects.filter(active=True, cdnnovelfile=None) \
                   .order_by('-updated_at', '-view_total', '-id').all()[0:20]

    @classmethod
    def get_available_chapter(cls):
        return cls.objects.filter(active=True, chapter_updated=True).all()

    @cached_property
    def images(self):
        images = []
        if self.images_content:
            images = self.images_content.split('\n')
        return images

    @cached_property
    def created_at_str(self):
        return datetime2string(self.created_at)

    @cached_property
    def next_chapter(self):
        next_chap = NovelChapter.objects.filter(novel_id=self.novel_id, pk__gt=self.id).first()
        return next_chap

    @cached_property
    def prev_chapter(self):
        prev_chap = NovelChapter.objects.filter(novel_id=self.novel_id, pk__lt=self.id).last()
        return prev_chap

    @cached_property
    def decompress_content(self):
        try:
            if self.binary_content and len(self.binary_content) > 0:
                decompresed = zlib.decompress(self.binary_content).decode()
                return decompresed
        except:
            pass
        return None

    def get_absolute_url(self):
        return reverse("chapter", args=[self.novel_slug, self.slug])


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
        return cls.objects.all()


class NovelUserProfile(models.Model):
    class Meta:
        db_table = "novel_user_profiles"

    user_id = models.IntegerField(primary_key=True)
    avatar = models.CharField(max_length=250, null=True, blank=True)

    @classmethod
    def get_profiles(cls, user_id):
        return cls.objects.filter(user_id=user_id).first()


class CDNNovelFile(models.Model):
    class Meta:
        db_table = "cdn_novel_files"
        unique_together = [('cdn', 'hash_origin_url')]

    cdn = models.ForeignKey(CDNServer, on_delete=models.CASCADE)
    chapter = models.ForeignKey(NovelChapter, on_delete=models.CASCADE, null=True, blank=True)
    type = models.CharField(max_length=250)
    hash_origin_url = models.CharField(max_length=250, db_index=True)
    url = models.TextField(blank=True, null=True)
    url_hash = models.TextField(blank=True, null=True)
    retry = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    full = models.BooleanField(default=False)
    allow_limit = models.BooleanField(default=False)

    @classmethod
    def get_missing_files(cls):
        limit_time = datetime.now() - timedelta(minutes=10)
        return cls.objects.filter(full=False,
                                  allow_limit=settings.BACKBLAZE_NOT_ALLOW_LIMIT,
                                  retry__lte=settings.BACKBLAZE_MAX_RETRY,
                                  updated_at__lte=limit_time).all()[0:50]
