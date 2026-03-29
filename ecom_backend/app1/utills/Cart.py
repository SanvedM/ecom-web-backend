from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from rest_framework import status
from ..models import Product,ProductVariant,Cart,CartItem
from ..serializers import CartSerializer,CartItemSerializer,ViewCartSerializer
from django.db.models import Prefetch

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart_api(request):
    print(request.user, "llllllllllluser=l")
    # ✅ HANDLE ANONYMOUS USER
    user = request.user if request.user.is_authenticated else None
    # ✅ IMPORTANT: only pass user if exists
    if user:
        cart, _ = Cart.objects.get_or_create(user=user)
    else:
        cart = Cart.objects.create(user=None)  # OR handle differently
    serializer = CartItemSerializer(
        data=request.data,
        context={'cart': cart}
    )
    if serializer.is_valid():
        serializer.save()
        return Response({
            "status": "success",
            "message": "Item added to cart",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mycart(request):
    user = request.user
    try:
        cart = Cart.objects.get(user=user)
    except Cart.DoesNotExist:
        return Response({
            "status": "empty",
            "message": "No cart found for this user",
            "data": []
        }, status=status.HTTP_404_NOT_FOUND)

    serializer = ViewCartSerializer(cart.items.all(), many=True, context={'request': request})
    grand_total = sum([item.quantity * item.variant.price for item in cart.items.all()])

    print(serializer.data,"///////////")
    return Response({
        "status": "success",
        "message": "Cart items retrieved",
        "grand_total": grand_total,
        "data": serializer.data
    }, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_cart_item(request):
    item_id = request.data.get("item_id")
    quantity = request.data.get("quantity")

    cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)

    # 🔥 STOCK CHECK
    if quantity > cart_item.variant.stock:
        return Response({
            "error": "Stock exceeded"
        }, status=400)

    cart_item.quantity = quantity
    cart_item.save()

    return Response({"message": "Updated"}, status=200)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_cart_items(request):
    try:
        item_id = request.data.get("item_id")
        print(item_id,"inside the delete cart")

        cart_item = CartItem.objects.get(id=item_id, cart__user=request.user).delete()
        print(cart_item,"this is deleted item")
        return Response({"message":"Cart item deleted"},status=200)
    except Exception as e:
        print(e,"thisis ")
        return Response(
        {"status": "error", "message": "Item not found in your cart"},
            status=status.HTTP_404_NOT_FOUND
    )
