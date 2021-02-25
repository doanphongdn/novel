from rest_framework import serializers


# Novel List Schema
class NovelSerializer(serializers.Serializer):
    name = serializers.CharField()
    url = serializers.CharField()
    latest_chapter_url = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    thumbnail_image = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class NovelListCampaignSchema(serializers.Serializer):
    src_url = serializers.CharField()
    src_campaign = serializers.CharField()
    novel_block = NovelSerializer(many=True)


# Novel Info Schema
class NovelInfoChapterListSerializer(serializers.Serializer):
    chapter_name = serializers.CharField()
    chapter_url = serializers.CharField()


class NovelInfoCampaignSchema(serializers.Serializer):
    src_url = serializers.CharField()
    name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    thumbnail_image = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    status = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    authors = serializers.ListField(required=False, allow_empty=True, allow_null=True)
    genres = serializers.ListField(required=False, allow_empty=True, allow_null=True)
    descriptions = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    list_chapter = NovelInfoChapterListSerializer(many=True, required=True, allow_null=True)


# Novel Chapter Schema
class NovelChapterCampaignSchema(serializers.Serializer):
    src_url = serializers.CharField()
    content_text = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    content_images = serializers.ListField(required=False, allow_empty=True, allow_null=True)
