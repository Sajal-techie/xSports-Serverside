from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView


# Create your views here.

from django.http import HttpResponse
  
class Index(APIView):
    def get(self, request):
        print(request)
        return Response({'hello':'haii'})