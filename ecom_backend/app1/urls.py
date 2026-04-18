
from django.urls import path
from .utills.Category import category_list
from .utills.Product import product_list,prod_cate,product_details
from .utills.Cart import add_to_cart_api,mycart,update_cart_item,delete_cart_items
from .utills.Order import create_order, my_orders, order_detail, save_address,get_address,update_address
from .views import register_api,CustomLoginView,verify_otp_register,forgot_password,reset_password

urlpatterns = [
    path('register', register_api,name="register"),
    path('login', CustomLoginView.as_view(),name="login"),
    path('verify-otp', verify_otp_register,name="verify-otp"),
    path("forgot-password",forgot_password,name="forgot_password"),
    path("reset-password",reset_password,name="reset_password"),
    path('cate-list',category_list,name='cate_list' ),
    path('prod-list',product_list,name='prod_list'),
    path('prod-cate/<int:cate>',prod_cate,name='prod_cate'),
    path('add-to-cart',add_to_cart_api,name='add_to_cart_api'),
    path("my-cart",mycart,name="mycart"),
    path("update-cart",update_cart_item,name="update_cart_item"),
    path('delete-cart',delete_cart_items,name='delete_cart_items'),
    path('prod-details/<int:pk>',product_details,name="product_details"),
    
    
    path('create-order',create_order,name='create_order'),
    path("my-orders", my_orders,name="myorders"),
    path("order-detail/<int:order_id>", order_detail,name="ordre_details"),
    path("save-address", save_address,name="save_address"),
    path("get-address",get_address,name="get_address"),
    path("update-address/<int:pk>", update_address, name="update_address"),

]

