from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import timedelta
from .models import User
from .serializers import UserRegistrationSerializer
from .utils import generate_verification_token
from django.core.mail import send_mail
from django.conf import settings


def send_verification_email(user):
    token = generate_verification_token()
    user.verification_token = token
    user.save()

    verification_url = f"{settings.SITE_URL}/verify-email/{token}/"  # Ссылка для подтверждения email

    send_mail(
        'Email confirmation',
        f"Please confirm your email by clicking on the link: {verification_url}",
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )


@api_view(['POST'])
def user_registration(request):
    email = request.data.get('email')

    if User.objects.filter(email=email).exists():
        return Response(
            {"email": "The user with this email already exists."},
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer = UserRegistrationSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()

        # Отправить письмо с подтверждением email
        send_verification_email(user)

        return Response(
            {
                "message": "The user has been successfully registered. Please check your email for confirmation.",
                "user": {
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email
                }
            },
            status=status.HTTP_201_CREATED
        )

    return Response(
        {"errors": serializer.errors},
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['GET'])
def verify_email(request, token):
    try:
        user = User.objects.get(verification_token=token)
        user.is_verified = True
        user.is_active = True
        user.verification_token = None  # Стираем токен после подтверждения
        user.save()

        return Response(
            {"message": "Your email has been successfully verified!"},
            status=status.HTTP_200_OK
        )
    except User.DoesNotExist:
        return Response(
            {"error": "Invalid activation token."},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
def login_user(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({"error": "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.filter(email=email).first()
    if not user:
        return Response({"error": "Invalid email."}, status=status.HTTP_401_UNAUTHORIZED)

    if user.failed_attempts >= 5 and user.lockout_time > timezone.now():
        remaining_lock_time = user.lockout_time - timezone.now()
        return Response({
            "error": f"Account is locked. Try again in {remaining_lock_time.seconds} seconds."
        }, status=status.HTTP_403_FORBIDDEN)

    user_authenticated = authenticate(request, email=email, password=password)

    if user_authenticated is None:
        user.failed_attempts += 1
        if user.failed_attempts >= 5:
            user.lockout_time = timezone.now() + timedelta(minutes=15)
        user.save()

        return Response({"error": "Invalid password."}, status=status.HTTP_401_UNAUTHORIZED)

    user.failed_attempts = 0
    user.save()

    refresh = RefreshToken.for_user(user_authenticated)
    access_token = refresh.access_token

    return Response(
        {
            "message": "Login successful.",
            "access_token": str(access_token),
            "refresh_token": str(refresh),
        },
        status=status.HTTP_200_OK
    )