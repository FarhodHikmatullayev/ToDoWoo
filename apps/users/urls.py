from django.urls import path

from .views import SignUpApiView, VerifyCodeApiView, NewVerificationApiView, EnterFieldsApiView, LoginApiView, \
    LoginRefreshApiView, LogOutApiView, ForgotPasswordApiView, ResetPasswordApiView

app_name = 'users'

urlpatterns = [
    path('sign-up/', SignUpApiView.as_view(), name='sign_up'),
    path('verify-code/', VerifyCodeApiView.as_view(), name='verify_code'),
    path('new-verification/', NewVerificationApiView.as_view(), name='new_verification'),
    path('register/', EnterFieldsApiView.as_view(), name='register'),
    path('login/', LoginApiView.as_view(), name='login'),
    path('refresh-login/', LoginRefreshApiView.as_view(), name='refresh_login'),
    path('log-out/', LogOutApiView.as_view(), name='log_out'),
    path('forgot-password/', ForgotPasswordApiView.as_view(), name='forgot_password'),
    path('reset-password/', ResetPasswordApiView.as_view(), name='reset_password'),
]
