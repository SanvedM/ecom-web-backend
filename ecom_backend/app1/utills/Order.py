from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from rest_framework import status
from ..models import Product,ProductVariant,Cart,CartItem,Order,OrderItem
from ..serializers import *
from django.db.models import Prefetch
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import authentication_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes



@api_view(["POST"])
@permission_classes([IsAuthenticated])
def save_address(request):
    serializer = AddressSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data)

    return Response(serializer.errors, status=400)



@api_view(["PUT"])
@authentication_classes([JWTAuthentication])   # 👈 IMPORTANT
@permission_classes([IsAuthenticated])
def update_address(request, pk):
    address = Address.objects.get(id=pk, user=request.user)

    serializer = AddressSerializer(address, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(serializer.errors, status=400)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_address(request):
    address = Address.objects.filter(user=request.user).order_by("-id").first()

    if not address:
        return Response(None)

    serializer = AddressSerializer(address)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_order(request):
    user = request.user

    address_id = request.data.get("address_id")
    payment_method = request.data.get("payment_method")  # COD / ONLINE

    try:
        address = Address.objects.get(id=address_id, user=user)
    except Address.DoesNotExist:
        return Response({"error": "Invalid address"}, status=400)

    try:
        cart = Cart.objects.get(user=user)
    except Cart.DoesNotExist:
        return Response({"error": "Cart not found"}, status=400)



    cart_items = cart.items.all()


    if not cart_items.exists():
        return Response({"error": "Cart is empty"}, status=400)

    total = Decimal(0)

    # CREATE ORDER
    order = Order.objects.create(
        user=user,
        name=address.full_name,
        address=f"{address.address_line}, {address.city}, {address.state} - {address.pincode}",
        total_amount=0,
        status="pending"
    )

    # CREATE ORDER ITEMS
    for item in cart_items:
        variant = item.variant
        price = item.variant.price
        quantity = item.quantity

        if variant.stock < quantity:
            return Response({
                "error": f"{variant.product.name} is out of stock"
            }, status=400)

        # ✅ REDUCE STOCK
        variant.stock -= quantity
        variant.save()

        total += price * quantity

        OrderItem.objects.create(
            order=order,
            variant=item.variant,
            quantity=quantity,
            price=price
        )

    order.total_amount = total
    order.save()

    # CLEAR CART
    Payment.objects.create(
        order=order,
        payment_id="COD_" + str(order.id),
        payment_method="COD",
        status="pending"
    )

    # CLEAR CART
    cart_items.delete()

    return Response({
        "message": "Order created successfully",
        "order_id": order.id
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")

    serializer = OrderSerializer(orders, many=True,context={"request": request})
    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def order_detail(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=404)

    serializer = OrderSerializer(
    order,
    context={"request": request}   # 👈 ADD THIS
)
    return Response(serializer.data)