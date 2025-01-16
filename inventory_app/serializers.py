from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.models import User

class RegistrationSerializer(serializers.ModelSerializer):
    
    
    class Meta:
        model = User
        fields = ['username','email','password']
        
        extra_kwargs = {'password': {'write_only': True}}
        
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user