import uuid
from random import randint

from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.generics import get_object_or_404
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

from shared.utils import check_phone, send_email
from apps.users.models import Confirmation, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'phone', 'photo')


class SignUpByPhone(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'auth_status', 'phone')

        extra_kwargs = {
            'phone': {
                'required': True
            },
            'auth_status': {
                'required': False,
                'read_only': True,
            },
        }

    def validate(self, data):
        phone = data.get('phone')
        if not check_phone(phone):
            raise ValidationError(
                {
                    'description': "Invalid phone number",
                    'status': status.HTTP_400_BAD_REQUEST
                }
            )

        confirmed_users = Confirmation.objects.filter(phone=phone, is_confirmed=True)
        if confirmed_users.exists():
            raise ValidationError(
                {
                    'description': "This phone already exist",
                    'status': status.HTTP_400_BAD_REQUEST
                }
            )
        return data

    def create(self, validated_data):
        username = f"username-{uuid.uuid4().__str__().split('-')[-1]}"
        while User.objects.filter(username=username).exists():
            username = f"{username}{randint(1, 9)}"
        password = f"password-{uuid.uuid4().__str__().split('-')[-1]}"
        phone = validated_data.get('phone')
        user = User.objects.filter(phone=phone)
        if user.exists():
            user = user.first()
        else:
            user = User.objects.create(username=username, phone=phone)
            user.set_password(password)
            user.save()
        confirmation = Confirmation.objects.create(user=user, phone=phone)
        code = confirmation.code
        send_email(phone, code)
        return user


class EnterFieldsSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'phone', 'confirm_password', 'password')
        extra_kwargs = {
            'password': {
                'required': True,
                'write_only': True
            },
            'username': {
                'required': True,
            },
            'phone': {
                'required': False,
                'read_only': True
            }
        }

    def validate(self, data):
        print(data)
        username = data.get('username')
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        users = User.objects.filter(username=username)
        if users.exists():
            raise ValidationError(
                {
                    'error': 'This username is already exists',
                    'status': status.HTTP_400_BAD_REQUEST
                }
            )
        print('password', password)
        print('confirm_password', confirm_password)
        if password != confirm_password:
            raise ValidationError({
                'error': 'password and confirm_password are not suitable',
                'status': status.HTTP_400_BAD_REQUEST
            })
        validate_password(password)
        validate_password(confirm_password)

        return data

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.set_password(validated_data.get('password'))
        instance.auth_status = 'registered'
        instance.save()
        return instance


class LoginSerializer(TokenObtainPairSerializer):
    username = serializers.CharField(required=True, write_only=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        username = data.pop('username')
        password = data.pop('password')

        authentication_kwargs = {
            self.username_field: username,
            'password': password,
        }

        user = authenticate(**authentication_kwargs)
        if user:
            self.user = user
        else:
            raise ValidationError(
                {
                    'success': False,
                    'detail': 'You entered wrong username or password',
                }
            )
        refresh = RefreshToken.for_user(user)
        data['access'] = str(refresh.access_token)
        data['refresh'] = str(refresh)
        return data


class LoginRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attr):
        data = super(LoginRefreshSerializer, self).validate(attr)
        access_token_instance = AccessToken(data['access'])
        user_id = access_token_instance.get('user_id')
        user = get_object_or_404(User.objects.all(), id=user_id)
        update_last_login(None, user)
        return data


class LogOutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class ForgotPasswordSerializer(serializers.Serializer):
    phone = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        phone = data.get("phone")
        user = User.objects.filter(phone=phone)
        if not user.exists():
            raise NotFound("User not found")
        data['user'] = user.first()
        return data


class ResetPasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('id', 'password', 'confirm_password')

    def validate(self, data):
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        if password != confirm_password:
            raise ValidationError(
                {
                    'success': False,
                    'message': "Password and confirm_password are not suitable",
                    'status': status.HTTP_400_BAD_REQUEST
                }
            )
        if password:
            validate_password(password)
        return data

    def update(self, instance, validated_data):
        password = validated_data.get('password')
        instance.set_password(password)
        instance.save()
        return instance
