from django.urls import path
from .views import *


urlpatterns = [
    path('add-product/', AddProductView.as_view(), name='add_product'),
    path('list-products/', ProductListView.as_view(), name='list_products'),
    path('add-stock/', AddStockView.as_view(), name='add_stock'),
    path('remove-stock/', RemoveStockView.as_view(), name='remove_stock'),
    path('update-stock/', ProductUpdate.as_view(), name='update_stock'),
    path('product-details/', ProductDetailView.as_view(), name='product-details')
    ]