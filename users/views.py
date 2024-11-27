from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserProfile, Wallet
from .serializers import UserSerializer, UserProfileSerializer, WalletSerializer

# User Registration View
from rest_framework.views import APIView
from rest_framework import serializers

class UserRegistrationAPIView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User registered successfully", "user_id": user.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# User Login (Token-based Authentication)
class UserLoginAPIView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"error": "Invalid username or password"}, status=status.HTTP_400_BAD_REQUEST)

        if user.check_password(password):
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        else:
            return Response({"error": "Invalid username or password"}, status=status.HTTP_400_BAD_REQUEST)

# User Profile Viewset (Already defined previously)
class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_update(self, serializer):
        profile = serializer.save()
        profile.user = self.request.user
        profile.save()

# Wallet Viewset (Already defined previously)
class WalletViewSet(viewsets.ModelViewSet):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def check_balance(self, request):
        wallet = self.get_object()
        return Response({'balance': wallet.balance})

    @action(detail=False, methods=['post'])
    def add_money(self, request):
        amount = request.data.get('amount', 0)
        wallet = self.get_object()
        wallet.balance += amount
        wallet.save()
        return Response({'balance': wallet.balance})

    @action(detail=False, methods=['patch'])
    def spend_money(self, request):
        amount = request.data.get('amount', 0)
        wallet = self.get_object()
        if wallet.balance < amount:
            return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)
        wallet.balance -= amount
        wallet.save()
        return Response({'balance': wallet.balance})
