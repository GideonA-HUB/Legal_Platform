from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .models import ClientProfile, LawyerProfile
from .serializers import (
    ClientProfileSerializer,
    LawyerProfileSerializer,
    UserSerializer,
    RegisterSerializer,
    LoginSerializer
)

User = get_user_model()

# Register View
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

# Login View
class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            refresh = RefreshToken.for_user(user)

            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Custom permission to allow only lawyers to see clients
class IsLawyer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_lawyer

# Custom permission to allow only clients to see lawyers
class IsClient(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_client        

# Lawyers can see clients
class ClientListView(ListAPIView):
    queryset = ClientProfile.objects.all()
    serializer_class = ClientProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsLawyer]  # Only lawyers can access

# Clients can see lawyers
class LawyerListView(ListAPIView):
    queryset = LawyerProfile.objects.all()
    serializer_class = LawyerProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsClient]  # Only clients can acess

class UpdateLawyerProfileView(RetrieveUpdateAPIView):
    serializer_class = LawyerProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.lawyerprofile  # Get the logged-in user's profile

class UpdateClientProfileView(RetrieveUpdateAPIView):
    serializer_class = ClientProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.clientprofile  # Get the logged-in user's profile
