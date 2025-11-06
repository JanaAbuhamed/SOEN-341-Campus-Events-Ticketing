# main/tests/test_api.py
from django.test import TestCase
from rest_framework.test import APIClient
from main.models import User, Event
from datetime import date, time
from main.models import User_groups


class SimpleTest(TestCase):
    def test_basic_math(self):
        self.assertEqual(1 + 1, 2)

class UserAndEventAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            email="admin@example.com",
            name="Admin",
            password="adminpass",
            role=2,
            status=1
        )
        self.organizer = User.objects.create_user(
            email="organizer@example.com",
            name="Organizer",
            password="organizerpass",
            role=1,
            status=1
        )

    def test_user_registration_via_api(self):
        """Test creating a new user through API"""
        data = {
            "email": "student@example.com",
            "name": "Student One",
            "password": "studypass",
            "role": 0,
            "status": 1
        }
        response = self.client.post("/api/users/", data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(email="student@example.com").exists())

    def test_event_creation_by_organizer(self):
        """Test creating an event through the Event API"""
        self.client.force_authenticate(user=self.organizer)
        data = {
            "title": "Music Fest",
            "description": "A fun music event",
            "date": date.today().isoformat(),
            "time": time(18, 0).isoformat(),
            "location": "Campus Hall",
            "capacity": 100,
            "ticket_type": "free",
            "status": "approved"
        }
        response = self.client.post("/api/events/", data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Event.objects.filter(title="Music Fest").exists())

    def test_event_creation_requires_authentication(self):
        """Ensure unauthenticated users cannot create events"""
        data = {
            "title": "Unauthorized Event",
            "description": "Should fail",
            "date": date.today().isoformat(),
            "time": time(10, 0).isoformat(),
            "location": "Nowhere",
            "capacity": 10,
            "ticket_type": "free",
            "status": "draft"
        }
        response = self.client.post("/api/events/", data, format="json")
        self.assertEqual(response.status_code, 403)
