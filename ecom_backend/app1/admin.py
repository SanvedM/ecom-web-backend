from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Customeuser)
admin.site.register(Address)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductVariant)
admin.site.register(ProductImage)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)



