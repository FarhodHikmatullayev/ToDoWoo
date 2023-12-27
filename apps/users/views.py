from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.shortcuts import render
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from shared.utils import send_email
from apps.users.models import User, Confirmation
from apps.users.serializers import SignUpByPhone, EnterFieldsSerializer, LoginSerializer, LoginRefreshSerializer, \
    LogOutSerializer, ForgotPasswordSerializer, ResetPasswordSerializer


class SignUpApiView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        data = request.data
        phone = data.get('phone')
        serializer = SignUpByPhone(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user = User.objects.get(phone=phone)
        response = serializer.validated_data
        refresh = RefreshToken.for_user(user=user)
        response['access'] = str(refresh.access_token)
        response['refresh'] = str(refresh)

        return Response({
            'success': True,
            'data': response,
            'detail': 'Sent yor phone a verification code',
            'status': status.HTTP_200_OK
        })


class VerifyCodeApiView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        data = request.data
        code = data.get('code')
        user = request.user
        confirmations = Confirmation.objects.filter(
            Q(code=code) & Q(is_confirmed=False) & Q(time_limit__gt=datetime.now()) & Q(user=user))
        if confirmations.exists():
            user.auth_status = 'code'
            user.save()
            refresh = RefreshToken.for_user(user)
            verification = confirmations.first()
            verification.is_confirmed = True
            verification.save()
            return Response(
                {
                    'success': True,
                    'detail': 'Your code successfully confirmed',
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'user_status': user.auth_status,
                    'status': status.HTTP_200_OK,
                }
            )
        else:
            return Response(
                {
                    'success': False,
                    'detail': 'You entered a wrong code',
                    'status': status.HTTP_400_BAD_REQUEST,
                }
            )


class NewVerificationApiView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        verifications = user.confirmations.filter(is_confirmed=False, time_limit__gt=datetime.now())
        if verifications.exists():
            return Response(
                {
                    'success': False,
                    'detail': 'You have a valid code, please, wait a moment!',
                    'status': status.HTTP_400_BAD_REQUEST,
                }
            )
        else:
            confirmation = Confirmation.objects.create(user=user, phone=user.phone)
            code = confirmation.code
            send_email(user.phone, code)
            return Response(
                {
                    'success': True,
                    'detail': 'Sent a new confirmation code to your phone number',
                    'status': status.HTTP_200_OK
                }
            )


class EnterFieldsApiView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request):
        data = request.data
        serializer = EnterFieldsSerializer(data=data, instance=request.user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                'success': True,
                'detail': 'Your username and password successfully saved',
                'status': status.HTTP_200_OK
            }
        )


class LoginApiView(TokenObtainPairView):
    serializer_class = LoginSerializer


class LoginRefreshApiView(TokenRefreshView):
    serializer_class = LoginRefreshSerializer


class LogOutApiView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        serializer = LogOutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            refresh_token = data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {
                    'success': True,
                    'detail': 'You are successfully logged out',
                    'status': status.HTTP_205_RESET_CONTENT,
                }
            )
        except TokenError:
            return Response(
                {
                    'success': False,
                    'status': 400
                }
            )


class ForgotPasswordApiView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        data = request.data
        serializer = ForgotPasswordSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get('user')
        phone = data.get('phone')
        confirmation = Confirmation.objects.create(user=user, phone=phone)
        refresh = RefreshToken.for_user(user)

        send_email(user.phone, code=confirmation.code)
        return Response(
            {
                'success': True,
                'detail': 'Sent confirmation code to your phone number',
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }
        )


class ResetPasswordApiView(UpdateAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['patch', 'put']
    queryset = User.objects.all()

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        response = super(ResetPasswordApiView, self).update(request, *args, **kwargs)
        print(response)
        try:
            user = User.objects.get(id=response.data.get('id'))
        except ObjectDoesNotExist as e:
            raise NotFound(detail="User not found")
        return Response({
            'success': True,
            'message': "Your password successfully changed",
            'status': status.HTTP_200_OK
        })
