import requests
import json
from django.core.management.base import BaseCommand

BASE_URL = 'http://127.0.0.1:8000/api/notes'

def create_note(body):
    url = f"{BASE_URL}/"
    headers = {
        'Content-Type': 'application/json',
    }
    payload = {
        'body': body,
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    return response.json()

def get_note(note_id):
    url = f"{BASE_URL}/{note_id}/"
    response = requests.get(url)
    return response.json()

def update_note(note_id, body):
    url = f"{BASE_URL}/{note_id}/"
    headers = {
        'Content-Type': 'application/json',
    }
    payload = {
        'body': body,
    }
    response = requests.put(url, headers=headers, data=json.dumps(payload))
    return response.json()

def delete_note(note_id):
    url = f"{BASE_URL}/{note_id}/"
    response = requests.delete(url)
    return response.status_code

class Command(BaseCommand):
    help = 'Perform CRUD operations on notes'

    def handle(self, *args, **kwargs):
        # Example usage:
        # Create a new note
        new_note = create_note("new note")
        self.stdout.write(f"Created Note: {new_note}")

        # Get the created note
        note_id = new_note['id']
        note = get_note(note_id)
        self.stdout.write(f"Retrieved Note: {note}")

        # # Update the note
        # updated_note = update_note(note_id, "This is an updated test note")
        # self.stdout.write(f"Updated Note: {updated_note}")

        # # Delete the note
        # delete_status = delete_note(note_id)
        # self.stdout.write(f"Delete Status: {delete_status}")
