from django.contrib import admin

from reviews.models import CustomUser, Review, Title, Category, Genre, GenreTitle, Comment


class TitleAdmin(admin.ModelAdmin):
    filter_horizontal = ('genre',)
    list_display = (
        'name',
        'year',
        'description',
        # 'genre',
        'category'
    )
    list_editable = (
        'year',
        'description',
        'category'
    )
    search_fields = ('name',)
    list_filter = ('category', 'year',)
    list_display_links = ('name',)
    # empty_value_display = 'Не задано'


admin.site.register(CustomUser)
admin.site.register(Review)
admin.site.register(Title, TitleAdmin)
admin.site.register(Category)
admin.site.register(Genre)
admin.site.register(GenreTitle)
admin.site.register(Comment)
