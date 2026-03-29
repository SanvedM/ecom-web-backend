from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from rest_framework import status
from ..models import Product,ProductVariant,Cart,CartItem,Order,OrderItem
from ..serializers import CreateOrderSerializer
from django.db.models import Prefetch


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_order(request):
    user = request.user if request.user.is_authenticated else None
    
    print(user,";asl;a",request.data)
    serializer = CreateOrderSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
    ord_obj = Order.objects.create()
    return Response("thishshs")