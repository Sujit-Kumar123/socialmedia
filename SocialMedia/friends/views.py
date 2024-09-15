from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404 
from rest_framework import status
from .models import CustomUser,Post,PostLike,PostComment,UserFollow
from .serializers import UserSerializer, LoginSerializer,PostSerializer,CommentSerializer,PostLikeSerializer,UserFollowSerializer
from rest_framework.permissions import AllowAny
from django.http import Http404
from .decorators import validate_token

from rest_framework_simplejwt.tokens import RefreshToken


class UserCreateAPIView(APIView):
    def post(self, request, format='json'):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def get(self, request, format='json'):
        users = CustomUser.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
class UserLoginAPIView(APIView):
    permission_classes = []
    authentication_classes = []
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({'refresh': str(refresh), 'access': str(refresh.access_token)}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Create your views here.
# Post API
class PostAPIView(APIView):
    @validate_token
    def get(self, request, format='json'):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @validate_token
    def post(self, request, format='json'):
        # print("req",request)
        serializer = PostSerializer(data=request.data,context={'request': request})
        print(serializer)
        # print("request.user",request.user)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @validate_token
    def put(self, request, pk, format='json'):
        post = get_object_or_404(Post, pk=pk)
        serializer = PostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @validate_token
    def delete(self, request, pk, format='json'):
        print(pk,"pk")
        post = get_object_or_404(Post, pk=pk)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
# Post Comment API
class PostCommentAPIView(APIView):
    @validate_token
    def get(self, request, post_id, format='json'):
        comments = PostComment.objects.filter(post_id=post_id)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @validate_token
    def post(self, request, post_id, format='json'):
        serializer = CommentSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user, post_id=post_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    @validate_token
    def put(self, request, post_id, comment_id, format='json'):
        comment = get_object_or_404(PostComment, id=comment_id, post_id=post_id)
        serializer = CommentSerializer(comment, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            if comment.user == request.user:
                serializer.save(user=request.user, post_id=post_id)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({"error": "You do not have permission to update this comment."}, status=status.HTTP_403_FORBIDDEN)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @validate_token
    def delete(self, request, post_id, comment_id, format='json'):
        comment = get_object_or_404(PostComment, id=comment_id, post_id=post_id)
        if comment.user == request.user:
            comment.delete()
            return Response({"message": "Comment deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        return Response({"error": "You do not have permission to delete this comment."}, status=status.HTTP_403_FORBIDDEN)

# Post Like API
class PostLikeAPIView(APIView):
    @validate_token
    def post(self, request, post_id, format='json'):
        if PostLike.objects.filter(post_id=post_id, user=request.user).exists():
            return Response({'detail': 'Already liked this post.'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = PostLikeSerializer(data={},context={'post': post_id, 'user': request.user})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @validate_token
    def delete(self, request, post_id, format='json'):
        like = get_object_or_404(PostLike, post_id=post_id, user=request.user)
        like.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# User Follow API
class UserFollowAPIView(APIView):
    @validate_token
    def post(self, request, user_id, format='json'):
        existing_follow = UserFollow.objects.filter(user=request.user, follows_id=user_id).first()
        if existing_follow:
            if existing_follow.status == UserFollow.FOLLOW_ACCEPTED:
                return Response({'detail': 'Already following this user.'}, status=status.HTTP_400_BAD_REQUEST)
            elif existing_follow.status == UserFollow.FOLLOW_REQUESTED:
                return Response({'detail': 'Follow request already sent.'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = {'follows': user_id}
        serializer = UserFollowSerializer(data=data, context={'request': request})
        
        if serializer.is_valid():
            serializer.save(user=request.user, status=UserFollow.FOLLOW_REQUESTED)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @validate_token
    def put(self, request, user_id, format='json'):
        follow_request = get_object_or_404(UserFollow, user=user_id, follows=request.user)
        
        if request.data.get('action') == 'accept':
            follow_request.status = UserFollow.FOLLOW_ACCEPTED
            follow_request.save()
            return Response({'detail': 'Follow request accepted.'}, status=status.HTTP_200_OK)
        elif request.data.get('action') == 'deny':
            follow_request.status = UserFollow.FOLLOW_DENIED
            follow_request.save()
            return Response({'detail': 'Follow request denied.'}, status=status.HTTP_200_OK)
        
        return Response({'detail': 'Invalid action.'}, status=status.HTTP_400_BAD_REQUEST)

    @validate_token
    def delete(self, request, user_id, format='json'):
        follow_request = get_object_or_404(UserFollow, user=request.user, follows_id=user_id)
        if follow_request.status == UserFollow.FOLLOW_ACCEPTED:
            follow_request.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'detail': 'Cannot unfollow a user without an accepted follow.'},status=status.HTTP_400_BAD_REQUEST)


