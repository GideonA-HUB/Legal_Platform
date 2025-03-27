from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError
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
from .models import Consultation, Notification, Review
from datetime import datetime
from rest_framework import serializers
from django.shortcuts import get_object_or_404
from .serializers import (
    ClientProfileSerializer,
    LawyerProfileSerializer,
    UserSerializer,
    RegisterSerializer,
    LoginSerializer,
    BookingSerializer,
    ConsultationSerializer,
    NotificationSerializer,
    ReviewSerializer,
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

class ConsultationListCreateView(generics.ListCreateAPIView):
    """List all consultations and create a new consultation"""
    queryset = Consultation.objects.all()
    serializer_class = ConsultationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Ensure only clients can create consultations
        if not hasattr(self.request.user, 'clientprofile'):
            raise ValidationError({"error": "Only clients can schedule consultations."})

        serializer.save(client=self.request.user.clientprofile)

class ConsultationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a consultation"""
    queryset = Consultation.objects.all()
    serializer_class = ConsultationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter consultations based on user type"""
        user = self.request.user
        if hasattr(user, 'clientprofile'):
            return Consultation.objects.filter(client=user.clientprofile)
        elif hasattr(user, 'lawyerprofile'):
            return Consultation.objects.filter(lawyer=user.lawyerprofile)
        return Consultation.objects.none()
    

class ConsultationStatusUpdateView(generics.UpdateAPIView):
    """Allow a lawyer to confirm or cancel a consultation"""
    queryset = Consultation.objects.all()
    serializer_class = ConsultationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        consultation = self.get_object()
        
        # Ensure only the lawyer can change the status
        if request.user != consultation.lawyer.user:
            return Response({"error": "You are not authorized to change this consultation's status."}, status=status.HTTP_403_FORBIDDEN)
        
        new_status = request.data.get("status")
        if new_status not in ["confirmed", "canceled"]:
            return Response({"error": "Invalid status value"}, status=status.HTTP_400_BAD_REQUEST)

        consultation.status = new_status
        consultation.save()

        # Create notification for the client
        Notification.objects.create(
            recipient=consultation.client.user,
            message=f"Your consultation with {consultation.lawyer.user.username} has been {new_status}."
        )

        return Response({"message": f"Consultation {new_status} successfully!"}, status=status.HTTP_200_OK)

class ConsultationRescheduleView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            consultation = Consultation.objects.get(id=pk, client=request.user.clientprofile)
        except Consultation.DoesNotExist:
            return Response({"error": "Consultation not found or not accessible"}, status=status.HTTP_404_NOT_FOUND)

        new_date_str = request.data.get("date")
        new_time_str = request.data.get("time")

        if not new_date_str or not new_time_str:
            return Response({"error": "Both date and time are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Convert date string to a date object before comparison
        try:
            new_date = datetime.strptime(new_date_str, "%Y-%m-%d").date()
            new_time = datetime.strptime(new_time_str, "%H:%M:%S").time()
        except ValueError:
            return Response({"error": "Invalid date or time format"}, status=status.HTTP_400_BAD_REQUEST)

        #  Ensure new date is in the future
        if new_date < datetime.today().date():
            return Response({"error": "New consultation date must be in the future"}, status=status.HTTP_400_BAD_REQUEST)

        #  Update consultation
        consultation.date = new_date
        consultation.time = new_time
        consultation.status = "pending"  # Reset status to pending after rescheduling
        consultation.save()

        # Notify the lawyer about the rescheduling
        Notification.objects.create(
            recipient=consultation.lawyer.user,
            message=f"Your consultation with {consultation.client.user.username} has been rescheduled to {new_date} at {new_time}."
        )

        return Response({"message": "Consultation rescheduled successfully!"}, status=status.HTTP_200_OK)

class NotificationListView(generics.ListAPIView):
    """Retrieve notifications for the logged-in user"""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).order_by('-created_at')

class ReviewListCreateView(generics.ListCreateAPIView):
    """Clients can create reviews, and everyone can list them"""
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Review.objects.all()

    def perform_create(self, serializer):
        consultation = serializer.validated_data.get("consultation")
        if consultation:
            lawyer = consultation.lawyer  # Retrieve the lawyer from the consultation
            serializer.save(client=self.request.user.clientprofile, lawyer=lawyer)
        else:
            raise serializers.ValidationError({"consultation": "A valid consultation is required."})


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Clients can update/delete their reviews"""
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Review.objects.filter(client=self.request.user.clientprofile)
