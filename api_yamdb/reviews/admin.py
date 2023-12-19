from django.contrib import admin

from reviews.models import CustomUser, Review, Title


admin.site.register(CustomUser)
admin.site.register(Review)
admin.site.register(Title)
