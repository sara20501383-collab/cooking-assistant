from django.contrib import admin
from django.urls import path
from kitchen import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.find_recipe, name='find_recipe'),
    path('menu/', views.menu, name='menu'),
]
