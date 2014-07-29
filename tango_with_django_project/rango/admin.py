from django.contrib import admin
from rango.models import Category, Page, UserProfile


# tell Django what models we wish to make available to the admin interface
admin.site.register(Category)
admin.site.register(Page)
admin.site.register(UserProfile)
