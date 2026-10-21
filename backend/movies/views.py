from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Film
from .serializers import FilmSerializer

@api_view(['GET'])
def film_list(request):
    films = Film.objects.all()
    
    serializer = FilmSerializer(films, many=True)
    
    return Response(serializer.data)
