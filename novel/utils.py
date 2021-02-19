import json
from os.path import basename, splitext


def is_json(json_str):
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


def get_history_cookies(request):
    # Get chapter ids from cookie
    try:
        histories = json.loads(request.COOKIES.get('_histories'))
    except:
        histories = {}

    return histories if isinstance(histories, dict) else {}
