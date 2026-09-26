from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('product/', views.product_list, name='product_list'),
     path('contact/', views.contact, name='contact'),
    path('error/', views.error_page, name='error_page'),
    path('about/', views.about, name='about'),
    path("login/", views.login_view, name="login"),
    path("register/",views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path("verify-otp/", views.verify_otp, name="verify_otp"),
    path("reset-password/", views.reset_password, name="reset_password"),
    path('verify-email/', views.verify_email, name='verify_email'),
]
