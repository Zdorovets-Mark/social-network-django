"""
URL configuration for my_diplom project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from backend.views import (CommentViewSet, PublicationViewSet, UserLoginView,
                           UserRegistrationView, home_view)

urlpatterns = [
    path("", home_view, name="home"),
    path("admin/", admin.site.urls),
    path("api/auth/register/", UserRegistrationView.as_view(), name="register"),
    path("api/auth/login/", UserLoginView.as_view(), name="login"),
    path(
        "api/publications/",
        PublicationViewSet.as_view({"get": "list", "post": "create"}),
    ),
    path(
        "api/publications/<int:pk>/",
        PublicationViewSet.as_view(
            {"get": "retrieve", "put": "update", "delete": "destroy"}
        ),
    ),
    path(
        "api/publications/<int:pk>/like/", PublicationViewSet.as_view({"post": "like"})
    ),
    path(
        "api/publications/<int:publication_pk>/comments/",
        CommentViewSet.as_view({"get": "list", "post": "create"}),
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
