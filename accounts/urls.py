from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    # Phase 3: User Registration
    path("register/", views.register, name="register"),
    # Phase 4: User Login & Logout
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    # Phase 5: Profile Management
    path("profile/", views.profile_view, name="profile"),
    # Phase 6: Password Change
    path("profile/password/", views.change_password_view, name="change_password"),
]
