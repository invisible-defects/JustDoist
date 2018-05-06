"""justdoist URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.defaults import page_not_found
from django.urls import path
from django.contrib.auth import views as dj_views

from main import views


urlpatterns = [
    path('admin/', admin.site.urls),

    url(r'^login/$', dj_views.login, {'template_name': 'login.html'}),
    url(r'^logout/$', dj_views.logout_then_login, name="logout"),


    path('', views.main_route, name="main_routed"),
    path('index', views.index, name='index'),
    path('landingpage', views.landingpage, name="landingpage"),
    path('register', views.Register.as_view(), name='register'),

    path('link/<slug:service>/', views.link, name='link'),
    path('authorize/<slug:provider>/', views.authorize),
    path('callback/<slug:provider>/', views.oauth_callback),
    path('progress/<slug:data>/', views.progress, name="progress"),
    path('progress/', views.default_progress, name="default_progress"),
    path('color', views.change_color),

    path('payments', views.payments, name="payments"),
    path('checkout/<slug:kind>', views.checkout, name="checkout"),
    path('failure', views.failure, name="failure"),
    path('success', views.success, name="success"),

    path('settings', views.settings),
    path('contact_us', views.contact_us),
    path('problem', views.problem),
    path('add_task', views.add_task),
    path('statistics', views.statistics),
]

urlpatterns += staticfiles_urlpatterns()

handler404 = 'main.views.handler404'
handler500 = handler404
