import requests
from .models import ShopifyBlog, ShopifyArticle

def fetch_shopify_blogs(shop_url, access_token):
    url = f'https://{shop_url}/admin/api/2023-01/blogs.json'
    headers = {
        'X-Shopify-Access-Token': access_token,
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json().get('blogs', [])
    else:
        return []




def fetch_shopify_articles(shop_url, access_token):
    url = f'https://{shop_url}/admin/api/2023-01/articles.json'
    headers = {
        'X-Shopify-Access-Token': access_token,
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        articles_data = response.json().get('articles', [])
        return articles_data
    else:
        return []


def save_shopify_blogs(blogs_data):
    for blog_data in blogs_data:
        ShopifyBlog.objects.create(
            title=blog_data['title'],
        )


def save_shopify_articles(articles_data):
    for article_data in articles_data:
        blog_id = article_data['blog_id']
        blog = ShopifyBlog.objects.get(pk=blog_id)  # Get the associated blog
        ShopifyArticle.objects.create(
            title=article_data['title'],
            body_html=article_data['body_html'],
            blog=blog,
        )
