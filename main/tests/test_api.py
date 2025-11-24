from django.test import TestCase
from rest_framework.test import APIClient
from datetime import date, time
from main.models import User, Event


# --------------------------
# BASIC TESTS
# --------------------------
class TestSimple(TestCase):

    # Test: Basic math operation works
    def test_basic_math(self):
        self.assertEqual(2 + 2, 4)

    # Test: String upper() method converts correctly
    def test_string_upper(self):
        self.assertEqual("hello".upper(), "HELLO")


# --------------------------
# USER MODEL TESTS
# --------------------------
class TestUserModel(TestCase):

    # Test: Creating a user with valid data
    def test_create_user(self):
        user = User.objects.create_user(
            email="test@example.com",
            name="Test User",
            password="pass123",
            role=0,
            status=1
        )
        self.assertEqual(user.email, "test@example.com")

    # Test: Creating a user with no email should raise an error
    def test_create_user_missing_email(self):
        with self.assertRaises(Exception):
            User.objects.create_user(
                email="",
                name="No Email",
                password="pass",
                role=0,
                status=1
            )


# --------------------------
# EVENT MODEL TESTS
# --------------------------
class TestEventModel(TestCase):

    # Test: Creating an event successfully
    def test_create_event(self):
        event = Event.objects.create(
            title="Test Event",
            description="Desc",
            date=date.today(),
            time=time(12, 0),
            location="Hall A",
            capacity=50,
            ticket_type="free",
            status="approved",
            organizer=self.user,
        )
        self.assertEqual(event.capacity, 50)

    # Test: Event __str__ contains event title
    def test_event_string_representation(self):
        event = Event.objects.create(
            title="Sample Event",
            description="Desc",
            date=date.today(),
            time=time(10, 0),
            location="Hall B",
            capacity=20,
            ticket_type="paid",
            status="draft",
            organizer=self.user,
        )
        self.assertIn("Sample Event", str(event))

    def setUp(self):
        self.user = User.objects.create_user(
            email="event@test.com",
            name="Event Tester",
            password="pass123",
            role=1,
            status=1
        )




# --------------------------
# API TESTS FOR USERS & EVENTS
# --------------------------
class TestUserAndEventAPI(TestCase):

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

    # Test: Registering a new user via API
    def test_user_registration_via_api(self):
        data = {
            "email": "student@example.com",
            "name": "Student",
            "password": "studypass",
            "role": 0,
            "status": 1
        }
        res = self.client.post("/api/users/", data, format="json")
        self.assertEqual(res.status_code, 201)

    # Test: Registering a duplicate user should fail (400)
    def test_duplicate_user_registration_fails(self):
        User.objects.create_user(
            email="exists@example.com",
            name="Old",
            password="123",
            role=0,
            status=1
        )
        data = {
            "email": "exists@example.com",
            "name": "New",
            "password": "abc",
            "role": 0,
            "status": 1
        }
        res = self.client.post("/api/users/", data, format="json")
        self.assertEqual(res.status_code, 400)

    # Test: Event creation succeeds when organizer is authenticated
    def test_event_creation_by_organizer(self):
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
        res = self.client.post("/api/events/", data, format="json")
        self.assertEqual(res.status_code, 201)

    # Test: Event creation fails when user is not authenticated
    def test_event_creation_requires_authentication(self):
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
        res = self.client.post("/api/events/", data, format="json")
        self.assertEqual(res.status_code, 403)
