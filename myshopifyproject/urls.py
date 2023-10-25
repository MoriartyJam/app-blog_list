"""myshopifyproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from shopifyapp import views
from graphene_django.views import GraphQLView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('install', views.install_app, name='install'),
    path('shopify/oauth/callback/', views.oauth_callback, name='oauth_callback'),
    path('product_list',  views.product_list, name='product_list'),
    path('shopify-blogs', views.display_shopify_blogs, name='shopify_blogs'),
    path('shopify-articles', views.display_shopify_articles, name='shopify_articles'),
    path('shopify-content', views.display_shopify_content, name='shopify_content'),
    path('get-products', views.get_products, name='fetch_products'),
    path('get-blogs', views.serialize_shopify_data, name='get-blogs'),
    path('send_data_to_shopify',  views.send_data_to_shopify, name='send-data_to_shopify'),
    path('send_content_to_shopify',  views.send_content_to_shopify, name='send-content_to_shopify'),
    path('display_data', views.display_shopify_data, name='display_shopify_data'),
    path('fetch-shopify-data/', views.fetch_and_save_shopify_data, name='fetch_shopify_data'),
    path('fetch-data/', views.fetch_shopify_data, name='fetch_data'),

]
