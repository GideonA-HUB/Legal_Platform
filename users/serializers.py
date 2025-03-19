from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from .models import ClientProfile, LawyerProfile

User = get_user_model()

# User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_client', 'is_lawyer']

# Register Serializer
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'is_client', 'is_lawyer']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        user.is_client = validated_data.get('is_client', False)
        user.is_lawyer = validated_data.get('is_lawyer', False)
        user.save()
        return user

# Login Serializer
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password.")

        # Authenticate using username instead of email
        user = authenticate(username=user.username, password=password)

        if not user:
            raise serializers.ValidationError("Invalid email or password.")
        
        return {"user": user}

# Client Profile Serializer
class ClientProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = ClientProfile
        fields = ['id', 'user', 'address']
        read_only_fields = ["id", "user"]

# Lawyer Profile Serializer
class LawyerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = LawyerProfile
        fields = ['id', 'user', 'specialization', 'license_number', 'verified', 'address']
        read_only_fields = ["id", "user"]  # This prevents users from changing the owner



