from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

#api_query_pattern = patterns(url(r'^api/test$','ApolloSite.views.api.query.test'))
api_group = [
        (r'test','test'),
        (r'homepage','homepage'),
        (r'q','query')
    ]
api_query_pattern = patterns('ApolloSite.views.api.query',*api_group)
default_pattern = patterns('',
    # Examples:
    # url(r'^$', 'ApolloSite.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns = default_pattern+api_query_pattern
