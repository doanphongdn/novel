from novel.views.includes.base import BaseTemplateInclude


class UserProfileTemplateInclude(BaseTemplateInclude):
    cache = False
    name = "user_profile"
    template = "novel/includes/user_profile.html"
