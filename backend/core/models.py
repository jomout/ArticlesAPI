from django.db import models
from django.conf import settings

class Author(models.Model):
    """
    Represents an author of articles.
    """
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class Tag(models.Model):
    """
    Represents a tag associated with articles.
    """
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Article(models.Model):
    """
    Represents an article written by an author.
    """
    id = models.BigAutoField(primary_key=True)
    identifier = models.CharField(max_length=64, unique=True)
    publication_date = models.DateField()
    title = models.CharField(max_length=300)
    abstract = models.TextField(blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="articles"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-publication_date", "-created_at"]

    def __str__(self):
        return f"{self.identifier} | {self.title}"


class Comment(models.Model):
    """
    Represents a comment made on an article.
    """
    id = models.BigAutoField(primary_key=True)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments")
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        

class Authorship(models.Model):
    """
    Explicit join table for Article - Author
    """
    id = models.BigAutoField(primary_key=True)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="authorships")
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="authorships")

    class Meta:
        unique_together = ("article", "author")
        

class ArticleTag(models.Model):
    """
    Explicit join table for Article - Tag
    """
    id = models.BigAutoField(primary_key=True)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="articletags")
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name="articletags")

    class Meta:
        unique_together = ("article", "tag")
