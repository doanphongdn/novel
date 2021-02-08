import json
import logging

import requests
from django.http import HttpResponse, StreamingHttpResponse

from novel import settings


logger = logging.getLogger(__name__)


def url2yield(url, chunksize=1024, referer=None):
    s = requests.Session()
    if referer:
        s.headers.update({
            "Referer": referer
        })
    # Note: here i enabled the streaming
    response = s.get(url, stream=True)

    if response.status_code != 200:
        logger.warning("[url2yield][Status = %s] Unable to get image for %s with referer %s",
                       response.status_code, url, referer)

    chunk = True
    while chunk:
        chunk = response.raw.read(chunksize)

        if not chunk:
            break

        yield chunk


def stream_image(request, *args, **kwargs):
    try:
        img_hash = (kwargs.get('img') or "").strip('.jpg')
        json_str = settings.redis_image.get(img_hash)
        if json_str:
            json_str = json.loads(json_str)

            origin_url = json_str.get("origin_url", "")
            referer_url = json_str.get("referer")
            return StreamingHttpResponse(url2yield(origin_url, referer=referer_url), content_type="image/jpeg")
    except Exception as e:
        print("[stream_image] Error when parse image %s : %s" % (img_hash, e))
        import traceback
        traceback.print_exc()
    return HttpResponse({})
