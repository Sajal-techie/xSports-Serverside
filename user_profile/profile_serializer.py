from rest_framework.serializers import ModelSerializer,Serializer
from rest_framework import serializers

class ImageSerializer(Serializer):
    image = serializers.ImageField(required=False)
 