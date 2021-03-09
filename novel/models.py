import hashlib
import json
import zlib
from datetime import datetime, timedelta
from urllib.parse import urlparse

from autoslug import AutoSlugField
from autoslug.utils import slugify
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.db import models
from django.db import transaction
from django.db.models import Q
from django.templatetags.static import static
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from unidecode import unidecode

from django_cms import settings
from django_cms.models import CDNServer
from django_cms.settings import SITE_URL
from django_cms.utils.cache_manager import CacheManager


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
    style_color = models.CharField(max_length=50, default='', blank=True, null=True)
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

    novel_flat = models.OneToOneField(NovelFlat, on_delete=models.CASCADE, null=True)
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

    hot_novel = models.BooleanField(default=False)
    follow = models.IntegerField(default=0)
    vote = models.FloatField(default=5)
    vote_total = models.IntegerField(default=1)
    view_daily = models.IntegerField(default=0)
    view_monthly = models.IntegerField(default=0)
    view_total = models.IntegerField(default=0)
    hot_point = models.IntegerField(default=0)

    latest_updated_time = models.DateTimeField(auto_now_add=True)
    src_url = models.TextField(unique=True)
    src_latest_chapter_url = models.CharField(max_length=250, blank=True, null=True)
    src_campaign = models.CharField(max_length=50)

    attempt = models.SmallIntegerField(default=0)
    crawl_errors = models.TextField(default='', blank=True, null=True)

    def __str__(self):
        return self.name

    @cached_property
    def structured_data(self):
        """
        This property cached in html template
        :return:
        """
        novel_setting = CacheManager(NovelSetting).get_from_cache()
        domain = Site.objects.get_current().domain
        site_url = "https://" + domain
        data = {
            '@id': '#novel',
            "@type": "Article",
            'headline': self.name,
            'author': [{
                '@type': 'Person',
                'name': author.name,
            } for author in self.authors.all()],
            'genre': [
                genre.name
                for genre in self.genres.all()
            ],
            "publisher": {
                "@type": "Organization",
                "name": domain.title(),
                "logo": {
                    "@type": "ImageObject",
                    "url": site_url + novel_setting.logo.url
                }
            },
            "url": site_url,
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": site_url + self.get_absolute_url()
            },
            "datePublished": self.created_at.strftime('%Y-%m-%d'),
            "dateCreated": self.created_at.strftime('%Y-%m-%d'),
            'dateModified': self.latest_updated_time.strftime('%Y-%m-%d'),
            "description": _("""The fastest and most complete updated %s comics at %s.""" % (self.name, domain)),
            "aggregateRating": {
                "@type": "AggregateRating",
                "ratingValue": self.vote,
                "bestRating": 5,
                "reviewCount": self.vote_total or 1,
            },
        }

        if self.thumbnail_image:
            data['image'] = site_url + self.stream_thumbnail_image

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
            # "chapter_updated": True,
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

        for ignoring_referer in settings.IGNORE_REFERER_FOR.split(","):
            if ignoring_referer in self.thumbnail_image:
                referer_url = None
                break

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
    crawl_errors = models.TextField(default='', blank=True, null=True)

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
        return cls.objects.filter(active=True, chapter_updated=True, cdnnovelfile=None) \
                   .order_by('-view_total', '-updated_at', '-id').all()[0:20]

    @classmethod
    def get_available_chapter(cls):
        return cls.objects.filter(active=True).all()

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
                return zlib.decompress(self.binary_content).decode()
        except Exception as e:
            print("[decompress_content] Error %s " % e)
            pass

        return ""

    @cached_property
    def absolute_url(self):
        return self.get_absolute_url()

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
        return cls.objects.get_or_create(user_id=user_id)

    @classmethod
    def get_avatar(cls, user):
        if user and user.is_authenticated:
            profile = cls.objects.filter(user_id=user.id).first()
            if profile:
                return profile.avatar

        return static("images/user-default.png")


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


class Comment(models.Model):
    class Meta:
        db_table = 'novel_comments'

    novel = models.ForeignKey(Novel, on_delete=models.CASCADE)
    chapter = models.ForeignKey(NovelChapter, null=True, on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    parent_id = models.IntegerField(null=True)
    reply_id = models.IntegerField(null=True)
    name = models.CharField(max_length=250)
    content = models.TextField()

    # Datetime
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def updated_at_str(self):
        return datetime2string(self.updated_at)

    @property
    def created_at_str(self):
        return datetime2string(self.created_at)


class CrawlNovelRetry(models.Model):
    class Meta:
        db_table = "crawl_novel_retry"

    novel = models.OneToOneField(Novel, on_delete=models.CASCADE)
    chapter = models.OneToOneField(NovelChapter, on_delete=models.CASCADE)
    is_processing = models.BooleanField(default=False)

    # Datetime
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def create_crawl_retry(cls, chapter):
        obj = cls.objects.filter(novel=chapter.novel).first()
        created = None
        if not obj:
            obj, created = CrawlNovelRetry.objects.get_or_create(novel=chapter.novel, chapter=chapter,
                                                                 is_processing=False)
        return obj, created

    @classmethod
    def get_available_records(cls):
        with transaction.atomic():
            return cls.objects.select_for_update().filter().all()[0:10]


class Bookmark(models.Model):
    class Meta:
        db_table = 'novel_bookmarks'
        unique_together = ('user', 'novel',)

    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE, db_index=True)


class History(models.Model):
    class Meta:
        db_table = 'novel_histories'
        unique_together = ('user', 'novel',)

    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE, db_index=True)
    chapter = models.ForeignKey(NovelChapter, on_delete=models.CASCADE, db_index=True)

    @classmethod
    def get_chapter_history_by_user(cls, user):
        return NovelChapter.objects.filter(
            id__in=cls.objects.filter(user=user).values_list('chapter', flat=True).distinct()).all()


class Rating(models.Model):
    class Meta:
        db_table = 'novel_ratings'
        unique_together = ('user', 'comic',)

    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    comic = models.ForeignKey(Novel, on_delete=models.CASCADE, db_index=True)
    rating_point = models.SmallIntegerField(default=0)


class AllowIP(models.Model):
    class Meta:
        db_table = 'novel_allow_ips'

    path_regex = models.CharField(max_length=250)
    method = models.CharField(max_length=10)
    ip = models.JSONField(blank=True, null=True)


class NovelReport(models.Model):
    class Meta:
        db_table = 'novel_reports'

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE, null=True, blank=True)
    chapter = models.ForeignKey(NovelChapter, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()

    # Datetime
    created_at = models.DateTimeField(auto_now_add=True, null=True)
