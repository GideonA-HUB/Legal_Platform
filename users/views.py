from rest_framework import generics, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
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
from .models import Booking
from django.shortcuts import get_object_or_404
from .serializers import (
    ClientProfileSerializer,
    LawyerProfileSerializer,
    UserSerializer,
    RegisterSerializer,
    LoginSerializer,
    BookingSerializer
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
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['specialization', 'address', 'user__is_verified', 'location']
    search_fields = ['user__username', 'specialization', 'location']
    ordering_fields = ['experience', 'user__username', 'verified', 'specialization']


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

class MatchLawyersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Get the authenticated user's client profile
        try:
            client_profile = ClientProfile.objects.get(user=request.user)
        except ClientProfile.DoesNotExist:
            return Response({"error": "Client profile not found"}, status=400)

        # Find lawyers in the same city
        matching_lawyers = LawyerProfile.objects.filter(city=client_profile.city, verified=True)

        # Serialize and return results
        serializer = LawyerProfileSerializer(matching_lawyers, many=True)
        return Response(serializer.data, status=200)
    
class CreateBookingView(generics.CreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(client=self.request.user, status='pending')


class ListClientBookingsView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(client=self.request.user)


class ListLawyerBookingsView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(lawyer=self.request.user)


class UpdateBookingStatusView(generics.UpdateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(lawyer=self.request.user)

    def perform_update(self, serializer):
        status = self.request.data.get("status", None)
        if status and status in ['confirmed', 'canceled']:
            serializer.save()
        else:
            return Response({"error": "Invalid status"}, status=400) 

class DeleteBookingView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id, *args, **kwargs):
        booking = get_object_or_404(Booking, id=id)

        # Ensure only the client who created the booking can delete it
        if booking.client != request.user:
            return Response({"error": "You can only delete your own bookings."}, status=status.HTTP_403_FORBIDDEN)

        booking.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)           