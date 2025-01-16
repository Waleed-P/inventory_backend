from django.db import models
# Create your models here.
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
import uuid
from .dependencies import *

# Create your models here.

class Products(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)    
    ProductID = models.BigIntegerField(unique=True)    
    ProductCode = models.CharField(max_length=255, unique=True)
    ProductName = models.CharField(max_length=255)    
    ProductImage = models.ImageField(upload_to="uploads/", blank=True, null=True)    
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True, null=True)
    CreatedUser = models.ForeignKey("auth.User", related_name="user%(class)s_objects", on_delete=models.CASCADE)    
    IsFavourite = models.BooleanField(default=False)
    Active = models.BooleanField(default=True)    
    HSNCode = models.CharField(max_length=255, blank=True, null=True)    
    TotalStock = models.DecimalField(default=0.00, max_digits=20, decimal_places=8, blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if not self.ProductCode:
            self.ProductCode = generate_product_code()
        super().save(*args, **kwargs)
    
    class Meta:
        db_table = "products_product"
        verbose_name = _("product")
        verbose_name_plural = _("products")
        unique_together = (("ProductCode", "ProductID"),)
        ordering = ("-CreatedDate", "ProductID")
        
    def __str__(self):
        return f'{self.ProductID} - {self.ProductName}'


class Varient(models.Model):
    product = models.ForeignKey(Products, related_name='variants', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

class SubVarient(models.Model):
    variant = models.ForeignKey(Varient, related_name='sub_variants', on_delete=models.CASCADE)
    option = models.CharField(max_length=100)
    stock = models.DecimalField(default=0.00, max_digits=20, decimal_places=8)

    class Meta:
        unique_together = ('variant', 'option')
    
    def __str__(self):
        return f"{self.id} - {self.option}"
