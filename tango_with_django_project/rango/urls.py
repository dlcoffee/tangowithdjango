from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin 
from rango import views


admin.autodiscover()


urlpatterns = patterns('',
        url(r'^$', views.index, name='index'),
        url(r'^about', views.about, name='about'),
        url(r'^category/(?P<category_name_url>\w+)/$', views.category, name='category'),
        url(r'^admin/', include(admin.site.urls))
        )



if settings.DEBUG:
        urlpatterns += patterns(
                'django.views.static',
                (r'media/(?P<path>.*)',
                'serve',
                {'document_root': settings.MEDIA_ROOT}), )


