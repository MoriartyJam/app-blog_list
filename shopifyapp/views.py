from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
import requests
from .models import ShopifyProduct, ShopifyBlog, ShopifyArticle
from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
import json


def install_app(request):
    shop = request.GET.get("shop", 'junior-state.myshopify.com')
    scope = 'read_products write_products read_content write_content write_themes read_themes'
    redirect_uri = request.build_absolute_uri('shopify/oauth/callback/')
    authorization_url = f'https://{shop}/admin/oauth/authorize?client_id={settings.SHOPIFY_API_KEY}&scope={scope}&redirect_uri={redirect_uri}'
    return redirect(authorization_url)


def oauth_callback(request):
    code = request.GET.get('code')
    shop = request.GET.get('shop')

    token_url = f'https://{shop}/admin/oauth/access_token'
    data = {
        'client_id': settings.SHOPIFY_API_KEY,
        'client_secret': settings.SHOPIFY_API_SECRET,
        'code': code,
    }
    response = requests.post(token_url, json=data)

    if response.status_code == 200:
        access_token = response.json().get('access_token')
        request.session['shopify_access_token'] = access_token
        messages.success(request, 'Authentication successful.')
        return redirect('get-blogs')
    else:
        messages.error(request, 'Authentication failed.')
        return redirect('install')


def fetch_shopify_data(request):
    # Replace with your Shopify store's URL
    shop_url = 'junior-state.myshopify.com'

    # Replace with your Shopify access token
    access_token = request.session.get('shopify_access_token')

    # Fetch blogs from Shopify
    response = requests.get(f'https://{shop_url}/admin/api/2023-01/blogs.json',
                            headers={'X-Shopify-Access-Token': access_token})
    blogs_data = response.json().get('blogs', [])

    for blog_data in blogs_data:
        # Create or update the blog in the database
        blog, created = ShopifyBlog.objects.get_or_create(title=blog_data.get('title', ''))

        # Fetch articles for the blog
        response = requests.get(f'https://{shop_url}/admin/api/2023-01/blogs/{blog_data["id"]}/articles.json',
                                headers={'X-Shopify-Access-Token': access_token})
        articles_data = response.json().get('articles', [])

        for article_data in articles_data:
            # Create or update articles for the blog
            ShopifyArticle.objects.update_or_create(
                title=article_data.get('title', ''),
                body_html=article_data.get('body_html', ''),
                blog=blog
            )

    # Fetch all blogs and articles from the database
    blogs = ShopifyBlog.objects.all()

    return render(request, 'blog_list.html', {'blogs': blogs})


def serialize_shopify_data(request):
    # Fetch all Shopify blogs
    blogs = ShopifyBlog.objects.all()

    # Create a list to store serialized data
    serialized_data = []

    for blog in blogs:
        serialized_blog = {
            'title': blog.title,
            'articles': []
        }

        articles = ShopifyArticle.objects.filter(blog=blog)

        for article in articles:
            serialized_article = {
                'title': article.title,
                'body_html': article.body_html
            }
            serialized_blog['articles'].append(serialized_article)

        serialized_data.append(serialized_blog)

    return JsonResponse({'blogs': serialized_data})
