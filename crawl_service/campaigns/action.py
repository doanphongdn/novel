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
        for f in fields:
            data = obj.get(f)
            if isinstance(data, list):
                data = "<p>%s</p>" % "</p><p>".join(txt.strip("\n ") for txt in data if txt.strip("\n "))
                obj[f] = data

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
