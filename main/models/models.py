from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group
from django.utils import timezone

# ⬇️ QR generation
import uuid
import io
import qrcode
from django.core.files.base import ContentFile


class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None, role=0, status=0):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, role=role, status=status)
        user.set_password(password)
        user.save(using=self._db)

        # Optionally add group membership (if groups exist)
        try:
            if role == 0:
                group = Group.objects.get(name='Student')
            elif role == 1:
                group = Group.objects.get(name='Organizer')
            else:
                group = Group.objects.get(name='Administrator')
            user.groups.add(group)
        except Group.DoesNotExist:
            pass

        return user

    def create_superuser(self, email, name, password=None):
        user = self.create_user(email=email, name=name, password=password, role=2, status=1)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        (0, "Student"),
        (1, "Organizer"),
        (2, "Admin"),
    ]

    STATUS_CHOICES = [
        (0, "Pending"),
        (1, "Active"),
        (2, "Suspended"),
    ]

    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=50, unique=True)
    password = models.CharField(max_length=128)
    role = models.IntegerField(choices=ROLE_CHOICES, default=0)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    def __str__(self):
        return f"{self.name} ({self.get_role_display()})"


# ------------------------
#        Events
# ------------------------
class Event(models.Model):
    TICKET_TYPES = [
        ('free', 'Free'),
        ('general', 'General Admission'),
        ('vip', 'VIP'),
    ]

    EVENT_STATUS = [
        ('draft', 'Draft'),
        ('pending', 'Pending Admin Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=200)
    capacity = models.PositiveIntegerField()

    ticket_type = models.CharField(max_length=20, choices=TICKET_TYPES, default='free')
    status = models.CharField(max_length=20, choices=EVENT_STATUS, default='draft')

    attendees = models.ManyToManyField("User", related_name="events_attending", blank=True)

    organizer = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        related_name="organized_events",
        limit_choices_to={'role': 1},
    )

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def available_spots(self):
        return self.capacity - self.attendees.count()

    def __str__(self):
        return self.title


# ------------------------
#        Tickets
# ------------------------
def qrcode_upload_path(instance, filename):
    return f"qrcodes/{filename}"

class Ticket(models.Model):
    """
    One ticket per (user, event). Generates a QR image containing a unique code.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tickets")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="tickets")
    code = models.CharField(max_length=64, unique=True, editable=False)
    qr_image = models.ImageField(upload_to=qrcode_upload_path, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    scanned_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("user", "event")
        indexes = [
            models.Index(fields=["code"]),
        ]

    def __str__(self):
        return f"Ticket {self.code[:8]}… for {self.user.email} @ {self.event.title}"

    def _ensure_code(self):
        if not self.code:
            self.code = uuid.uuid4().hex  # short, unique, URL-safe

    def _ensure_qr(self):
        """
        Generate a PNG QR image that encodes the ticket 'code'.
        (Verification endpoint will accept the code and validate.)
        """
        # Make a small QR with just the code; frontend/validator can call /api/tickets/verify/<code>/
        img = qrcode.make(self.code)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        # Save into ImageField without triggering an infinite save loop
        filename = f"{self.code}.png"
        self.qr_image.save(filename, ContentFile(buf.read()), save=False)

    def save(self, *args, **kwargs):
        self._ensure_code()
        super().save(*args, **kwargs)  # need PK for upload_to path on some storages
        if not self.qr_image:
            self._ensure_qr()
            super().save(update_fields=["qr_image"])
