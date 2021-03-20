import os
import os
import shutil
import time
from urllib.parse import urlparse

from django.core.management.base import BaseCommand
from django_backblaze_b2 import BackblazeB2Storage

from django_cms import settings
from django_cms.utils.helpers import download_cdn_file, get_short_url, str_format_num_alpha_only
from novel.models import Novel


class CDNThumbnailProcess:

    def __init__(self, bucket_name='nettruyen', local_path='', origin_domain=''):
        self.b2 = BackblazeB2Storage(opts={'bucket': bucket_name, 'allowFileOverwrites': True})
        self.local_path = local_path
        self.origin_domain = origin_domain

    def upload_file2b2(self, file_path, b2_file_name, bucket_name='nettruyen'):
        if not self.b2.bucket:
            self.b2.bucket = bucket_name
        self.b2.bucket.upload_local_file(file_path, b2_file_name)

    def get_cdn_domain(self):
        cdn_domain = settings.BACKBLAZE_FRIENDLY_ALIAS_URL or settings.BACKBLAZE_FRIENDLY_URL
        return cdn_domain.rstrip("/")

    def download_file_to_local(self, origin_file_url, local_path, file_name, referer=None):
        # Check local is exist the file, just return to upload it without download it again
        source = origin_file_url
        short_path = get_short_url(source)
        if not local_path:
            local_path = self.local_path
        _, ext = os.path.splitext(short_path)
        ext = ext or '.jpg'
        output_file = "%s/%s/%s" % (settings.CDN_FILE_FOLDER, local_path, file_name)
        if os.path.isfile(output_file + ext):
            return output_file + ext

        # Get file from origin url and download to local server
        target_file = "%s/%s" % (local_path, file_name)
        local_image = download_cdn_file(source=source, target_file=target_file, ext=ext, referer=referer,
                                        optimize=False)
        return local_image

    def upload_file_to_cdn(self, local_file):
        # Process to upload local files to remote CDN server
        if not local_file:
            return None
        b2_file_name = local_file.replace(settings.CDN_FILE_FOLDER, '')
        self.upload_file2b2(local_file, b2_file_name.lstrip('/'))
        return "%s/%s" % (self.get_cdn_domain(), b2_file_name.lstrip('/'))

    def remove_file(self, local_full_file_path):
        # Process to remove local files after we upload them to the CDN server
        try:
            os.remove(local_full_file_path)
        except OSError as e:
            print("[remove_file] Error: %s : %s" % (local_full_file_path, e.strerror))

    def remove_path_files(self, local_path):
        if not local_path and self.local_path:
            local_path = self.local_path
        full_path = "%s/%s" % (settings.CDN_FILE_FOLDER, local_path)

        try:
            shutil.rmtree(full_path, ignore_errors=False)
        except OSError as e:
            print("[remove_path_files] Error: %s : %s" % (full_path, e.strerror))

    def full_schema_url(self, url):
        if url.strip().startswith('//'):
            url = "http:" + url
        elif url.strip().startswith('/'):
            if self.origin_domain:
                url = self.origin_domain.strip('/') + url
        else:
            url = url.rstrip('/')

        return url

    def get_referer(self, src_url):
        origin_domain = urlparse(src_url) if src_url else None
        referer = origin_domain.scheme + "://" + origin_domain.netloc if origin_domain else None
        return referer

    # For the files has been processed before but not get any images
    def process_files(self):
        print('[process_files] Starting...')
        init_time = time.time()

        novels = Novel.get_not_uploaded_cdn_thumbs()
        # processed_files = []
        print('[process_files] total %s records' % len(novels))
        for novel in novels:
            start_time = time.time()
            referer = self.get_referer(novel.src_url)
            novel_slug = str_format_num_alpha_only(novel.slug)
            local_path = "thumbnails"
            url = self.full_schema_url(novel.thumbnail_image)

            # Download Files to local server
            success_file = self.download_file_to_local(origin_file_url=url, local_path=local_path,
                                                       file_name=novel_slug,
                                                       referer=referer)
            if not success_file:
                print('[process_files][%s-%s] NO thumbnail image downloaded %s' % (local_path, novel.id, url))
                continue

            # Upload File to CDN
            cdn_url_novel = self.upload_file_to_cdn(local_file=success_file)

            uploaded_time = time.time() - start_time
            print('[process_files][%s-%s] spent %s to uploaded %s'
                  % (local_path, novel.id, uploaded_time, success_file))

            # Update thumbnail src
            if not cdn_url_novel:
                print('[process_files][%s-%s] NO thumbnail image uploaded %s' % (local_path, novel.id, url))
                continue

            if novel.thumbnail_image != cdn_url_novel:
                novel.thumbnail_image = cdn_url_novel
                # processed_files.append(novel)
                novel.save()

            # Remove Files from local
            self.remove_file(success_file)

        # if processed_files:
        #     Novel.objects.bulk_update(processed_files, ['thumbnail_image'])

        finish_time = time.time() - init_time
        print('[process_files] Finish in ', finish_time, 's')


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        print('[CDN Thumbnail Processing Files] Starting...')
        try:
            cdn_process = CDNThumbnailProcess()
            cdn_process.process_files()
        except Exception as e:
            print("[CDN Thumbnail Processing Files] Error: %s" % e)

        print('[CDN Thumbnail Processing Files] Finish')
