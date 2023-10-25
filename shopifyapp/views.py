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
from .utils import fetch_shopify_blogs, save_shopify_blogs, save_shopify_articles, fetch_shopify_articles


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
        return redirect('product_list')
    else:
        messages.error(request, 'Authentication failed.')
        return redirect('product_list')


def product_list(request):
    access_token = request.session.get('shopify_access_token')
    if access_token:
        shop_url = 'junior-state.myshopify.com'  # Replace with your Shopify store URL
        headers = {'X-Shopify-Access-Token': access_token}
        response = requests.get(f'https://{shop_url}/admin/api/{settings.SHOPIFY_API_VERSION}/products.json',
                                headers=headers)

        if response.status_code == 200:
            products_data = response.json().get('products', [])
            for product_data in products_data:
                ShopifyProduct.objects.create(
                    title=product_data['title'],
                    description=product_data['body_html'],
                    price=product_data['variants'][0]['price'],
                )

    products = ShopifyProduct.objects.all()
    return render(request, 'product_list.html', {'products': products})


def display_shopify_blogs(request):
    # Replace with your Shopify store's URL
    shop_url = 'junior-state.myshopify.com'

    # Replace with your Shopify access token
    access_token = request.session.get('shopify_access_token')

    # Make a GET request to fetch blogs from Shopify
    response = requests.get(f'https://{shop_url}/admin/api/2023-07/blogs.json',
                            headers={'X-Shopify-Access-Token': access_token})

    if response.status_code == 200:
        data = response.json()
        blogs = data.get('blogs', [])

        for blog in blogs:
            shopify_blog, created = ShopifyBlog.objects.get_or_create(
                title=blog['title']
            )

    blogs = ShopifyBlog.objects.all()
    articles = ShopifyArticle.objects.all()
    return render(request, 'blog_list.html', {'blogs': blogs})


def display_shopify_articles(request):
    # Replace with your Shopify store's URL
    shop_url = 'junior-state.myshopify.com'

    # Replace with your Shopify access token
    access_token = request.session.get('shopify_access_token')

    # Make a GET request to fetch blogs from Shopify
    response = requests.get(f'https://{shop_url}/admin/api/2023-07/articles.json',
                            headers={'X-Shopify-Access-Token': access_token})

    if response.status_code == 200:
        data = response.json()
        articles = data.get('articles', [])
        for article in articles:
            ShopifyArticle.objects.get_or_create(
                blog=article['blog'],
                title=article['title'],
                body_html=article['body_html']
            )

    articles = ShopifyArticle.objects.all()


def get_products(request):
    products = ShopifyProduct.objects.all()
    serialized_products = []

    for product in products:
        serialized_products.append({
            'title': product.title,
            'description': product.description,
        })

    return JsonResponse({'products': serialized_products})


def get_blogs(request):
    articles = ShopifyArticle.objects.all()
    serialized_articles = []

    for article in articles:
        serialized_articles.append({
            'title': article.title,

        })

    return JsonResponse({'articles': serialized_articles})


def send_data_to_shopify(request):
    success_message = ""
    access_token = request.session.get('shopify_access_token')
    products = ShopifyProduct.objects.all()

    # Convert Decimal values to float
    serialized_products = []
    for product in products:
        serialized_product = {
            'title': product.title,
            'description': product.description,
        }
        serialized_products.append(serialized_product)

    # Convert the data to JSON
    data_to_send = json.dumps(serialized_products)

    # Construct the GraphQL mutation
    section_id = "shopify-section-template--19513904169277__23edbad7-2082-4a84-8b0d-be5426ca4ce9"  # Replace with the actual section ID
    graphql_mutation = f'''
            mutation {{
                sectionUpdate(id: "{section_id}", data: "{data_to_send}") {{
                    section {{
                        id
                        data
                    }}
                }}
            }}
        '''

    # Make a GraphQL request to update the section's data
    graphql_url = 'https://junior-state.myshopify.com/admin/api/2023-07/graphql.json'  # Replace with your Shopify GraphQL API endpoint
    headers = {
        'Content-Type': 'application/json',
        'X-Shopify-Access-Token': access_token,  # Replace with your Shopify access token
    }
    data = json.dumps({'query': graphql_mutation})
    response = requests.post(graphql_url, headers=headers, data=data)

    if response.status_code == 200:
        # Handle success
        success_message = 'Data sent to Shopify section successfully'
    else:
        # Handle error
        error_message = 'Failed to send data to Shopify section'

    return HttpResponse(success_message if success_message else error_message)


def display_shopify_content(request):
    # Replace with your Shopify store's URL
    shop_url = 'junior-state.myshopify.com'

    # Replace with your Shopify access token
    access_token = request.session.get('shopify_access_token')

    blogs_data = fetch_shopify_blogs(shop_url, access_token)
    articles_data = []

    for blog_data in blogs_data:
        blog_id = blog_data['id']
        blog_articles = fetch_shopify_articles(shop_url, access_token, blog_id)
        articles_data.append({'blog': blog_data, 'articles': blog_articles})
    return render(request, 'content_list.html', {'articles_data': articles_data})


def send_content_to_shopify(request):
    success_message = ""
    access_token = request.session.get('shopify_access_token')
    articles = ShopifyArticle.objects.all()

    # Convert Decimal values to float
    serialized_articles = []
    for article in articles:
        serialized_product = {
            'blog': article.blog,
            'title': article.title,
            'body_html': article.body_html
        }
        serialized_articles.append(serialized_product)

    # Convert the data to JSON
    data_to_send = json.dumps(serialized_articles)

    # Construct the GraphQL mutation
    section_id = "shopify-section-template--19513904169277__23edbad7-2082-4a84-8b0d-be5426ca4ce9"  # Replace with the actual section ID
    graphql_mutation = f'''
            mutation {{
                sectionUpdate(id: "{section_id}", data: "{data_to_send}") {{
                    section {{
                        id
                        data
                    }}
                }}
            }}
        '''

    # Make a GraphQL request to update the section's data
    graphql_url = 'https://junior-state.myshopify.com/admin/api/2023-07/graphql.json'  # Replace with your Shopify GraphQL API endpoint
    headers = {
        'Content-Type': 'application/json',
        'X-Shopify-Access-Token': access_token,  # Replace with your Shopify access token
    }
    data = json.dumps({'query': graphql_mutation})
    response = requests.post(graphql_url, headers=headers, data=data)

    if response.status_code == 200:
        # Handle success
        success_message = 'Data sent to Shopify section successfully'
    else:
        # Handle error
        error_message = 'Failed to send data to Shopify section'

    return HttpResponse(success_message if success_message else error_message)


def fetch_and_save_shopify_data(request):
    # Replace with your Shopify store's URL
    shop_url = 'junior-state.myshopify.com'

    # Replace with your Shopify access token
    access_token = request.session.get('shopify_access_token')

    blogs_data = fetch_shopify_blogs(shop_url, access_token)
    articles_data = fetch_shopify_articles(shop_url, access_token)

    if blogs_data:
        save_shopify_blogs(blogs_data)

    if articles_data:
        save_shopify_articles(articles_data)

    return HttpResponse("Shopify blogs and articles fetched and saved successfully.")


def display_shopify_data(request):
    blogs = ShopifyBlog.objects.all()
    articles = ShopifyArticle.objects.all()
    return render(request, 'display_shopify_data.html', {'blogs': blogs, 'articles': articles})


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