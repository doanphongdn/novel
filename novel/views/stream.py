import json

import requests
from django.http import HttpResponse, StreamingHttpResponse

from novel import settings


def url2yield(url, chunksize=1024, referer=None):
    s = requests.Session()
    if referer:
        s.headers.update({
            "Referer": referer
        })
    # Note: here i enabled the streaming
    response = s.get(url, stream=True)

    chunk = True
    while chunk:
        chunk = response.raw.read(chunksize)

        if not chunk:
            break

        yield chunk


def stream_image(request, *args, **kwargs):
    img_hash = (kwargs.get('img') or "").strip('.jpg')
    json_str = settings.redis_image.get(img_hash)
    if json_str:
        try:
            json_str = json.loads(json_str)
        except:
            return HttpResponse({})

        origin_url = json_str.get("origin_url", "")
        referer_url = json_str.get("referer")
        return StreamingHttpResponse(url2yield(origin_url, referer=referer_url), content_type="image/jpeg")

    return HttpResponse({})
