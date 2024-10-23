from rest_framework import generics
from .serializers import LoginSerializer, RegistrationSerializer
from .models import User
from rest_framework.response import Response
from rest_framework import status
from .utils import error

class RegisterView(generics.GenericAPIView):
    serializer_class = RegistrationSerializer

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status= status.HTTP_200_OK)
        return Response(error(serializer.errors), status= status.HTTP_400_BAD_REQUEST)


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(error(serializer.errors), status=status.HTTP_400_BAD_REQUEST)
