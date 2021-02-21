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
    new_list = []
    new_list_int = []
    for x in existed_urls:
        val = splitext(basename(x))[0]
        new_list.append(val)
        new_list_int.append(int(val))
    new_list_int.sort()
    missing_index = [x for x in range(0, new_list_int[-1] + 1) if x not in new_list_int]
    fin_list = list(zip(existed_urls, new_list))
    fin_list = [x[0] for x in sorted(fin_list, key=lambda x: int(x[1]))]
    return fin_list, missing_index


def get_history_cookies(request):
    # Get chapter ids from cookie
    try:
        histories = json.loads(request.COOKIES.get('_histories'))
    except:
        histories = {}

    return histories if isinstance(histories, dict) else {}
