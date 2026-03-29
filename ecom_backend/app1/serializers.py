from rest_framework import serializers
from .models import *

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


from rest_framework import serializers

class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = "__all__"

    def get_image(self, obj):
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url
    
class ProductVariantSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    price = serializers.SerializerMethodField()
    stock = serializers.SerializerMethodField()
    class Meta:
        model = ProductVariant
        fields = "__all__"

    def get_price(self, obj):
        return obj.price if obj.price is not None else 0

    def get_stock(self, obj):
        return obj.stock if obj.stock is not None else 0

class ProductSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(many=True)
    images = ProductImageSerializer(many=True) 
    class Meta:
        model = Product
        fields = "__all__"
        


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'user', 'updated_at']
        read_only_fields = ['user']

# And ensure your Item serializer looks like this
class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem  # <--- AND THIS
        fields = ['variant', 'quantity']

    def create(self, validated_data):
        cart = self.context['cart']
        variant = validated_data.get('variant')
        quantity = validated_data.get('quantity')
        print(cart,variant,quantity,";;;;;;;;;;;;;;;;;;;")

        # Logic to update quantity if already exists
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            variant=variant,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        print(cart_item,"thisis inside serializer")
            
        return cart_item
        

class ViewCartSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='variant.product.name', read_only=True)
    price = serializers.DecimalField(source='variant.price', max_digits=10, decimal_places=2, read_only=True)
    product_stock = serializers.CharField(source='variant.stock', read_only=True)

    image = serializers.SerializerMethodField()
    line_total = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'quantity', 'product_name', 'price', 'image', 'line_total','product_stock']

    def get_image(self, obj):
        request = self.context.get('request')
        image = obj.variant.product.images.filter(is_primary=True).first()
        if not image:
            image = obj.variant.product.images.first()
        if image and request:
            return request.build_absolute_uri(image.image.url)  # ✅ full clickable URL
        return None

    def get_line_total(self, obj):
        return obj.quantity * obj.variant.price

    def create(self, validated_data):
        cart = self.context['cart']
        variant = validated_data.get('variant')
        quantity = validated_data.get('quantity')

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            variant=variant,
            defaults={'quantity': quantity}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        return cart_item


class CreateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem  # <--- AND THIS
        fields = ['user','name', 'address','total_amount','status']

    def create(self, validated_data):
        print("validated dtaat",validated_data)
        name = validated_data.get('name')
        address = validated_data.get('address')
        total_amount = validated_data.get("total_amount")
        print(name,address,";;;;;;;;;;;;;;;;;;;")

        # Logic to update quantity if already exists
        order_item = OrderItem.objects.create(
            user=self.user,
            name=name,
            address=address,
            total_amount=total_amount,
            status="Pending"
        )
 
        return order_item
        