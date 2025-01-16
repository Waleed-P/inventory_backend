from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status
from .models import *
from rest_framework.views import APIView
import json
from .permissions import *
from django.shortcuts import get_object_or_404
# Create your views here.

class AddProductView(APIView):
    permission_classes = [IsLoginUserOnly]

    def post(self, request, *args, **kwargs):
        try:
            user = request.user
            if not user.is_authenticated:
                return Response({
                    'status': 'Failed',
                    'message': 'User not authenticated',
                    'response_code': status.HTTP_401_UNAUTHORIZED
                }, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({
                'status': "Failed",
                "message": "Failed to login",
                'response_code': status.HTTP_401_UNAUTHORIZED
            }, status=status.HTTP_401_UNAUTHORIZED)

        try:
            product_name = request.data.get('name')
            varients_data = request.data.get('varients', [])

            if not product_name or not varients_data:
                return Response({
                    'status': 'Failed',
                    'message': 'Product name and varients are required',
                    'response_code': status.HTTP_400_BAD_REQUEST
                }, status=status.HTTP_400_BAD_REQUEST)

            # Use auto-increment for ProductID in the DB instead of manual calculation
            product = Products.objects.create(
                ProductName=product_name,
                ProductID=Products.objects.latest('ProductID').ProductID + 1 if Products.objects.exists() else 1,
                CreatedUser=user
            )

            varients_list = []
            for i in varients_data:
                varient_name = i.get('name')
                options = i.get('options', [])
                if not varient_name or not options:
                    continue

                varient = Varient.objects.create(product=product, name=varient_name)
                sub_varients_list = []
                for k in options:
                    sub_varient = SubVarient.objects.create(variant=varient, option=k, stock=0)
                    sub_varients_list.append({
                        'id': sub_varient.id,
                        'option': sub_varient.option,
                        'stock': float(sub_varient.stock)
                    })

                varients_list.append({
                    'id': varient.id,
                    'name': varient.name,
                    'sub_varients': sub_varients_list
                })

            data = {
                'id': product.id,
                'ProductID': product.ProductID,
                'ProductCode': product.ProductCode,
                'ProductName': product.ProductName,
                'TotalStock': float(product.TotalStock),
                'varients': varients_list
            }

            return Response({
                'status': 'success',
                "message": "Successfully created",
                'response_code': status.HTTP_201_CREATED,
                "data": data
            }, status=201)

        except Exception as e:
            return Response({'error': str(e)}, status=500)

class ProductListView(APIView):
    permission_classes = [IsLoginUserOnly]

    def get(self, request, *args, **kwargs):
        products = Products.objects.all()
        product_list = []

        for product in products:
            variants = product.variants.all()
            variant_list = []
            for variant in variants:
                sub_variants = variant.sub_variants.all()
                sub_variant_list = [{'id': sv.id, 'option': sv.option, 'stock': float(sv.stock)} for sv in sub_variants]
                variant_list.append({'id': variant.id, 'name': variant.name, 'sub_varients': sub_variant_list})
            
            product_list.append({
                'id': product.id,
                'ProductID': product.ProductID,
                'ProductCode': product.ProductCode,
                'ProductName': product.ProductName,
                'TotalStock': float(product.TotalStock),
                'varients': variant_list
            })

        return Response({
            "status": "success",
            "message": "Products list fetched successfully",
            'products': product_list,
            "response_code": status.HTTP_200_OK
        }, status=200)

class ProductDetailView(APIView):
    def get(self, request):
        try:
            product_code = request.data.get('product_code')
            if product_code is None:
                return Response({
                    "status": "Failed",
                    "message": "Product code is missing",
                    "response_code": status.HTTP_400_BAD_REQUEST
                }, status=400)
            
            product = Products.objects.filter(ProductCode=product_code).first()
            if not product:
                return Response({
                    "status": "Failed",
                    "message": "Product not found",
                    "response_code": status.HTTP_404_NOT_FOUND
                }, status=404)
            
            variant_list = []  # Corrected the variable name
            for variant in product.variants.all():  # Corrected the attribute name
                sub_variant_list = [{
                    'id': sv.id,
                    'option': sv.option,
                    'stock': float(sv.stock)
                } for sv in variant.sub_variants.all()]
                
                variant_list.append({
                    'id': variant.id,
                    'name': variant.name,
                    'sub_varients': sub_variant_list
                })

            product_data = {
                'id': product.id,
                'ProductID': product.ProductID,
                'ProductCode': product.ProductCode,
                'ProductName': product.ProductName,
                'TotalStock': float(product.TotalStock),
                'variants': variant_list
            }

            return Response({
                "status": "Success",
                "message": "Product details fetched successfully",
                "response_code": status.HTTP_200_OK,
                "product": product_data
            }, status=200)

        except Exception as e:
            return Response({
                "status": "Failed",
                "message": str(e),
                "response_code": status.HTTP_500_INTERNAL_SERVER_ERROR
            }, status=500)

class AddStockView(APIView):
    permission_classes = [IsLoginUserOnly]
    def post(self, request, *args, **kwargs):
        try:
            sub_varient_id = request.data.get('sub_varient_id')
            if sub_varient_id is None:
                return Response({
                    "status":"Failed",
                    "message":"Sub-varient ID is missing",
                    "response_code":status.HTTP_400_BAD_REQUEST
                },
                                status=400)
            stock_to_add = request.data.get('stock', 0)
            if not isinstance(stock_to_add, (int, float)):
                return Response({
                    "status":"Failed",
                    "message":"Stock quantity is missing",
                    "response_code":status.HTTP_400_BAD_REQUEST
                },
                                status=400)

            if stock_to_add <= 0:
                return Response({
                    "status":"Failed",
                    "message":"Invalid stock quantity",
                    "response_code":status.HTTP_400_BAD_REQUEST
                    },
                                status=400)
            
            sub_varient = SubVarient.objects.filter(id=sub_varient_id).first()
            if sub_varient is None:
                return Response({
                    "status":"Failed",
                    "message":"Sub-varient not found",
                    "response_code":status.HTTP_404_NOT_FOUND
                },
                                status=404)
            sub_varient.stock += stock_to_add
            sub_varient.save()
            
            data = {
                "sub_varient_id":sub_varient.id,
                "stock":sub_varient.stock
            }
            
            return Response({
                "status":"Success",
                "message":"Stock added successfully",
                "data":data,
                "response_code":status.HTTP_200_OK
            },
                            status=200)
            
        except SubVarient.DoesNotExist:
            return Response({
                "status":"Failed",
                "message":"Sub-varient not found",
                "response_code":status.HTTP_404_NOT_FOUND
                },
                            status=404)
        except Exception as e:
            return Response({
                "status":"Failed",
                "message":str(e),
                "response_code":status.HTTP_500_INTERNAL_SERVER_ERROR
                },
                            status=500)


class RemoveStockView(APIView):
    permission_classes = [IsLoginUserOnly]
    def post(self, request, *args, **kwargs):
        try:
            sub_varient_id = request.data.get('sub_varient_id')
            if sub_varient_id is None:
                return Response({
                    "status":"Failed",
                    "message":"Sub-varient ID is missing",
                    "response_code":status.HTTP_400_BAD_REQUEST
                },
                                status=400)
            stock_to_remove = request.data.get('stock')
            if stock_to_remove is None:
                return Response({
                    "status":"Failed",
                    "message":"Stock quantity is missing",
                    "response_code":status.HTTP_400_BAD_REQUEST
                },
                                status=400)

            if stock_to_remove <= 0:
                return Response({
                    "status":"Failed",
                    "message":"Stock quantity is invalid",
                    "response_code":status.HTTP_400_BAD_REQUEST
                },
                                status=400)

            sub_varient = SubVarient.objects.filter(id=sub_varient_id).first()
            if sub_varient is None:
                return Response({
                    "status":"Failed",
                    "message":"Sub-varient not found",
                    "response_code":status.HTTP_404_NOT_FOUND
                },
                                status=404)
            if sub_varient.stock >= stock_to_remove:
                sub_varient.stock -= stock_to_remove
                sub_varient.save()
                return Response({
                    "status":"Success",
                    "message":"Stock removed successfully",
                    "data": {
                        "sub_varient_id":sub_varient.id,
                        "stock":sub_varient.stock
                    },
                    "response_code":status.HTTP_200_OK
                },
                                status=200)
            else:
                return Response({
                    "status":"Failed",
                    "message":"Not enough stock to remove",
                    "response_code":status.HTTP_400_BAD_REQUEST
                },
                                status=400)
        except SubVarient.DoesNotExist:
            return Response({
                "status":"Failed",
                "message":"Sub-varient not found",
                "response_code":status.HTTP_404_NOT_FOUND
                },
                            status=404)
        except Exception as e:
            return Response({
                "status":"Failed",
                "message":str(e),
                "response_code":status.HTTP_500_INTERNAL_SERVER_ERROR
            },
                            status=500)

class ProductUpdate(APIView):
    def post(self, request):
        print("Product update")
        try:
            product_code = request.data.get('product_code')

            if product_code:
                product = Products.objects.filter(ProductCode=product_code).first()
                print("product ", product)

                if product:
                    product_name = request.data.get('product_name')
                    if product_name:
                        product.ProductName = product_name
                        product.save()

                    varient_id = request.data.get('varient_id')
                    if varient_id:
                        varient = Varient.objects.filter(id=varient_id).first()
                        if varient:
                            varient_name = request.data.get('varient_name')
                            if varient_name:
                                varient.name = varient_name
                                varient.save()

                            sub_varient_id = request.data.get('sub_varient_id')
                            if sub_varient_id:
                                sub_varient = SubVarient.objects.filter(id=sub_varient_id).first()
                                if sub_varient:
                                    sub_varient_option = request.data.get('sub_varient_option')
                                    sub_varient_stock = request.data.get('sub_varient_stock')
                                    if sub_varient_option:
                                        sub_varient.option = sub_varient_option
                                    if sub_varient_stock:
                                        sub_varient.stock = sub_varient_stock
                                    sub_varient.save()

                            return Response({
                                "status": "Success",
                                "message": "Product updated successfully",
                                "response_code": status.HTTP_200_OK
                            }, status=200)

                    return Response({
                        "status": "Success",
                        "message": "Product updated successfully",
                        "response_code": status.HTTP_200_OK
                    }, status=200)

                else:
                    return Response({
                        "status": "Failed",
                        "message": "Product not found",
                        "response_code": status.HTTP_404_NOT_FOUND
                    }, status=404)
            else:
                return Response({
                    "status": "Success",
                    "message": "Product code is required to update product",
                    "response_code": status.HTTP_200_OK
                }, status=200)
        except Exception as e:
            return Response({
                "status": "Failed",
                "message": str(e),
                "response_code": status.HTTP_500_INTERNAL_SERVER_ERROR
            }, status=500)