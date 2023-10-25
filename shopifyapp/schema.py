import graphene
from graphene_django.types import DjangoObjectType
from .models import ShopifyProduct  # Replace with your model
from django.views.decorators.csrf import csrf_exempt

