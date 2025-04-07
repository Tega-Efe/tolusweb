from django.shortcuts import render
from .serializers import NoteSerializer
from .models import Note
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .utils import *

@api_view(['GET'])
def getRoutes(request):
    routes = [
        {
            'Endpoint': '/notes/',
            'method': 'GET',
            'body': None,
            'description': 'Returns an array of notes'
        },
        {
            'Endpoint': '/notes/id',
            'method': 'GET',
            'body': None,
            'description': 'Returns a single note object'
        },
        {
            'Endpoint': '/notes/create/',
            'method': 'POST',
            'body': {'body': ""},
            'description': 'Creates new note with data sent in post request'
        },
        {
            'Endpoint': '/notes/id/update/',
            'method': 'PUT',
            'body': {'body': ""},
            'description': 'Creates an existing note with data sent in post request'
        },
        {
            'Endpoint': '/notes/id/delete/',
            'method': 'DELETE',
            'body': None,
            'description': 'Deletes an existing note'
        },
    ]
    return Response(routes)

@api_view(['GET', 'POST'])
def getNotes(request):
    device_id = request.headers.get('X-Device-ID')
    if request.method == 'GET':
        return getNotesList(request, device_id)

    if request.method == 'POST':
        return createNote(request, device_id)

@api_view(['GET', 'PUT', 'DELETE'])
def getNote(request, pk):
    device_id = request.headers.get('X-Device-ID')
    if request.method == 'GET':
        return getNoteDetail(request, pk, device_id)

    if request.method == 'PUT':
        return updateNote(request, pk, device_id)

    if request.method == 'DELETE':
        return deleteNote(request, pk, device_id)


