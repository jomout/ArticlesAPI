from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Article, Author, Tag, Comment, Authorship, ArticleTag

User = get_user_model()


class AuthorSerializer(serializers.ModelSerializer):
    """
    Serializer for Author model.
    """
    class Meta:
        model = Author
        fields = ["id", "name"]


class TagSerializer(serializers.ModelSerializer):
    """
    Serializer for Tag model.
    """
    class Meta:
        model = Tag
        fields = ["id", "name"]


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for Comment model.
    - Shows author's username
    - Accepts article by ID
    """
    author = serializers.ReadOnlyField(source="author.username")   # show username
    article_id = serializers.PrimaryKeyRelatedField(
        source="article", queryset=Article.objects.all(), write_only=True
    )

    class Meta:
        model = Comment
        fields = ["id", "article_id", "author", "body", "created_at", "updated_at"]
        read_only_fields = ["id", "author", "created_at", "updated_at"]


class ArticleSerializer(serializers.ModelSerializer):
    """
    Serializer for Article with manual join tables.
    - Accepts authors as list of names (write-only)
    - Accepts tags as list of names (write-only)
    - Expands authors/tags details when reading
    """
    authors = serializers.ListField(
        child=serializers.CharField(), write_only=True, required=False
    )
    tags = serializers.ListField(
        child=serializers.CharField(), write_only=True, required=False
    )

    authors_detail = serializers.SerializerMethodField()
    tags_detail = serializers.SerializerMethodField()
    created_by = serializers.ReadOnlyField(source="created_by.username")

    class Meta:
        model = Article
        fields = [
            "id",
            "identifier",
            "publication_date",
            "title",
            "abstract",
            "authors",        # write-only
            "tags",           # write-only
            "authors_detail", # read-only
            "tags_detail",    # read-only
            "created_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "authors_detail",
            "tags_detail",
            "created_by",
            "created_at",
            "updated_at",
        ]

    # ---- helpers for join tables ----
    def get_authors_detail(self, obj):
        return AuthorSerializer(
            [a.author for a in obj.authorships.select_related("author")],
            many=True
        ).data

    def get_tags_detail(self, obj):
        return TagSerializer(
            [t.tag for t in obj.articletags.select_related("tag")],
            many=True
        ).data

    def _get_or_create(self, names, ModelClass):
        objs = []
        for n in (names or []):
            obj, _ = ModelClass.objects.get_or_create(name=n.strip())
            objs.append(obj)
        return objs

    # CREATE METHOD
    def create(self, validated_data):
        author_names = validated_data.pop("authors", [])
        tag_names = validated_data.pop("tags", [])

        article = Article.objects.create(**validated_data)

        for author in self._get_or_create(author_names, Author):
            Authorship.objects.get_or_create(article=article, author=author)

        for tag in self._get_or_create(tag_names, Tag):
            ArticleTag.objects.get_or_create(article=article, tag=tag)

        return article

    # UPDATE METHOD
    def update(self, instance, validated_data):
        author_names = validated_data.pop("authors", None)
        tag_names = validated_data.pop("tags", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if author_names is not None:
            instance.authorships.all().delete()
            for author in self._get_or_create(author_names, Author):
                Authorship.objects.get_or_create(article=instance, author=author)

        if tag_names is not None:
            instance.articletags.all().delete()
            for tag in self._get_or_create(tag_names, Tag):
                ArticleTag.objects.get_or_create(article=instance, tag=tag)

        return instance

