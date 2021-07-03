import datetime
import json
import logging
import os
import re
from json import JSONEncoder
from os.path import basename, splitext
from urllib.parse import urlparse

import requests
from django.templatetags.static import static
from django_backblaze_b2 import BackblazeB2Storage

from django_cms import settings
from django_cms.models import CDNServer


logger = logging.getLogger(__name__)


def is_json(json_str):
    try:
        json_object = json.loads(json_str.decode("utf-8").replace("\'", "\""))
    except ValueError as e:
        return False
    return json_object


def sort_images(existed_urls, domain=''):
    # we have to sort the list to make sure the images is correct ordering
    # regex map url: ^(.+\/)*(.+)\.(.+)$
    existed_urls = list(set(existed_urls))  # Ensure have no duplication items
    new_list = []
    new_list_int = []
    for x in existed_urls:
        if not x:
            continue
        val = splitext(basename(x))[0]
        new_list.append(val)
        new_list_int.append(int(val))
    fin_list = list(zip(existed_urls, new_list))
    fin_list = {x[1]: domain + x[0] for x in sorted(fin_list, key=lambda x: int(x[1]))}
    new_list_int.sort()
    # missing_index = [x for x in range(0, new_list_int[-1] + 1) if x not in new_list_int]
    dict_images = {}
    # from sorted list, just check index is valid and push to reason position
    for x in range(0, new_list_int[-1] + 1):
        if x not in new_list_int:
            dict_images[x] = None  # missing image
        else:
            dict_images[x] = fin_list.get(str(x))  # image from cdn

    return dict_images


def get_history_cookies(request):
    # Get chapter ids from cookie
    try:
        histories = json.loads(request.COOKIES.get('_histories'))
    except:
        histories = {}

    return histories if isinstance(histories, dict) else {}


def download_image(source, target_file, referer=None):
    headers = {}
    if referer:
        headers.update({"Referer": referer})
    try:
        _, ext = os.path.splitext(source)
        target_file = "%s%s" % (target_file, ext or '.jpg')
        target = "%s/%s" % (settings.NOVEL_STATIC_IMAGE_PATH, target_file)
        image = requests.get(source, headers=headers, timeout=5)
        if image.status_code == 200:
            with open(target, 'wb') as f:
                f.write(image.content)
                return static("%s/%s" % (settings.NOVEL_STATIC_IMAGE_FOLDER, target_file))
    except:
        pass

    return None


def str_format_num_alpha_only(s):
    # Remove All Characters Except the Alphabets and the Numbers From a String
    return re.sub("[^A-Za-z0-9-]", "-", s)


def get_short_url(url):
    # urlparse('http://www.cwi.nl:80/%7Eguido/Python.html')
    # Get scheme='http', netloc='www.cwi.nl:80', path='/%7Eguido/Python.html'
    parsed_url = urlparse(url)
    return parsed_url.scheme + "://" + parsed_url.netloc + parsed_url.path


def get_referer(chapter):
    origin_domain = urlparse(chapter.src_url) if chapter.src_url else None
    referer = origin_domain.scheme + "://" + origin_domain.netloc if origin_domain else None
    return referer


def full_schema_url(url, origin_domain=None):
    if url.strip().startswith('//'):
        url = "http:" + url
    elif url.strip().startswith('/'):
        if origin_domain:
            url = origin_domain.strip('/ ') + url
    else:
        url = url.rstrip('/ ')

    return url


def upload_file2b2(file_path, b2_file_name, bucket_name='nettruyen', cdn_number=0):
    active_cdn = CDNServer.get_active_cdn()
    if not active_cdn:
        return None
    cdn = active_cdn[cdn_number]
    b2 = BackblazeB2Storage(opts={'bucket': cdn.name, 'allowFileOverwrites': True})
    if not b2:
        return None
    if not b2.bucket:
        b2.bucket.name = bucket_name
    try:
        cdn_url = cdn.friendly_alias_url or cdn.friendly_url or cdn.s3_url
        file_info = b2.exists(b2_file_name)
        if file_info:
            return cdn_url + file_info.file_name

        uploaded_file = b2.bucket.upload_local_file(file_path, b2_file_name)
        if not uploaded_file:
            return None

        return cdn_url + uploaded_file.file_name
    except Exception as e:
        return None


def remove_b2_files(b2_file_name, bucket_name='nettruyen', cdn_number=0):
    """
    b2_file_name should be a file path or folder path
    """
    active_cdn = CDNServer.get_active_cdn()
    if not active_cdn:
        return
    cdn = active_cdn[cdn_number]
    b2 = BackblazeB2Storage(opts={'bucket': cdn.name, 'allowFileOverwrites': True})
    if not b2:
        return
    if not b2.bucket:
        b2.bucket.name = bucket_name
    try:
        b2.delete(b2_file_name)
    except Exception as e:
        logger.exception(e)


def get_first_number_pattern(string, pattern='Chapter '):
    if pattern != 'Chapter':
        pattern = '(' + pattern + '|Chapter)([a-zA-Z ])*'
    else:
        pattern = '(' + pattern + ')([a-zA-Z ])*'
    regex = re.compile(r'^' + pattern + '([0-9.]*)')
    result = regex.findall(string)
    if result:
        # Get the second group from the result, such as:
        return result[0][2].rstrip(".")
    else:
        return None


# subclass JSONEncoder
class DateTimeEncoder(JSONEncoder):
    # Override the default method
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
