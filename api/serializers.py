import re
from rest_framework import serializers
from main import settings
from todo.models import Todo

import imghdr

from rest_framework import serializers
from .models import CustomUser

def validate_image_file(value):
    # You can use any logic to validate the image file format
    # For example, use the imghdr module to check the file header
    file_type = imghdr.what(value)
    if file_type not in ['jpeg', 'png', 'gif']:
        raise serializers.ValidationError('Invalid image file format.')
    return value    

def validate_mobile_number(value):
    # You can use any regex pattern to match your desired phone number format
    # For example, this pattern matches a 10-digit number with optional hyphens
    pattern = r'^\d{4}-?\d{3}-?\d{4}$'
    if not re.match(pattern, value):
        raise serializers.ValidationError('Invalid mobile number format.')
    return value



class CustomUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    is_active = serializers.BooleanField(source='user.is_active', read_only=True)
    last_login = serializers.DateTimeField(source='user.last_login', read_only=True)
    profile_pic = serializers.ImageField(max_length=None, use_url=True, required=False)

    class Meta:
        model = CustomUser
        fields = ['mobile', 'profile_pic', 'username', 'is_active', 'last_login']

    def validate_mobile(self, value):
        # validate mobile number format
        return validate_mobile_number(value)

    def validate_profile_pic(self, value):
        # validate profile pic file size
        return validate_image_file(value)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        if representation['profile_pic']:
            if request is not None:
                representation['profile_pic'] = request.build_absolute_uri(representation['profile_pic'])
            else:
                representation['profile_pic'] = f"{settings.BASE_URL}{representation['profile_pic']}"
        return representation

class TodoSerializer(serializers.ModelSerializer):
    created = serializers.ReadOnlyField()
    completed = serializers.ReadOnlyField()
    class Meta:
        model = Todo
        fields = ['id','title','memo','created','completed']


class TodoToggleCompleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Todo
        fields = ['id'] # why need to show id?
        read_only_fields = ['title','memo','created','completed']
