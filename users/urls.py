from django.urls import path, include
from .views import (
    Signup,
    VerifyOtp,
    Login,
    Logout,
    ResendOtp,
    ForgetPassword,
    GoogleSignIn,
    SearchResult,
)

urlpatterns = [
    path("signup", Signup.as_view(), name="signup"),
    path("otp_verification", VerifyOtp.as_view(), name="otp_verification"),
    path("login", Login.as_view(), name="login"),
    path("google", GoogleSignIn.as_view(), name="google"),
    path("logout", Logout.as_view(), name="logout"),
    path("resend_otp", ResendOtp.as_view(), name="resend_otp"),
    path("forget_pass", ForgetPassword.as_view(), name="forget_pass"),
    path("search", SearchResult.as_view(), name="search"),
]
