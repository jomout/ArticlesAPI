from rest_framework import viewsets, permissions, decorators
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.http import HttpResponse
import csv
from io import StringIO

from .models import Article, Comment, Author, Tag
from .serializers import (
    ArticleSerializer,
    CommentSerializer,
    AuthorSerializer,
    TagSerializer,
)
from .permissions import IsOwnerOrReadOnly, IsCommentOwnerOrReadOnly, ReadOnly
from .filters import ArticleFilter


class ArticleViewSet(viewsets.ModelViewSet):
    """
    CRUD for Articles.
    - Filterable by year, month, author, tag, keyword
    - Only creator can update/delete
    - CSV export available at /articles/export/
    """
    queryset = Article.objects.all().prefetch_related(
        "authorships__author", "articletags__tag"
    )
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filterset_class = ArticleFilter
    search_fields = ["title", "abstract"]
    ordering_fields = ["publication_date", "created_at", "identifier", "title"]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        if self.get_object().created_by != self.request.user:
            raise PermissionDenied("You can only update your own articles.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.created_by != self.request.user:
            raise PermissionDenied("You can only delete your own articles.")
        instance.delete()

    @decorators.action(detail=False, methods=["get"])
    def export(self, request):
        """
        CSV export of filtered or specific articles.
        Example:
        - /api/articles/export/?ids=ART-001,ART-002
        - /api/articles/export/?year=2024&tag=AI
        """
        ids = request.query_params.get("ids")
        qs = self.filter_queryset(self.get_queryset())
        if ids:
            id_list = [i.strip() for i in ids.split(",") if i.strip()]
            qs = qs.filter(identifier__in=id_list)

        f = StringIO()
        writer = csv.writer(f)
        writer.writerow(["identifier", "publication_date", "title", "abstract", "authors", "tags"])

        for article in qs:
            authors = ", ".join([a.author.name for a in article.authorships.all()])
            tags = ", ".join([t.tag.name for t in article.articletags.all()])
            writer.writerow([article.identifier, article.publication_date, article.title, article.abstract, authors, tags])

        response = HttpResponse(f.getvalue(), content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename=articles.csv"
        return response


class CommentViewSet(viewsets.ModelViewSet):
    """
    CRUD for Comments.
    - Only comment owner can update/delete
    """
    queryset = Comment.objects.select_related("article", "author")
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsCommentOwnerOrReadOnly]
    ordering_fields = ["created_at"]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        if self.get_object().author != self.request.user:
            raise PermissionDenied("You can only update your own comments.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied("You can only delete your own comments.")
        instance.delete()


# Optional: expose authors and tags as read-only
class AuthorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [ReadOnly]


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [ReadOnly]
