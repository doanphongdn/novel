import os
import re

import requests
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
