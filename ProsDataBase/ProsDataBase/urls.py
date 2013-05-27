# -*- coding: UTF-8 -*-

from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from django.conf import settings


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns(
    '',
    # Examples:
    # url(r'^$', 'ProsDataBase.views.home', name='home'),
    # url(r'^ProsDataBase/', include('ProsDataBase.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    (r'^detailview/$', TemplateView.as_view(template_name="table_detailview.html")),
    (r'^createTable/$', TemplateView.as_view(template_name="createTable.html")),
    (r'^createGroup/$', TemplateView.as_view(template_name="createGroup.html")),
    (r'^groupadmin/$', TemplateView.as_view(template_name="groupadmin.html")),
    (r'^table/$', TemplateView.as_view(template_name="table_overview.html")),
    (r'^register/$', TemplateView.as_view(template_name="register.html")),
    (r'^/$', TemplateView.as_view(template_name="login.html")),
    url(regex=r'^dataset/(?P<table_id>\w+)/$',
        view='database.views.frontend.insertDataset'),

    # APIs for table requests
    (r'^api/table/$', "database.views.api.table"),
    (r'^api/table/all/$', "database.views.api.showAllTables"),
    (r'^api/table/dataset/$', "database.views.api.insertData"),
    (r'^api/table/dataset/(?P<datasetID>[\d]+)/$', "database.views.api.modifyData"),
    # must come after other uris of the form api/table/[string], or they will match
    (r'^api/table/(?P<name>[\w]+)/$', "database.views.api.showTable"),
    (r'^api/table/(?P<name>[\w]+)/structure/$', "database.views.api.tableStructure"),

    (r'^api/user/$', "database.views.api.showAllUsers"),
    (r'^api/group/$', "database.views.api.showAllGroups"),


)

if settings.DEBUG:
    #noinspection PyAugmentAssignment
    urlpatterns = patterns('',
                           url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
                               'document_root': settings.STATIC_ROOT,
                               }),
                           url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
                               'document_root': settings.MEDIA_ROOT,
                               }),
                           ) + urlpatterns

