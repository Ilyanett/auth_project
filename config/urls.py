"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from users.views import RegisterView, LoginView, ProfileView, DeleteAccountView, LogoutView
from access_control.views import (
    OrdersView, ProductsView,
    AdminAccessRulesView, AdminUsersView
)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/register/', RegisterView.as_view()),
    path('api/login/', LoginView.as_view()),
    path('api/logout/', LogoutView.as_view()),
    path('api/profile/', ProfileView.as_view()),
    path('api/profile/delete/', DeleteAccountView.as_view()),

    path('api/orders/', OrdersView.as_view()),
    path('api/products/', ProductsView.as_view()),

    path('api/admin/rules/', AdminAccessRulesView.as_view()),
    path('api/admin/users/', AdminUsersView.as_view()),
]
