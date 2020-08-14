
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("like/<int:post_id>",views.like_unlike,name ='like_unlike'),
    path("users/<str:username>",views.profilepage,name='profilepage'),
    path("following",views.following_posts,name="following_posts")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
