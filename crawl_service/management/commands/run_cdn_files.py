import hashlib
import os
import shutil
import time
from os.path import basename, splitext
from threading import Thread
from urllib.parse import urlparse

from django.core.management.base import BaseCommand
from django.db import transaction
from django_backblaze_b2 import BackblazeB2Storage

from crawl_service import settings, utils
from crawl_service.models import CDNServer
from novel.models import CDNNovelFile, NovelChapter


class CDNProcess:

    def __init__(self):
        available_cdn = CDNServer.get_available_cdn()
        if available_cdn:
            self.cdn = available_cdn[0]
            self.b2 = BackblazeB2Storage(opts={'bucket': self.cdn.name, 'allowFileOverwrites': True})
        else:
            print('[CDN Processing Files] Not found CDN server configuration!')
            raise ValueError("Not found CDN server configuration!")

        self.origin_domain = None
        self.local_path = None

    def update_status(self, status):
        """
        Update status as 'running' or 'stopped'
        """
        self.cdn.status = status
        self.cdn.save()

    def upload_file2b2(self, file_path, b2_file_name, bucket_name='nettruyen'):
        if not self.b2.bucket:
            self.b2.bucket = bucket_name
        self.b2.bucket.upload_local_file(file_path, b2_file_name)

    def download_file_to_local(self, origin_file_urls, local_path, referer=None, limit_image=-1):
        success_files = []
        for idx, origin_file in enumerate(origin_file_urls):
            # stop download if reach limit images
            if limit_image and idx >= limit_image:
                break
            # Check local is exist the file, just return to upload it without download it again
            source = origin_file.get('url')
            _, ext = os.path.splitext(source)
            output_file = "%s/%s/%s" % (settings.CDN_FILE_FOLDER, local_path, str(origin_file.get('index')))
            if os.path.isfile(output_file + ext):
                success_files.append({'index': origin_file.get('index'), 'url': output_file + ext})
                continue

            # Get file from origin url and download to local server
            if not local_path and self.local_path:
                local_path = self.local_path
            target_file = "%s/%s" % (local_path, str(origin_file.get('index')))
            local_image = utils.download_cdn_file(source=source, target_file=target_file, ext=ext, referer=referer)
            success_files.append({'index': origin_file.get('index'), 'url': local_image})
        return success_files

    def upload_file_to_cdn(self, local_files):
        # Process to upload local files to remote CDN server
        for local_file in local_files:
            if not local_file.get('url'):
                continue
            b2_file_name = local_file.get('url').replace(settings.CDN_FILE_FOLDER, '')
            # utils.upload_file_to_b2(local_file, b2_file_name)
            self.upload_file2b2(local_file.get('url'), b2_file_name.lstrip('/'))
        return

    def remove_file(self, local_files, local_path, exclude_path=False):
        # Process to remove local files after we upload them to the CDN server
        for local_file in local_files:
            file_path = local_file
            if not exclude_path:
                if not local_path and self.local_path:
                    local_path = self.local_path
                file_path = local_path + "/" + file_path
            try:
                os.remove(file_path)
            except OSError as e:
                print("[remove_file] Error: %s : %s" % (file_path, e.strerror))

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


class Command(BaseCommand):

    def __init__(self, cdn_process=None):
        self.cdn_process = cdn_process

    def process_missing_files(self):
        print('[process_missing_files] Starting...')
        if not self.cdn_process:
            print('[process_missing_files] Missing cdn object...')
            print('[process_missing_files] Finish')
            return

        init_time = time.time()

        files = CDNNovelFile.get_missing_files()
        print('[process_missing_files] total %s records' % len(files))
        for file in files:
            start_time = time.time()

            referer = self.get_referer(file.chapter)
            local_path = "%s/%s" % (file.chapter.novel.slug, file.chapter.slug)
            urls = [self.cdn_process.full_schema_url(img_url) for img_url in file.chapter.images_content.split("\n")]

            # validate images are missing
            missing_files = []
            for idx, chapter_image in enumerate(urls):
                origin_img = hashlib.md5(chapter_image.encode()).hexdigest()
                if not file.url or origin_img not in file.url:
                    missing_files.append({"index": idx, "url": chapter_image})

            # get_img_time = time.time() - start_time
            # print('[process_missing_files][%s-%s] spent %s to get %s missing images'
            #       % (local_path, file.chapter.id, get_img_time, len(missing_files)))

            # Download Files to local server
            success_files = self.cdn_process.download_file_to_local(origin_file_urls=missing_files,
                                                                    local_path=local_path,
                                                                    referer=referer)
            # downloaded_time = time.time() - get_img_time - start_time
            # print('[process_missing_files][%s-%s] spent %s to download %s missing images'
            #       % (local_path, file.chapter.id, downloaded_time, len(missing_files)))

            if not len(success_files):
                print('[process_missing_files][%s-%s] NO missing images uploaded' % (local_path, file.chapter.id))
                continue

            # Upload Files to CDN
            self.cdn_process.upload_file_to_cdn(local_files=success_files)

            # uploaded_time = time.time() - downloaded_time - get_img_time - start_time
            uploaded_time = time.time() - start_time
            print('[process_missing_files][%s-%s] spent %s to upload %s missing images'
                  % (local_path, file.chapter.id, uploaded_time, len(success_files)))

            # Update status and url to CDNNovelFile
            existed_urls = file.url.split("\n") if file.url else []
            sorted_success_files = sorted(success_files, key=lambda i: i['index'], reverse=True)
            for success_file in sorted_success_files:
                if not success_file.get('url'):
                    continue
                local_file = success_file.get('url').replace(settings.CDN_FILE_FOLDER, '').lstrip('/')
                existed_urls.append(local_file)

            # we have to sort the list to make sure the images is correct ordering
            # regex map url: ^(.+\/)*(.+)\.(.+)$
            existed_urls = list(set(existed_urls)) # Ensure have no duplication items
            new_list = [splitext(basename(x))[0] for x in existed_urls]
            fin_list = list(zip(existed_urls, new_list))
            fin_list = [x[0] for x in sorted(fin_list, key=lambda x: int(x[1]))]
            file.url = "\n".join(fin_list) if len(fin_list) else None

            if not len(fin_list):
                print('[process_missing_files][%s-%s] unable to download any missing images'
                      % (local_path, file.chapter.id))

            if len(urls) == len(fin_list):
                file.full = True
            else:
                file.full = False
                file.retry = file.retry + 1
            file.save()

            # Remove Files from local
            self.cdn_process.remove_path_files(file.chapter.novel.slug)

        finish_time = time.time() - init_time
        print('[process_missing_files] Finish in ', finish_time, 's')

    def process_rest_files(self):
        print('[process_rest_files] Starting...')
        if not self.cdn_process:
            print('[process_rest_files] Missing cdn object...')
            print('[process_rest_files] Finish')
            return

        init_time = time.time()

        chapters = NovelChapter.get_undownloaded_images_chapters()

        inserted_files = None
        with transaction.atomic():
            new_files = [CDNNovelFile(cdn=self.cdn_process.cdn, chapter=chapter, type='chapter',
                                      hash_origin_url=hashlib.md5(chapter.url.encode()).hexdigest(),
                                      url=None, full=False) for chapter in chapters]

            if new_files:
                inserted_files = CDNNovelFile.objects.bulk_create(new_files, ignore_conflicts=False)

        if not inserted_files:
            print('[process_rest_files] Unable to create inserted_files...')
            print('[process_rest_files] Finish')
            return

        limit_image = int(os.environ.get('BACKBLAZE_LIMIT_IMG', 150))
        updated_files = []

        # batch_records = int(os.environ.get('BACKBLAZE_BATCH_RECORD_INSERT', 50))
        # Handle downloading & storing
        for chapter in chapters:
            start_time = time.time()

            referer = self.get_referer(chapter)
            local_path = "%s/%s" % (chapter.novel.slug, chapter.slug)
            urls = [
                {'index': idx, 'url': self.cdn_process.full_schema_url(img_url)}
                for idx, img_url in enumerate(chapter.images_content.split("\n"))
            ]

            number_urls = len(urls)

            # Download Files to local server
            success_files = self.cdn_process.download_file_to_local(origin_file_urls=urls, local_path=local_path,
                                                                    referer=referer, limit_image=limit_image)

            # downloaded_time = time.time() - start_time
            # print('[process_rest_files][%s-%s] spent %s to get %s images'
            #       % (local_path, chapter.id, downloaded_time, len(urls)))

            if not len(success_files):
                print('[process_missing_files][%s-%s] NO images uploaded' % (local_path, chapter.id))
                continue

            # Upload Files to CDN
            self.cdn_process.upload_file_to_cdn(local_files=success_files)

            # uploaded_time = time.time() - downloaded_time - start_time
            uploaded_time = time.time() - start_time
            print('[process_rest_files][%s-%s] spent %s to upload %s images'
                  % (local_path, chapter.id, uploaded_time, len(success_files)))

            # Update status and url to CDNNovelFile
            sorted_success_files = sorted(success_files, key=lambda i: i['index'])
            valid_urls = []
            for sub in sorted_success_files:
                if not sub.get('url'):
                    continue
                valid_urls.append(sub.get('url').replace(settings.CDN_FILE_FOLDER, '').lstrip('/'))
            if not len(valid_urls):
                print('[process_rest_files] Unable to get files for %s-%s/%s-%s'
                      % (chapter.novel.id, chapter.novel.slug, chapter.id, chapter.slug))
                continue
            valid_urls = list(set(valid_urls)) # Ensure have no duplication items
            result_url = "\n".join(valid_urls) if len(valid_urls) else None
            if number_urls == len(valid_urls):
                full = True
            else:
                full = False
                # retry = 0

            allow_limit = False
            if number_urls > limit_image:
                allow_limit = True

            for inserted_file in inserted_files:
                if inserted_file.id and inserted_file.chapter == chapter:
                    inserted_file.url = result_url
                    inserted_file.full = full
                    inserted_file.allow_limit = allow_limit
                    updated_files.append(inserted_file)
                    # inserted_file.save() ### => Do not save here

            # Remove Files from local
            self.cdn_process.remove_path_files(chapter.novel.slug)

        if updated_files:
            CDNNovelFile.objects.bulk_update(updated_files, ['url', 'full', 'allow_limit'])

        finish_time = time.time() - init_time
        print('[process_rest_files] Finish in', finish_time, 's')

    def get_referer(self, chapter):
        origin_domain = urlparse(chapter.url) if chapter.url else None
        referer = origin_domain.scheme + "://" + origin_domain.netloc if origin_domain else None
        return referer

    def handle(self, *args, **kwargs):
        print('[CDN Processing Files] Starting...')
        if not self.cdn_process:
            self.cdn_process = CDNProcess()

        ### Test code
        # self.cdn_process.upload_file2b2("/data/cdn/novel/goong-hoang-cung/chapter-24/0.jpg",
        #                                 "goong-hoang-cung/chapter-24/0.jpg")
        try:
            # Set status to running CDN server
            self.cdn_process.update_status('running')

            # Create threads
            t1 = Thread(target=self.process_missing_files)
            t2 = Thread(target=self.process_rest_files)

            # Start all threads
            t1.start()
            t2.start()

            # Wait for all of them to finish
            t1.join()
            t2.join()

        except Exception as e:
            print("[CDN Processing Files] Error: %s" % e)

        # Set status to running CDN server
        self.cdn_process.update_status('stopped')
        print('[CDN Processing Files] Finish')
