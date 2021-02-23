from rest_framework import serializers

# Novel List Schema
class NovelSerializer(serializers.Serializer):
    name = serializers.CharField()
    url = serializers.CharField()
    latest_chapter_url = serializers.CharField(required=False)
    thumbnail_image = serializers.CharField(required=False)


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
    name = serializers.CharField(required=False)
    thumbnail_image = serializers.CharField(required=False)
    status = serializers.CharField(required=False)
    authors = serializers.ListField(required=False)
    genres = serializers.ListField(required=False)
    descriptions = serializers.CharField(required=False)
    list_chapter = NovelInfoChapterListSerializer(many=True, required=False)


# Novel Chapter Schema
class NovelChapterCampaignSchema(serializers.Serializer):
    src_url = serializers.CharField()
    content_text = serializers.CharField(required=False)
    content_images = serializers.ListField(required=False)
