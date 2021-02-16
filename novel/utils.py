from os.path import basename, splitext

import json
from django.db.models.signals import pre_save
from django.dispatch import receiver

from novel.models import Novel
n(json_str):
    try:
        json_object = json.loads(json_str.decode("utf-8").replace("\'", "\""))
    except ValueError as e:
        return False
    return json_object


def sort_images(existed_urls):
    # we have to sort the list to make sure the images is correct ordering
    # regex map url: ^(.+\/)*(.+)\.(.+)$
    existed_urls = list(set(existed_urls))  # Ensure have no duplication items
    new_list = [splitext(basename(x))[0] for x in existed_urls]
    fin_list = list(zip(existed_urls, new_list))
    fin_list = [x[0] for x in sorted(fin_list, key=lambda x: int(x[1]))]
    return fin_list
