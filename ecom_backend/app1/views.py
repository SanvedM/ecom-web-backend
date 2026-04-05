# Create your views here.
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import CustomTokenSerializer
import random
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail

from django.utils import timezone
from rest_framework_simplejwt.views import TokenObtainPairView





User = get_user_model()


@api_view(['POST'])
def register_api(request):
    email = request.data.get("email")
    username = request.data.get("username")
    password = request.data.get("password")

    if not email or not username or not password:
        return Response({"error": "All fields required"}, status=400)

    # 🔥 DUPLICATE CHECK
    if User.objects.filter(email=email, is_active=True).exists():
        return Response({"error": "Email already registered"}, status=400)

    if User.objects.filter(username=username, is_active=True).exists():
        return Response({"error": "Username already exists"}, status=400)

    otp = str(random.randint(100000, 999999))

    # 🔥 CREATE OR UPDATE TEMP USER
    user, created = User.objects.update_or_create(
        email=email,
        defaults={
            "username": username,
            "password": make_password(password),
            "email_otp": otp,
            "otp_created_at": timezone.now(),
            "is_active": False
        }
    )

    # 🔥 SEND EMAIL
    send_mail(
        'Your OTP Code',
        f'Your OTP is {otp}',
        'yourgmail@gmail.com',
        [email],
        fail_silently=False,
    )

    print(f"OTP: {otp}")

    return Response({"message": "OTP sent to email"})

@api_view(['POST'])
def verify_otp_register(request):
    email = request.data.get("email")
    otp = str(request.data.get("otp")).strip()

    if not email or not otp:
        return Response({"error": "Email and OTP required"}, status=400)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=400)

    if user.email_otp != otp:
        return Response({"error": "Invalid OTP"}, status=400)

    if user.is_otp_expired():
        return Response({"error": "OTP expired"}, status=400)

    # 🔥 ACTIVATE USER
    user.is_active = True
    user.is_mobile_verified = True
    user.email_otp = None
    user.otp_created_at = None
    user.save()

    return Response({"message": "User registered successfully"}, status=201)




@api_view(['POST'])
def forgot_password(request):
    email = request.data.get("email")

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=400)

    otp = str(random.randint(100000, 999999))

    user.reset_otp = otp
    user.reset_otp_created_at = timezone.now()
    user.save()

    send_mail(
        'Reset Password OTP',
        f'Your OTP is {otp}',
        'yourgmail@gmail.com',
        [email],
        fail_silently=False,
    )

    print("RESET OTP:", otp)

    return Response({"message": "OTP sent to email"})




@api_view(['POST'])
def reset_password(request):
    email = request.data.get("email")
    otp = request.data.get("otp")
    new_password = request.data.get("password")

    if not email or not otp or not new_password:
        return Response({"error": "All fields required"}, status=400)

    otp = str(otp).strip()

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=400)

    if not user.is_active:
        return Response({"error": "User not verified"}, status=400)

    if user.reset_otp != otp:
        return Response({"error": "Invalid OTP"}, status=400)

    if user.is_reset_otp_expired():
        return Response({"error": "OTP expired"}, status=400)

    user.password = make_password(new_password)
    user.reset_otp = None
    user.reset_otp_created_at = None
    user.save()

    return Response({"message": "Password reset successful"})


class CustomLoginView(TokenObtainPairView):
    serializer_class = CustomTokenSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_api(request):
    try:
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response({"error": "Refresh token required"}, status=400)

        token = RefreshToken(refresh_token)
        token.blacklist()

        return Response({
            "message": "Logout successful"
        }, status=205)

    except Exception as e:
        return Response({
            "error": "Invalid token"
        }, status=400)