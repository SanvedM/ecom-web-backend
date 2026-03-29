from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import Product,ProductVariant
from ..serializers import ProductSerializer
from django.db.models import Prefetch


@api_view(["GET"])
def product_list(request):
    prod = Product.objects.filter(
        is_active=True,
        variants__is_active=True,
        variants__price__isnull=False,
        variants__stock__isnull=False,
        variants__price__gt=0
        ).distinct().prefetch_related(
        "variants",
        "images"
    )
    data = ProductSerializer(prod,many=True,context={"request": request})
    print(data.data,"this is data")
    return Response({"data":data.data})

@api_view(["GET"])
def prod_cate(request,cate):
    prod = Product.objects.filter(
        category=cate,is_active=True,
        variants__is_active=True,
        variants__price__isnull=False,
        variants__stock__isnull=False,
        variants__price__gt=0
        ).prefetch_related(
        "variants",
        "images"
    )
    data = ProductSerializer(prod,many = True,context={"request": request} )
    return Response({"data":data.data})


@api_view(["GET"])
def product_details(request,pk):
    prod = Product.objects.filter(id=pk).prefetch_related("variants","images")

    data = ProductSerializer(prod,many = True,context={"request": request} )
    print(data.data,"this is data")
    return Response({"data":data.data})