from django.contrib import admin

from reviews.models import Category, Comment, CustomUser, Genre, Review, Title


MAX_DISPLAY_LENGTH = 50


class GenreAdmin(admin.ModelAdmin):
    list_display_links = ("name",)
    list_display = ("name", "slug")
    search_fields = ("name",)


class TitleInline(admin.StackedInline):
    model = Title.genre.through
    extra = 0


class TitleAdmin(admin.ModelAdmin):
    filter_horizontal = ("genre",)
    inlines = (TitleInline,)
    list_display_links = ("name",)
    list_display = ("name", "year", "category")
    list_editable = ("category",)
    list_filter = (
        "category",
        "year",
    )
    search_fields = ("name",)


class CustomUserAdmin(admin.ModelAdmin):
    list_display_links = ("username",)
    list_display = ("username", "first_name", "last_name", "email", "role")
    list_editable = ("role",)
    list_filter = ("role",)
    search_fields = ("username", "first_name", "last_name", "email")


@admin.display(description="Текст отзыва")
def get_short_text(obj):
    return obj.text[:MAX_DISPLAY_LENGTH] + "..."


class ReviewAdmin(admin.ModelAdmin):
    list_display_links = (get_short_text,)
    list_display = (get_short_text, "author", "score", "title")
    list_filter = (
        "author",
        "score",
        "title",
    )
    search_fields = (
        get_short_text,
        "author",
        "title",
    )


class CategorAdmin(admin.ModelAdmin):
    list_display_links = ("name",)
    list_display = ("name", "slug")
    search_fields = ("name",)


class CommentAdmin(admin.ModelAdmin):
    list_display_links = ("text",)
    list_display = ("text", "author", get_short_text)
    list_filter = ("author",)
    search_fields = (
        "text",
        "author",
        get_short_text,
    )


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Title, TitleAdmin)
admin.site.register(Category, CategorAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Comment, CommentAdmin)
