from django.contrib import admin

from reviews.models import CustomUser, Review, Title, Category, Genre, GenreTitle, Comment


admin.site.register(CustomUser)
admin.site.register(Review)
admin.site.register(Title)
admin.site.register(Category)
admin.site.register(Genre)
admin.site.register(GenreTitle)
admin.site.register(Comment)
