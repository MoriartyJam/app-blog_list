from django.db import models


# Create your models here.


class ShopifyProduct(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class ShopifyBlog(models.Model):
    title = models.CharField(max_length=255)


class ShopifyArticle(models.Model):
    title = models.CharField(max_length=255)
    body_html = models.TextField()
    blog = models.ForeignKey(ShopifyBlog, on_delete=models.CASCADE)
