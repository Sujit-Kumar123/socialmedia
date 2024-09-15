from rest_framework import serializers
from .models import CustomUser,Post,PostComment,PostLike,UserFollow
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from .validators import CustomEmailValidator
from django.contrib.auth import get_user_model


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(validators=[CustomEmailValidator()])
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username', 'phone_no', 'first_name', 'last_name', 'role', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(validators=[CustomEmailValidator()]) 
    password = serializers.CharField(style={'input_type': 'password'},trim_whitespace=False)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        print("user",email)
        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)

            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "email" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        data['user'] = user
        return data
class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = "__all__"

    title = serializers.CharField()
    description = serializers.CharField()
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def update(self, instance, validated_data):
        print(validated_data,"validated_data")
        if instance.user.id == validated_data["user"].id:
            print("validated_data['user'].id",validated_data["user"].id)
            return super().update(instance, validated_data)
        
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostComment
        fields = "__all__"

    comment_text = serializers.CharField(max_length=264)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    post = serializers.PrimaryKeyRelatedField(read_only=True)

    def save(self, **kwargs):
        post_id = kwargs.get("post_id")
        post = Post.objects.get(id=post_id)
        if self.instance is None:
            self.instance = PostComment.objects.create(
                post=post,
                user=kwargs.get("user"),
                comment_text=self.validated_data.get("comment_text"),
            )
        else:
            # Updating an existing instance
            self.instance.post = post
            self.instance.user = kwargs.get("user")
            self.instance.comment_text = self.validated_data.get("comment_text")
            self.instance.save()

        return self.instance
    
class PostLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostLike
        fields = "__all__"

    user = serializers.PrimaryKeyRelatedField(read_only=True)
    post = serializers.PrimaryKeyRelatedField(read_only=True)
    def create(self, validated_data):
        post_id = self.context.get('post')
        user = self.context.get('user')
        post = Post.objects.get(id=post_id)
        validated_data['post'] = post
        validated_data['user'] = user
        
        return super().create(validated_data)

class UserFollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFollow
        fields = "__all__"
        read_only_fields = ('user',) 

    follows = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    status = serializers.ChoiceField(choices=UserFollow.FOLLOW_STATUS_CHOICES, read_only=True)

