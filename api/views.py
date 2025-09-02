from django.shortcuts import render
from django.http import JsonResponse
from api.models import User,Todo

from api.serializer import MyTokenObtainPairSerializer, RegisterSerializer,TodoSerializer,CookieTokenRefreshSerializer

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.views import TokenRefreshView


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        tokens = serializer.validated_data
        access_token = tokens.get("access")
        refresh_token = tokens.get("refresh")

        response = Response({
            "message": "Login successful",
            "user": serializer.user.username,
        }, status=status.HTTP_200_OK)

        # Set HttpOnly cookies
        response.set_cookie(
            key="access",
            value=access_token,
            httponly=True,
            secure=True,       # only over HTTPS in production
            samesite="None", # CSRF protection
            max_age=60 * 5     # match access token lifetime
        )
        response.set_cookie(
            key="refresh",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="None",
            max_age=60 * 60 * 24 * 7  # match refresh token lifetime
        )

        return response


class CookieTokenRefreshView(TokenRefreshView):
    serializer_class = CookieTokenRefreshSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


# Get All Routes

@api_view(['GET'])
def getRoutes(request):
    routes = [
        '/api/token/',
        '/api/register/',
        '/api/token/refresh/'
    ]
    return Response(routes)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def testEndPoint(request):
    if request.method == 'GET':
        # Get all users and return their usernames
        users = User.objects.all().values('id', 'username', 'email')
        return Response(users, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        text = "Hello Buddy!"
        data = f'Congratulations! Your API just responded to POST request with text: {text}'
        return Response({'response': data}, status=status.HTTP_200_OK)

    return Response({}, status=status.HTTP_400_BAD_REQUEST)

class TodoListView(generics.ListCreateAPIView):
    queryset = Todo.objects.all()
    serializer_class = TodoSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = User.objects.get(id=user_id)

        todo = Todo.objects.filter(user=user) 
        return todo


class TodoDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TodoSerializer

    def get_object(self):
        user_id = self.kwargs['user_id']
        todo_id = self.kwargs['todo_id']

        user = User.objects.get(id=user_id)
        todo = Todo.objects.get(id=todo_id, user=user)

        return todo


class TodoMarkAsCompleted(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TodoSerializer

    def get_object(self):
        user_id = self.kwargs['user_id']
        todo_id = self.kwargs['todo_id']

        user = User.objects.get(id=user_id)
        todo = Todo.objects.get(id=todo_id, user=user)

        todo.completed = True
        todo.save()

        return todo