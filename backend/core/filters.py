import django_filters as df
from .models import Article


class ArticleFilter(df.FilterSet):
    year = df.NumberFilter(field_name="publication_date", lookup_expr="year")
    month = df.NumberFilter(field_name="publication_date", lookup_expr="month")
    author = df.CharFilter(method="filter_author")
    tag = df.CharFilter(method="filter_tag")
    keyword = df.CharFilter(method="filter_keyword")

    def filter_author(self, qs, name, value):
        names = [v.strip() for v in value.split(",") if v.strip()]
        if names:
            qs = qs.filter(authorships__author__name__in=names)
        return qs.distinct()

    def filter_tag(self, qs, name, value):
        names = [v.strip() for v in value.split(",") if v.strip()]
        if names:
            qs = qs.filter(articletags__tag__name__in=names)
        return qs.distinct()

    def filter_keyword(self, qs, name, value):
        if value:
            qs = qs.filter(title__icontains=value) | qs.filter(abstract__icontains=value)
        return qs

    class Meta:
        model = Article
        fields = ["year", "month", "author", "tag", "keyword"]
