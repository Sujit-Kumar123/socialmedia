from django.urls import path
from .views import (
    UserCreateAPIView,
    UserLoginAPIView,
    PostAPIView,
    PostCommentAPIView,
    PostLikeAPIView,
    UserFollowAPIView
)

urlpatterns = [
    path('api/signup/', UserCreateAPIView.as_view(), name='user-create'),
    path('api/login/', UserLoginAPIView.as_view(), name='user-login'),
    path('api/posts/', PostAPIView.as_view(), name='post-list-create'),
    path('api/posts/<int:pk>/', PostAPIView.as_view(), name='post-detail-update-delete'),
    path('api/posts/<int:post_id>/comments/', PostCommentAPIView.as_view(), name='post-comment-list-create'),
    path('api/posts/<int:post_id>/comments/<int:comment_id>/', PostCommentAPIView.as_view(), name='comment-detail'),
    path('api/posts/<int:post_id>/likes/', PostLikeAPIView.as_view(), name='post-like'),
    path('api/users/<int:user_id>/follow/', UserFollowAPIView.as_view(), name='user-follow'),
]
