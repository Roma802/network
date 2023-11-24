from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.views.generic import RedirectView

from . import views
from .views import PostUpdateView, PostDetailView, PostDeleteView, ProfileUpdateView, BookmarksListView, \
    NotificationListView

urlpatterns = [
    path("index", views.PostListView.as_view(), name="index"),
    path("index/tag/<slug:tag_slug>", views.PostListView.as_view(), name="index-tag"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("explore", views.explore, name="explore"),
    path("create_post", views.new_post, name="create_post"),
    path('follow', views.user_follow, name='user_follow'),
    path("user_profile/<slug:slug>", views.user_profile, name="user_profile"),
    path('post/<int:pk>/edit/', PostUpdateView.as_view(), name='post_edit'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post_delete'),
    path("likes", views.likes, name="likes"),
    path("following/", views.FollowingListView.as_view(), name="following"),
    path('post/<int:pk>', PostDetailView.as_view(), name='post_detail'),
    path("user_profile_edit/<slug:slug>", ProfileUpdateView.as_view(), name="user_profile_edit"),
    path("bookmarks", BookmarksListView.as_view(), name="bookmarks"),
    path("notifications", NotificationListView.as_view(), name="notifications"),
    path('__debug__/', include('debug_toolbar.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
