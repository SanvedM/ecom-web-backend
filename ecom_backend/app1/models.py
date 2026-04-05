from django.contrib.auth.models import AbstractUser
from django.db import models
from cloudinary.models import CloudinaryField
from django.utils import timezone

class Customeuser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('customer', 'Customer'),
    )

    mobile = models.CharField(max_length=15, unique=True, null=True, blank=True)
    is_mobile_verified = models.BooleanField(default=False)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')

    # 🔥 NEW FIELDS
    email_otp = models.CharField(max_length=6, null=True, blank=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)
    reset_otp = models.CharField(max_length=6, null=True, blank=True)
    reset_otp_created_at = models.DateTimeField(null=True, blank=True)

    def is_reset_otp_expired(self):
        from datetime import timedelta
        return self.reset_otp_created_at < timezone.now() - timedelta(minutes=10)

    def is_otp_expired(self):
        from datetime import timedelta
        return self.otp_created_at < timezone.now() - timedelta(minutes=5)
    
    
class Address(models.Model):
    user = models.ForeignKey(Customeuser, on_delete=models.CASCADE, related_name="addresses")
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    address_line = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

class Category(models.Model):
    name = models.CharField(max_length=255,db_index=True)
    # images = models.ImageField(upload_to="category/")
    images = CloudinaryField('image')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255,db_index=True)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    sku = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    size = models.CharField(max_length=50, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.product.name} - {self.sku}"
    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    # image = models.ImageField(upload_to="products/")
    image = CloudinaryField('image')
    is_primary = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.product.name}"
    


class Cart(models.Model):
    user = models.OneToOneField(Customeuser, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField()

    class Meta:
        unique_together = ('cart', 'variant')


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(Customeuser, on_delete=models.CASCADE, related_name="orders")
    name = models.CharField(max_length=100)
    address = models.CharField(null=True,blank=True,max_length=500)

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)



class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True)

    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)


class Payment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    )

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments")

    payment_id = models.CharField(max_length=255)
    payment_method = models.CharField(max_length=50)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

class Review(models.Model):
    user = models.ForeignKey(Customeuser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")

    rating = models.IntegerField()
    comment = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)