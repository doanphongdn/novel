import errno
import os
import re

import requests
from PIL import Image
from django.core.exceptions import ValidationError
from django.templatetags.static import static

from crawl_service import settings


def code_validate(value):
    reg = re.compile(r'^[a-zA-Z0-9_]+$')
    if not reg.match(value):
        raise ValidationError(u'<%s> must be character, number or underline' % value)


def download_image(source, target_file, referer=None):
    headers = {}
    if referer:
        headers.update({"Referer": referer})
    try:
        _, ext = os.path.splitext(source)
        target_file = "%s%s" % (target_file, ext)
        target = "%s/%s" % (settings.NOVEL_STATIC_IMAGE_PATH, target_file)
        image = requests.get(source, headers=headers, timeout=5)
        if image.status_code == 200:
            with open(target, 'wb') as f:
                f.write(image.content)
                return static("%s/%s" % (settings.NOVEL_STATIC_IMAGE_FOLDER, target_file))
    except:
        pass

    return None


# Taken from https://stackoverflow.com/a/600612/119527
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def safe_open_w(path):
    ''' Open "path" for writing, creating any parent directories as needed.
    '''
    mkdir_p(os.path.dirname(path))
    return open(path, 'wb')


def download_cdn_file(source, target_file, ext=None, referer=None):
    headers = {}
    if referer:
        headers.update({"Referer": referer})
    try:
        if not ext:
            _, ext = os.path.splitext(source)
        target_file = "%s%s" % (target_file, ext)
        target_dir = "%s/%s" % (settings.CDN_FILE_FOLDER, target_file)
        file_request = requests.get(source, headers=headers, timeout=5)
        if file_request.status_code == 200:
            # with open(target_dir, 'wb') as f:
            with safe_open_w(target_dir) as f:
                f.write(file_request.content)
                return "%s/%s" % (settings.CDN_FILE_FOLDER, target_file)
    except Exception as e:
        print("[download_cdn_file] Error: %s : %s" % (source, e))

    return None


def image_processing(image):
    '''
    Optimize images
    '''
    # Image ratio
    baseheight = 500
    temp = settings.CDN_FILE_FOLDER + '/temp.jpg'
    os.rename(image, temp)
    img = Image.open(temp)
    hpercent = (baseheight / float(img.size[1]))
    wsize = int((float(img.size[0]) * float(hpercent)))
    img = img.resize((wsize, baseheight), Image.ANTIALIAS)
    rgb_im = img.convert('RGB')
    rgb_im.save(image, optimize=True, quality=95)


def upload_file_to_b2(file_path, b2_file_name, bucket_name='nettruyen'):
    # Ref: https://www.backblaze.com/b2/docs/quick_command_line.html
    # b2 upload-file <bucket name> <file path> <folder/file name on backblaze>
    os.system(
        ".venv/bin/b2 upload-file " + bucket_name + " \"" + file_path + "\" \"" + b2_file_name + "\"  >> upload.log 2>&1")
    os.system("mv \"" + file_path + "\" " + settings.CDN_FILE_FOLDER + "/done/ >> upload.log 2>&1")
