from rest_framework import serializers, status
from .models import User
from django.contrib.auth import authenticate


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id", "email")


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField()
    tokens = serializers.CharField(max_length=100, min_length=6, read_only=True)
    class Meta:
        model = User
        fields = ['email', 'password','name', 'tokens']

    def validate(self, attrs):
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError('Email already exists')
        return attrs

    def create(self, validated_data):
        print(validated_data['password'])
        user = User.objects.create_user(
            email=validated_data['email'],
            name = validated_data['name'],
            password=validated_data['password']
        )
        user.save()
        return user


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    tokens = serializers.CharField(max_length=100, min_length=6, read_only=True)
    password = serializers.CharField(write_only=True, max_length=100, min_length=4, required=True)

    class Meta:
        model = User
        fields = ['email','tokens','password']


    def validate(self, attrs):
        email = attrs.get('email',None)
        password = attrs.get('password',None)

        if not authenticate(email=email,password=password):
            raise serializers.ValidationError('Email or password is invalid')

        user = User.objects.filter(email=email).first()

        return {
            'email':user.email,
            'tokens':user.tokens(),
        }


