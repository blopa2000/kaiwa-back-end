from rest_framework import serializers
from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("email", "username", "password", "first_name", "last_name")

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )
        return user


class UserListSerializer(serializers.ModelSerializer):
    photo = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "username", "email", "photo")

    def get_photo(self, obj):
        if obj.photo:
            return obj.photo.url
        return None


class UserProfileSerializer(serializers.ModelSerializer):
    photo = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "photo",
        )
        read_only_fields = ("email",)

    def get_photo(self, obj):
        if obj.photo:
            return obj.photo.url
        return None


class UserPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["photo"]
