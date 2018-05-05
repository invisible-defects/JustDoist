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
from django.urls import path
from django.contrib.auth import views as dj_views
from main import views


urlpatterns = [
    path('admin/', admin.site.urls),

    url(r'^login/$', dj_views.login, {'template_name': 'login.html'}),
    url(r'^logout/$', dj_views.logout_then_login, name="logout"),

    path('', views.index),
    path('index', views.index, name='index'),
    path('register', views.Register.as_view(), name='register'),
    path('link/<slug:service>/', views.link, name='link'),
    path('authorize/<slug:provider>/', views.authorize),
    path('callback/<slug:provider>/', views.oauth_callback),
    path('profile/<slug:data>/', views.profile, name="profile"),
    path('settings', views.settings),
    path('contact_us', views.contact_us),
    path('problem', views.problem),
    path('add_task', views.add_task),
    path('statistics', views.statistics),
]

urlpatterns += staticfiles_urlpatterns()
