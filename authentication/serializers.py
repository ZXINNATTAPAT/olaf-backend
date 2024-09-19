from rest_framework import serializers
from blog.models import User
from django.contrib.auth import authenticate

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)  # Only include this field for input

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'phone', 'email', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password') 
        user = User(**validated_data)  
        user.set_password(password)  
        user.save()  
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        
        print(f'Attempting login with username: {username} and password: {password}')

        user = authenticate(username=username, password=password)
        
        if user is None:
            raise serializers.ValidationError("Invalid credentials")
        
        return {
            'user': user
        }