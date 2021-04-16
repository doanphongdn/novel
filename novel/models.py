import hashlib
import json
import os
import re
import zlib
from datetime import datetime, timedelta
from urllib.parse import urlparse
from pathlib import Path

from autoslug import AutoSlugField
from autoslug.utils import slugify
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.db import models
from django.db import transaction
from django.db.models import Q, Count
from django.templatetags.static import static
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from unidecode import unidecode

from django_cms import settings
from django_cms.models import CDNServer
from django_cms.utils.cache_manager import CacheManager
from django_cms.utils.helpers import code_validate
from novel import utils
from novel.utils import get_first_number_pattern
from django.utils.translation import ugettext as _


def datetime2string(value):
    """ Convert updated_at to friendly string
    :return: string - ex: 1 hour ago, 1 month ago, phút
    """
    diff_timestamp = datetime.timestamp(datetime.now()) - datetime.timestamp(value)

    if diff_timestamp / 60 < 60:
        updated_at = "%s " % (int(diff_timestamp / 60) + 1) + _("minute(s) ago")
    elif diff_timestamp / 3600 < 24:
        updated_at = "%s " % int(diff_timestamp / 3600) + _("hour(s) ago")
    elif diff_timestamp / 3600 / 24 < 30:
        updated_at = "%s " % int(diff_timestamp / 3600 / 24) + _("day(s) ago")
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
    thumbnail_image_replace = models.ImageField(upload_to="images/novels", blank=True, null=True)
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
            "description": _("The fastest and most complete updated {} comics at {}.").format(self.name, domain),
            "aggregateRating": {
                "itemReviewed": {
                    "@type": "Book",
                    "name": self.name,
                },
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
        return ", ".join([str(p.name) for p in self.genres.filter(active=True).all()])

    @cached_property
    def status_name(self):
        return self.status and self.status.name or None

    @cached_property
    def genre_all(self):
        return self.genres.filter(active=True).all()

    @classmethod
    def get_available_novel(cls):
        deactive_ids = cls.objects.filter(genres__active=False).values_list('id', flat=True).distinct()
        available_novels = cls.objects.filter(~Q(id__in=deactive_ids),
                                              active=True, publish=True).distinct()
        return available_novels

    @classmethod
    def get_not_uploaded_cdn_thumbs(cls):
        return cls.objects.filter(~Q(thumbnail_image__icontains='cdn.nettruyen.vn'),
                                  active=True).order_by('-updated_at').all()[0:10000]

    @property
    def novel_chapter_condition(self):
        return {
            "novel_id": self.id,
            # "chapter_updated": True,
            "active": True,
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

    def update_chapter_name(self):
        for chatper in self.chapters:
            chatper.update_name()

    @cached_property
    def chapter_total(self):
        return NovelChapter.objects.filter(**self.novel_chapter_condition).count()

    @cached_property
    def chapters(self):
        return NovelChapter.objects.filter(**self.novel_chapter_condition).order_by("name_index").order_by("id").all()

    @cached_property
    def first_chapter(self):
        return NovelChapter.objects.filter(**self.novel_chapter_condition).order_by("--name_index").last()

    @cached_property
    def latest_chapter(self):
        return NovelChapter.objects.filter(**self.novel_chapter_condition).order_by("--name_index").first()

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

        # TODO: do not hard the 'cdn' string here, let replace by cdn server configuration
        if self.thumbnail_image.startswith(('/static', '/media')) or '//cdn.' in self.thumbnail_image:
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
    name_index = models.FloatField(db_index=True, null=True, default=-1)

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
    def get_undownloaded_images_chapters(cls, order_by_list=['-view_total', '-updated_at', '-id'], limit=20):
        return cls.objects.filter(active=True, chapter_updated=True, cdnnovelfile=None) \
                   .order_by(*order_by_list).all()[0:limit]

    @classmethod
    def get_available_chapter(cls):
        return cls.objects.filter(active=True).all()

    @cached_property
    def images(self):
        images = []
        if self.images_content:
            if self.images_content.strip().startswith('<video '):
                images = [self.images_content]
            else:
                images = self.images_content.split('\n')
        return images

    @cached_property
    def created_at_str(self):
        return datetime2string(self.created_at)

    @cached_property
    def next_chapter(self):
        next_chap = NovelChapter.objects.filter(novel_id=self.novel_id, name_index__gt=self.name_index) \
            .order_by("name_index").first()
        if not next_chap:
            next_chap = NovelChapter.objects.filter(novel_id=self.novel_id, id__gt=self.id) \
                .order_by("id").first()
        return next_chap

    @cached_property
    def prev_chapter(self):
        prev_chap = NovelChapter.objects.filter(novel_id=self.novel_id, name_index__lt=self.name_index) \
            .order_by("name_index").last()
        if not prev_chap:
            prev_chap = NovelChapter.objects.filter(novel_id=self.novel_id, id__lt=self.id) \
                .order_by("id").last()
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

    def remove_cdn_files(self):
        # Get CDN item
        cdn_file = CDNNovelFile.objects.filter(chapter_id=self.id).first()
        if cdn_file:
            path = "%s/%s" % (self.novel_slug, self.slug)
            if cdn_file.url:
                for file in cdn_file.url:
                    file_path = Path(file)
                    utils.remove_b2_files(path + "/" + file_path.name)
                cdn_file.url = None
                cdn_file.full = False
                cdn_file.url_hash = None
                cdn_file.save()
            else:
                for idx, url in enumerate(self.images):
                    utils.remove_b2_files(path + "/" + str(idx) + ".jpg")

    def update_name(self):
        if 'en' not in settings.LANGUAGE_CODE and self.name.startswith('Chapter'):
            self.name = self.name.replace('Chapter', os.environ.get('LANGUAGE_CHAPTER_NAME', 'Chương'))
            self.save()

    def save(self, *args, **kwargs):
        if not self.name_index:
            self.name_index = get_first_number_pattern(self.name, os.environ.get('LANGUAGE_CHAPTER_NAME', 'Chapter'))
        if 'en' not in settings.LANGUAGE_CODE and self.name.startswith('Chapter'):
            self.name = self.name.replace('Chapter', os.environ.get('LANGUAGE_CHAPTER_NAME', 'Chương'))
        super(NovelChapter, self).save(*args, **kwargs)


class NovelSetting(models.Model):
    class Meta:
        db_table = "novel_settings"

    title = models.CharField(max_length=250)
    favicon = models.ImageField(upload_to="images", null=True, blank=True)
    logo = models.ImageField(upload_to="images", null=True, blank=True)
    meta = models.JSONField(null=True, blank=True)
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
    ads_txt = models.TextField(blank=True, null=True)
    robots_txt = models.TextField(blank=True, null=True)
    img_ignoring = models.TextField(null=True, blank=True)
    google_analytics_id = models.TextField(null=True, blank=True)
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
    def get_avatar(cls, user):
        if user and user.is_authenticated:
            user_profile = CacheManager(NovelUserProfile, **{"user_id": user.id}).get_from_cache()
            if user_profile:
                return user_profile.avatar

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
                                  url__isnull=True,
                                  # allow_limit=settings.BACKBLAZE_NOT_ALLOW_LIMIT,
                                  retry__lte=settings.BACKBLAZE_MAX_RETRY,
                                  updated_at__lte=limit_time).order_by('-updated_at').all()[0:50]


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
    report_count = models.IntegerField(default=0)

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
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)


class History(models.Model):
    class Meta:
        db_table = 'novel_histories'
        unique_together = ('user', 'novel',)

    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE, db_index=True)
    chapter = models.ForeignKey(NovelChapter, on_delete=models.CASCADE, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

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


NOVEL_ADV_GROUPS = (
    ('base', "BASE"),
    ('index', "INDEX"),
    ('novel_all', "NOVEL ALL"),
    ('novel_info', "NOVEL INFO"),
    ('novel_chapter', "NOVEL CHAPTER"),
)
NOVEL_ADV_PLACES = (
    # Base, apply all page
    ('base_header', _('BASE HEADER')),
    ('base_top', _('BASE TOP')),
    ('base_bottom', _('BASE BOTTOM')),
    ('base_scroll_left', _('BASE SCROLL LEFT')),
    ('base_scroll_right', _('BASE SCROLL RIGHT')),

    # Index page
    ('index_header', _('INDEX HEADER')),
    ('index_top', _('INDEX TOP')),
    ('index_bottom', _('INDEX BOTTOM')),
    ('index_sidebar', _('INDEX SIDEBAR')),
    ('index_inside_content', _('INDEX INSIDE CONTENT')),
    ('index_after_content', _('INDEX AFTER CONTENT')),

    # Novel all page
    ('novel_all_header', _('NOVEL ALL HEADER')),
    ('novel_all_top', _('NOVEL ALL TOP')),
    ('novel_all_bottom', _('NOVEL ALL END')),

    # Novel info page
    ('novel_info_header', _('NOVEL INFO HEADER')),
    ('novel_info_top', _('NOVEL INFO TOP')),
    ('novel_info_bottom', _('NOVEL INFO BOTTOM')),
    ('novel_info_right', _('NOVEL INFO RIGHT')),
    ('novel_info_after_thumbnail', _('NOVEL INFO AFTER THUMBNAIL')),
    ('novel_info_before_chap_list', _('NOVEL INFO BEFORE CHAP LIST')),
    ('novel_info_after_chap_list', _('NOVEL INFO AFTER CHAP LIST')),
    ('novel_info_before_comment', _('NOVEL INFO BEFORE COMMENT')),

    # Novel chapter page
    ('novel_chapter_header', _('NOVEL CHAPTER HEADER')),
    ('novel_chapter_top', _('NOVEL CHAPTER TOP')),
    ('novel_chapter_bottom', _('NOVEL CHAPTER BOTTOM')),
    ('novel_chapter_before_content', _('NOVEL CHAPTER BEFORE CONTENT')),
    ('novel_chapter_inside_content', _('NOVEL CHAPTER INSIDE CONTENT')),
    ('novel_chapter_before_comment', _('NOVEL CHAPTER BEFORE COMMENT')),
    ('novel_chapter_scroll_left', _('NOVEL CHAPTER SCROLL LEFT')),
    ('novel_chapter_scroll_right', _('NOVEL CHAPTER SCROLL RIGHT')),
)


class NovelAdvertisementPlace(models.Model):
    class Meta:
        db_table = 'novel_advertisement_places'
        ordering = ("group", "code")

    group = models.CharField(max_length=50, choices=NOVEL_ADV_GROUPS)
    code = models.CharField(max_length=50, choices=NOVEL_ADV_PLACES, unique=True)
    base_override = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    def __str__(self):
        for val in NOVEL_ADV_PLACES:
            if val[0] == self.code:
                return val[1]

        return self.code


DEVICES = (('all', 'ALL'), ('mobile', 'MOBILE'), ('pc', 'DESKTOP'))


class NovelAdvertisement(models.Model):
    class Meta:
        db_table = 'novel_advertisements'

    name = models.CharField(max_length=250)
    ad_type = models.CharField(max_length=50, choices=DEVICES, default='all')
    ad_content = models.TextField()
    places = models.ManyToManyField(NovelAdvertisementPlace, db_table="novel_adv_adv_place_rel")

    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


PARAMS = [
    ('comment_filters', 'COMMENT FILTERS')
]


class NovelParam(models.Model):
    class Meta:
        db_table = "novel_params"

    key = models.CharField(max_length=50, validators=[code_validate], unique=True, choices=PARAMS)
    values = models.TextField()
    active = models.BooleanField(default=True)


class NovelNotify(models.Model):
    class Meta:
        db_table = "novel_notifications"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE, blank=True, null=True)
    notify = models.TextField()
    read = models.BooleanField(default=False)

    # Datetime
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    @classmethod
    def unread_notify_number(cls, user):
        number = cls.objects.filter(user=user, read=False).count()
        return number

    @classmethod
    def get_notify(cls, user):
        return cls.objects.filter(user=user).order_by("-id").order_by("read").all()
