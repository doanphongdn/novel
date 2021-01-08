from html2text import HTML2Text
from mistletoe import markdown

from crawl_service.campaigns.base import BaseAction


class ReverseAction(BaseAction):
    name = 'Reverse Chapter List'

    @classmethod
    def handle(cls, obj, *args, **kwargs):
        super().handle(obj)
        fields = kwargs.get("fields") or []
        for f in fields:
            data = obj.get(f)
            if isinstance(data, list):
                data.reverse()

        return obj


class FormatChapterContent(BaseAction):
    name = "Format Chapter Content"

    @classmethod
    def handle(cls, obj, *args, **kwargs):
        super().handle(obj, *args, **kwargs)
        fields = kwargs.get("fields") or []
        replaces = kwargs.get("replaces") or []

        for f in fields:
            data = obj.get(f)
            if isinstance(data, list):
                # Get full html
                full_html = "".join(data)

                # Convert to markdown
                htmlobj = HTML2Text()
                htmlobj.ignore_links = True
                htmlobj.ignore_images = True
                htmlobj.skip_internal_links = True
                htmlobj.ignore_emphasis = True
                htmlobj.body_width = 500

                md = htmlobj.handle(full_html)
                for rep in replaces:
                    if isinstance(rep, list) and len(rep) >= 2:
                        md = md.replace(rep[0], rep[1])

                # Remove duplicate breakline
                md = "<p>%s</p>" % "</p><p>".join(txt.strip() for txt in md.split("\n") if txt.strip())

                # Final html
                obj[f] = markdown(md)

        return obj


class GroupItem(BaseAction):
    name = "Group Items"

    @classmethod
    def handle(cls, obj, *args, **kwargs):
        super().handle(obj, *args, **kwargs)

        fields = kwargs.get("fields") or []
        name = kwargs.get("name")

        group_values = [obj.pop(f) for f in fields]
        res_data = []
        for val in zip(*group_values):
            dict_val = {}
            for i in range(len(fields)):
                dict_val[fields[i]] = val[i]
            res_data.append(dict_val)

        obj[name] = res_data

        return obj


class JoinItem(BaseAction):
    name = "Join Items"

    @classmethod
    def handle(cls, obj, *args, **kwargs):
        super().handle(obj, *args, **kwargs)

        fields = kwargs.get("fields") or []
        name = kwargs.get("name")
        sperator = kwargs.get("sperator") or ' '

        group_values = [obj.pop(f) for f in fields]
        res_data = []
        for val in zip(*group_values):
            str_arr = []
            for i in range(len(fields)):
                str_arr.append(val[i])

            res_data.append(sperator.join(str_arr))

        obj[name] = res_data

        return obj
    # return "<p>%s</p>" % "</p><p>".join(txt.strip("\n ") for txt in obj if txt.strip("\n "))
