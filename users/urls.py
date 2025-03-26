from django.urls import path
from .views import (
    RegisterView, 
    LoginView, 
    ClientListView, 
    LawyerListView, 
    UpdateLawyerProfileView, 
    UpdateClientProfileView,
    CreateBookingView,
    ListClientBookingsView,
    ListLawyerBookingsView,
    UpdateBookingStatusView,
    DeleteBookingView,
)

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from users.views import MatchLawyersView



urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('clients/', ClientListView.as_view(), name='client-list'),
    path('lawyers/', LawyerListView.as_view(), name='lawyer-list'),
    path("profile/lawyer/update/", UpdateLawyerProfileView.as_view(), name="update-lawyer-profile"),
    path("profile/client/update/", UpdateClientProfileView.as_view(), name="update-client-profile"),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('match-lawyers/', MatchLawyersView.as_view(), name='match-lawyers'),
    path('bookings/create/', CreateBookingView.as_view(), name='create-booking'),
    path('bookings/client/', ListClientBookingsView.as_view(), name='client-bookings'),
    path('bookings/lawyer/', ListLawyerBookingsView.as_view(), name='lawyer-bookings'),
    path('bookings/update/<int:pk>/', UpdateBookingStatusView.as_view(), name='update-booking-status'),
    path('bookings/delete/<int:id>/', DeleteBookingView.as_view(), name='delete-booking'),
]
