from rest_framework.response import Response
from .models import Note
from .serializers import NoteSerializer

def getNotesList(request, device_id):
    if device_id:
        notes = Note.objects.filter(device_id=device_id).order_by('-updated')
    else:
        notes = Note.objects.all().order_by('-updated')
    serializer = NoteSerializer(notes, many=True)
    return Response(serializer.data)

def getNoteDetail(request, pk, device_id):
    try:
        if device_id:
            note = Note.objects.get(id=pk, device_id=device_id)
        else:
            note = Note.objects.get(id=pk)
    except Note.DoesNotExist:
        return Response(status=404)
    serializer = NoteSerializer(note, many=False)
    return Response(serializer.data)

def createNote(request, device_id):
    data = request.data
    note = Note.objects.create(
        body=data['body'],
        device_id=device_id  # Save device_id with the note
    )
    serializer = NoteSerializer(note, many=False)
    return Response(serializer.data)

def updateNote(request, pk, device_id):
    data = request.data
    try:
        if device_id:
            note = Note.objects.get(id=pk, device_id=device_id)
        else:
            note = Note.objects.get(id=pk)
    except Note.DoesNotExist:
        return Response(status=404)
    note.body = data['body']
    note.save()
    serializer = NoteSerializer(note, many=False)
    return Response(serializer.data)

def deleteNote(request, pk, device_id):
    try:
        if device_id:
            note = Note.objects.get(id=pk, device_id=device_id)
        else:
            note = Note.objects.get(id=pk)
    except Note.DoesNotExist:
        return Response(status=404)
    note.delete()
    return Response('Note was deleted!')



