import hashlib
import os
import shutil
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from os.path import basename, splitext
from threading import Thread
from urllib.parse import urlparse

from django.core.management.base import BaseCommand
from django.db import transaction
from django_backblaze_b2 import BackblazeB2Storage

from django_cms import settings
from django_cms.models import CDNServer
from django_cms.utils.helpers import download_cdn_file, get_short_url, str_format_num_alpha_only, \
    download_cdn_file_multi_thread
from novel.models import CDNNovelFile, NovelChapter


class CDNProcess:

    def __init__(self, available_cdn):
        if not available_cdn:
            print('[CDN Processing Files] Not found CDN server configuration!')
            raise ValueError("Not found CDN server configuration!")
        else:
            self.cdn = available_cdn
            self.b2 = BackblazeB2Storage(opts={'bucket': self.cdn.name, 'allowFileOverwrites': True})

        self.origin_domain = self.cdn.referer
        self.local_path = None

    def update_status(self, status):
        """
        Update status as 'running' or 'stopped'
        """
        if status == 'stopped':
            self.cdn.last_run = datetime.now()
        self.cdn.status = status
        self.cdn.save()

    def upload_file2b2(self, file_path, b2_file_name, bucket_name='nettruyen'):
        if not self.b2.bucket:
            self.b2.bucket = bucket_name

        uploaded_file = None
        if not self.b2.exists(b2_file_name):
            uploaded_file = self.b2.bucket.upload_local_file(file_path, b2_file_name)

        return uploaded_file

    def upload_file2b2_multi_thread(self, pending_file, bucket_name='nettruyen'):
        if not pending_file:
            return None

        file_path = pending_file.get('url')
        if not file_path:
            return None

        if not self.b2.bucket:
            self.b2.bucket = bucket_name

        uploaded_file = None
        b2_file_name = file_path.replace(settings.CDN_FILE_FOLDER, '').lstrip('/')
        if not self.b2.exists(b2_file_name):
            uploaded_file = self.b2.bucket.upload_local_file(file_path, b2_file_name)
        pending_file['uploaded_file'] = uploaded_file
        return uploaded_file

    def download_file_to_local(self, origin_file_urls, local_path, referer=None, limit_image=-1):
        success_files = []
        for idx, origin_file in enumerate(origin_file_urls):
            # stop download if reach limit images
            if 0 < limit_image <= idx and settings.BACKBLAZE_ALLOW_LIMIT:
                break
            # # when we need to run full images after run for a limit number
            # if settings.BACKBLAZE_NOT_ALLOW_LIMIT and idx < num_downloaded_url:
            #     continue
            # Check local is exist the file, just return to upload it without download it again
            source = origin_file.get('url')
            short_path = get_short_url(source)
            _, ext = os.path.splitext(short_path)
            ext = ext or '.jpg'
            output_file = "%s/%s/%s" % (settings.CDN_FILE_FOLDER, local_path, str(origin_file.get('index')))
            if os.path.isfile(output_file + ext):
                success_files.append({
                    'index': origin_file.get('index'),
                    'url': output_file + ext,
                    'url_hash': origin_file.get('url_hash')
                })
                continue

            # Get file from origin url and download to local server
            if not local_path and self.local_path:
                local_path = self.local_path
            target_file = "%s/%s" % (local_path, str(origin_file.get('index')))
            local_image = download_cdn_file(source=source, target_file=target_file, ext=ext, referer=referer)
            success_files.append({
                'index': origin_file.get('index'),
                'url': local_image,
                'url_hash': origin_file.get('url_hash')
            })
        return success_files

    def download_file_to_local_multi_thread(self, origin_file_urls, local_path, referer=None, limit_image=-1,
                                            max_worker=5):
        success_files = []
        pending_files = []
        for idx, origin_file in enumerate(origin_file_urls):
            # stop download if reached limit images
            if 0 < limit_image <= idx and settings.BACKBLAZE_ALLOW_LIMIT:
                break
            # Check local is exist the file, just return to upload it without download it again
            source = origin_file.get('url')
            _, ext = os.path.splitext(get_short_url(source))
            ext = ext or '.jpg'
            output_file = "%s/%s/%s" % (settings.CDN_FILE_FOLDER, local_path, str(origin_file.get('index')))
            if os.path.isfile(output_file + ext):
                success_files.append({
                    'index': origin_file.get('index'),
                    'url': output_file + ext,
                    'url_hash': origin_file.get('url_hash')
                })
                continue

            # Get file from origin url and download to local server
            if not local_path and self.local_path:
                local_path = self.local_path
            target_file = "%s/%s" % (local_path, str(origin_file.get('index')))
            pending_files.append({
                'index': origin_file.get('index'),
                'url': None,
                'url_hash': origin_file.get('url_hash'),
                'source': source,
                'target_file': target_file,
                'ext': ext,
                'referer': referer,
            })

        start = time.perf_counter()  # start timer
        with ThreadPoolExecutor(max_workers=max_worker) as executor:
            results = executor.map(download_cdn_file_multi_thread,
                                   pending_files)  # this is Similar to map(func, *iterables)
        finish = time.perf_counter()  # end timer
        print(f"Finished download in {round(finish - start, 2)} seconds")

        for pending_file in pending_files:
            if pending_file.get('url'):
                success_files.append({
                    'index': pending_file.get('index'),
                    'url': pending_file.get('url'),
                    'url_hash': pending_file.get('url_hash')
                })
        return success_files

    def upload_file_to_cdn(self, local_files, explicit_restriction=True):
        # Process to upload local files to remote CDN server
        img_hash = []
        for local_file in local_files:
            if not local_file.get('url'):
                continue
            b2_file_name = local_file.get('url').replace(settings.CDN_FILE_FOLDER, '')
            # utils.upload_file_to_b2(local_file, b2_file_name)
            uploaded_file = self.upload_file2b2(local_file.get('url'), b2_file_name.lstrip('/'))
            allow_img_hash = (explicit_restriction and uploaded_file) or (not explicit_restriction)
            if allow_img_hash and local_file.get('url_hash'):
                img_hash.append(local_file.get('url_hash'))
        return img_hash

    def upload_file_to_cdn_multi_thread(self, local_files, explicit_restriction=True, max_worker=5):
        # Process to upload local files to remote CDN server
        start = time.perf_counter()  # start timer
        with ThreadPoolExecutor(max_workers=max_worker) as executor:
            results = executor.map(self.upload_file2b2_multi_thread,
                                   local_files)  # this is Similar to map(func, *iterables)
        finish = time.perf_counter()  # end timer
        print(f"Finished upload in {round(finish - start, 2)} seconds")

        img_hash = []
        for local_file in local_files:
            if not local_file.get('url_hash'):
                continue
            allow_img_hash = (explicit_restriction and local_file.get('uploaded_file')) or (not explicit_restriction)
            if allow_img_hash and local_file.get('url_hash'):
                img_hash.append(local_file.get('url_hash'))
        return img_hash

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

    def get_referer(self, chapter):
        origin_domain = urlparse(chapter.src_url) if chapter.src_url else None
        referer = origin_domain.scheme + "://" + origin_domain.netloc if origin_domain else None
        return referer

    # For the files has been processed before but not get any images
    def process_missing_files(self, multi_thread=False):
        print('[process_missing_files] Starting...')
        if not self.cdn:
            print('[process_missing_files] Missing cdn object...')
            print('[process_missing_files] Finish')
            return

        init_time = time.time()

        files = CDNNovelFile.get_missing_files()
        processed_files = []
        limit_image = int(os.environ.get('BACKBLAZE_LIMIT_IMG', 150))
        print('[process_missing_files] total %s records' % len(files))
        for file in files:
            if self.is_ignored_chapter(file.chapter):
                continue

            start_time = time.time()

            referer = self.get_referer(file.chapter)
            novel_slug = str_format_num_alpha_only(file.chapter.novel.slug)
            chapter_slug = str_format_num_alpha_only(file.chapter.slug)
            local_path = "%s/%s" % (novel_slug, chapter_slug)
            urls = [self.full_schema_url(img_url) for img_url in file.chapter.images_content.split("\n")]

            # validate images are missing
            missing_files = []
            for idx, chapter_image in enumerate(urls):
                origin_img = hashlib.md5(chapter_image.encode()).hexdigest()
                if not file.url or (file.url_hash and origin_img not in file.url_hash):
                    missing_files.append({"index": idx, "url": chapter_image, "url_hash": origin_img})

            # compute number of downloaded url
            limit_download = 0
            if file.url:
                limit_download = len(urls)

            # get_img_time = time.time() - start_time
            # print('[process_missing_files][%s-%s] spent %s to get %s missing images'
            #       % (local_path, file.chapter.id, get_img_time, len(missing_files)))

            # Download Files to local server
            if multi_thread:
                success_files = self.download_file_to_local_multi_thread(origin_file_urls=missing_files,
                                                                         local_path=local_path,
                                                                         referer=referer, limit_image=limit_image,
                                                                         max_worker=multi_thread)
            else:
                success_files = self.download_file_to_local(origin_file_urls=missing_files,
                                                            local_path=local_path,
                                                            referer=referer, limit_image=limit_image)
            # downloaded_time = time.time() - get_img_time - start_time
            # print('[process_missing_files][%s-%s] spent %s to download %s missing images'
            #       % (local_path, file.chapter.id, downloaded_time, len(missing_files)))

            if not len(success_files):
                print('[process_missing_files][%s-%s] NO missing images uploaded' % (local_path, file.chapter.id))
                continue

            # Upload Files to CDN
            if multi_thread:
                url_hashed = self.upload_file_to_cdn_multi_thread(local_files=success_files, max_worker=multi_thread)
            else:
                url_hashed = self.upload_file_to_cdn(local_files=success_files)

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
            existed_urls = list(set(existed_urls))  # Ensure have no duplication items
            new_list = [splitext(basename(x))[0] for x in existed_urls]
            fin_list = list(zip(existed_urls, new_list))
            fin_list = [x[0] for x in sorted(fin_list, key=lambda x: int(x[1]))]
            file.url = "\n".join(fin_list) if len(fin_list) else None
            file.url_hash = ",".join(url_hashed) if len(url_hashed) else None

            if not len(fin_list):
                print('[process_missing_files][%s-%s] unable to download any missing images'
                      % (local_path, file.chapter.id))

            if len(urls) == len(fin_list):
                file.full = True
            else:
                file.full = False
                file.retry = file.retry + 1
            processed_files.append(file)
            # file.save()

            # Remove Files from local
            self.remove_path_files(novel_slug)

        if processed_files:
            CDNNovelFile.objects.bulk_update(processed_files, ['url', 'url_hash', 'full', 'retry'])

        finish_time = time.time() - init_time
        print('[process_missing_files] Finish in ', finish_time, 's')

    # For the files never running before
    def process_not_running_files(self, order_by_list=None, limit=None, multi_thread=False):
        print('[process_not_running_files] Starting...')
        if not self.cdn:
            print('[process_not_running_files] Missing cdn object...')
            print('[process_not_running_files] Finish')
            return

        init_time = time.time()

        if order_by_list and limit:
            chapters = NovelChapter.get_undownloaded_images_chapters(order_by_list=order_by_list, limit=limit)
        elif order_by_list:
            chapters = NovelChapter.get_undownloaded_images_chapters(order_by_list=order_by_list)
        elif limit:
            chapters = NovelChapter.get_undownloaded_images_chapters(limit=limit)
        else:
            chapters = NovelChapter.get_undownloaded_images_chapters()

        inserted_files = None
        with transaction.atomic():
            new_files = []
            for chapter in chapters:

                if self.is_ignored_chapter(chapter):
                    continue

                hash_origin_url = hashlib.md5(chapter.src_url.encode()).hexdigest()
                if not CDNNovelFile.objects.filter(hash_origin_url=hash_origin_url).first():
                    new_files.append(CDNNovelFile(cdn=self.cdn, chapter=chapter, type='chapter',
                                                  hash_origin_url=hash_origin_url,
                                                  url=None, full=False))

            if new_files:
                inserted_files = CDNNovelFile.objects.bulk_create(new_files, ignore_conflicts=False)

        if not inserted_files:
            print('[process_not_running_files] Unable to create inserted_files...')
            print('[process_not_running_files] Finish')
            return

        limit_image = int(os.environ.get('BACKBLAZE_LIMIT_IMG', 150))
        updated_files = []
        chapter_updated_list = []

        # batch_records = int(os.environ.get('BACKBLAZE_BATCH_RECORD_INSERT', 50))
        # Handle downloading & storing
        for chapter in chapters:
            if self.is_ignored_chapter(chapter):
                continue

            start_time = time.time()

            referer = self.get_referer(chapter)
            novel_slug = str_format_num_alpha_only(chapter.novel.slug)
            chapter_slug = str_format_num_alpha_only(chapter.slug)
            local_path = "%s/%s" % (novel_slug, chapter_slug)
            urls = []
            for idx, img_url in enumerate(chapter.images_content.split("\n")):
                full_img_url = self.full_schema_url(img_url)
                origin_img = hashlib.md5(full_img_url.encode()).hexdigest()
                url = {'index': idx, 'url': full_img_url, 'url_hash': origin_img}
                urls.append(url)

            number_urls = len(urls)

            # Download Files to local server
            if multi_thread:
                success_files = self.download_file_to_local_multi_thread(origin_file_urls=urls, local_path=local_path,
                                                                         referer=referer, limit_image=limit_image)
            else:
                success_files = self.download_file_to_local(origin_file_urls=urls, local_path=local_path,
                                                            referer=referer, limit_image=limit_image)

            # downloaded_time = time.time() - start_time
            # print('[process_not_running_files][%s-%s] spent %s to get %s images'
            #       % (local_path, chapter.id, downloaded_time, len(urls)))

            if not len(success_files):
                print('[process_missing_files][%s-%s] NO images uploaded' % (local_path, chapter.id))
                continue

            # Upload Files to CDN
            if multi_thread:
                url_hashed = self.upload_file_to_cdn_multi_thread(local_files=success_files)
            else:
                url_hashed = self.upload_file_to_cdn(local_files=success_files)

            # uploaded_time = time.time() - downloaded_time - start_time
            uploaded_time = time.time() - start_time
            print('[process_not_running_files][%s-%s] spent %s to upload %s images'
                  % (local_path, chapter.id, uploaded_time, len(success_files)))

            # Update status and url to CDNNovelFile
            sorted_success_files = sorted(success_files, key=lambda i: i['index'])
            valid_urls = []
            for sub in sorted_success_files:
                if not sub.get('url'):
                    continue
                valid_urls.append(sub.get('url').replace(settings.CDN_FILE_FOLDER, '').lstrip('/'))
            if not len(valid_urls):
                print('[process_not_running_files] Unable to get files for %s-%s/%s-%s'
                      % (chapter.novel.id, novel_slug, chapter.id, chapter_slug))
                chapter.chapter_updated = False
                chapter_updated_list.append(chapter)
                continue
            valid_urls = list(set(valid_urls))  # Ensure have no duplication items
            # we have to sort the list to make sure the images is correct ordering
            # regex map url: ^(.+\/)*(.+)\.(.+)$
            new_list = [splitext(basename(x))[0] for x in valid_urls]
            fin_list = list(zip(valid_urls, new_list))
            fin_list = [x[0] for x in sorted(fin_list, key=lambda x: int(x[1]))]
            result_url = "\n".join(fin_list) if len(fin_list) else None
            if number_urls == len(fin_list):
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
                    inserted_file.url_hash = ",".join(url_hashed) if len(url_hashed) else None
                    updated_files.append(inserted_file)
                    # inserted_file.save() ### => Do not save here

            # Remove Files from local
            self.remove_path_files(chapter.novel.slug)

        if updated_files:
            CDNNovelFile.objects.bulk_update(updated_files, ['url', 'full', 'allow_limit', 'url_hash'])

        if chapter_updated_list:
            NovelChapter.objects.bulk_update(chapter_updated_list, ['chapter_updated'])

        finish_time = time.time() - init_time
        print('[process_not_running_files] Finish in', finish_time, 's')

    def is_ignored_chapter(self, chapter):
        img_ignoring = os.environ.get('BACKBLAZE_IMG_IGNORING', '')
        # Sometimes the crawled chapter has content the wrong images,
        # we should ignore this chapter to upload to the CDN
        images_ignore = img_ignoring.split(",") if img_ignoring else []
        ignore_chapter = False
        for image_ignore in images_ignore:
            if image_ignore in chapter.images_content:
                ignore_chapter = True
                break
        return ignore_chapter


class Command(BaseCommand):

    # def __init__(self, cdn_process=None):
    #     self.cdn_process = cdn_process

    def add_arguments(self, parser):
        parser.add_argument('--order_by_list', '-o')
        parser.add_argument('-l', '--limit')
        parser.add_argument('-m', '--multi_thread')

    def handle(self, *args, **kwargs):
        print('[CDN Processing Files] Starting...')
        order_by_list = kwargs.get("order_by_list")
        multi_thread = kwargs.get("multi_thread", False)
        if multi_thread:
            multi_thread = int(multi_thread)
            if multi_thread < 1:
                multi_thread = 5  # default

        if order_by_list:
            order_by_result = []
            for orderby in order_by_list.split(","):
                order_by_result.append('-' + orderby)
            order_by_list = order_by_result
        limit = kwargs.get("limit")
        ### Test code
        # self.cdn_process.upload_file2b2("/data/cdn/novel/goong-hoang-cung/chapter-24/0.jpg",
        #                                 "goong-hoang-cung/chapter-24/0.jpg")
        active_cdn = CDNServer.get_active_cdn()
        try:
            if not active_cdn:
                print('[CDN Processing Files] Not Found any CDN Server for processing... Stopped!')
            max_thread = int(os.environ.get('BACKBLAZE_THREAD_NUM', 2))
            running_cdn = [cdn for cdn in active_cdn if cdn.status == 'running']
            if max_thread <= len(running_cdn):
                print('[CDN Processing Files] Exceed %s CDN Server for processing... Stopped!' % max_thread)
            available_cdn = [cdn for idx, cdn in enumerate(active_cdn) if
                             cdn.status == 'stopped' or idx + len(running_cdn) < max_thread]
            if not available_cdn:
                print('[CDN Processing Files] Not Found available CDN Server for processing... Stopped!')

            threads = []
            for cdn in available_cdn:
                cdn_process = CDNProcess(cdn)

                # Set status to 'running' CDN server
                cdn_process.update_status('running')

                # Create threads
                t1 = Thread(target=cdn_process.process_missing_files, args=(multi_thread,))
                t2 = Thread(target=cdn_process.process_not_running_files, args=(order_by_list, limit, multi_thread))

                # Start all threads
                t1.start()
                t2.start()

                # Append to list of threads before start them
                threads.append({'cdn_process': cdn_process, 'thread1': t1, 'thread2': t2})

            for t in threads:
                # Wait for all of them to finish
                t.get('thread1').join()
                t.get('thread2').join()

                # Set status to stop CDN server
                t.get('cdn_process').update_status('stopped')

        except Exception as e:
            print("[CDN Processing Files] Error: %s" % e)
            for cdn in active_cdn:
                cdn.last_run = datetime.now()
                cdn.status = 'stopped'
                cdn.save()

        print('[CDN Processing Files] Finish')
