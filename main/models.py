# main/models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group
from django.utils import timezone
from django.conf import settings
import secrets


class User_groups(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    group_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.user.username} - {self.group_name}"


class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None, role=0, status=0):
        if not email:
            raise ValueError("Users must have an email address")

        email = self.normalize_email(email)
        user = self.model(email=email, name=name, role=role, status=status)
        user.set_password(password)  # hashes password properly
        user.save(using=self._db)

        # Attach group; be tolerant so migrations don't fail
        try:
            if role == 0:       # Student
                group, _ = Group.objects.get_or_create(name="Student")
            elif role == 1:     # Organizer
                group, _ = Group.objects.get_or_create(name="Organizer")
            elif role == 2:     # Admin
                group, _ = Group.objects.get_or_create(name="Administrator")
            else:
                group = None

            if group:
                user.groups.add(group)
        except Exception:
            # If auth tables aren't migrated yet, don't crash user creation
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
    password = models.CharField(max_length=128)   # 128 for password hashes
    role = models.IntegerField(choices=ROLE_CHOICES, default=0)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    # required for Django admin
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    def __str__(self):
        return f"{self.name} ({self.get_role_display()})"


# -------------------
# TICKET MODEL
# -------------------
class Ticket(models.Model):
    event = models.ForeignKey('Event', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    purchase_date = models.DateTimeField(default=timezone.now)

    # === QR / Scan / Check-in fields (nullable to avoid breaking teammates) ===
    qr_token = models.CharField(max_length=64, unique=True, null=True, blank=True, db_index=True)
    claimed_at = models.DateTimeField(null=True, blank=True)
    first_scanned_at = models.DateTimeField(null=True, blank=True)
    last_scanned_at = models.DateTimeField(null=True, blank=True)
    scan_count = models.PositiveIntegerField(default=0)
    checked_in_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('event', 'user')  # each user can only have 1 ticket per event

    def __str__(self):
        return f"{self.user.name} - {self.event.title}"

    # ---- helpers used by views ----
    def ensure_qr_token(self):
        if not self.qr_token:
            # ~32 urlsafe chars; unguessable and compact QR
            self.qr_token = secrets.token_urlsafe(24)

    def mark_claimed(self):
        if not self.claimed_at:
            self.claimed_at = timezone.now()
        self.ensure_qr_token()

    def record_scan(self):
        now = timezone.now()
        if not self.first_scanned_at:
            self.first_scanned_at = now
        self.last_scanned_at = now
        self.scan_count = (self.scan_count or 0) + 1

    def mark_checked_in(self):
        if not self.checked_in_at:
            self.checked_in_at = timezone.now()


# -------------------
# EVENT MODEL
# -------------------
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

    # Optional – used for student filtering
    category = models.CharField(max_length=100, blank=True, default="")

    ticket_type = models.CharField(max_length=20, choices=TICKET_TYPES, default='free')
    status = models.CharField(max_length=20, choices=EVENT_STATUS, default='draft')

    attendees = models.ManyToManyField(
        User,
        through='Ticket',
        related_name='events_attending',
        blank=True,
    )

    organizer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="organized_events",
        limit_choices_to={'role': 1}
    )

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def available_spots(self):
        return self.capacity - self.attendees.count()

    def attendee_info(self):
        """Return a list of dicts with attendee details including purchase date."""
        tickets = Ticket.objects.filter(event=self).select_related("user")
        return [
            {
                'full_name': t.user.name,
                'email': t.user.email,
                'purchase_date': t.purchase_date.strftime("%Y-%m-%d %H:%M"),
            }
            for t in tickets
        ]

    def __str__(self):
        return self.title


# -------------------
# SAVED EVENT (deduplicated – single definition)
# -------------------
class SavedEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saved_events")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="saved_by")
    remind_me = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "event")

    def __str__(self):
        return f"{self.user.email} → {self.event.title}"


class Payment(models.Model):
    STATUS_CHOICES = (
        ("succeeded", "Succeeded"),
        ("failed", "Failed"),
        ("pending", "Pending"),
    )
    user       = models.ForeignKey("main.User", on_delete=models.CASCADE, related_name="payments")
    event      = models.ForeignKey("main.Event", on_delete=models.CASCADE, related_name="payments")
    amount     = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    status     = models.CharField(max_length=16, choices=STATUS_CHOICES, default="succeeded")
    txn_id     = models.CharField(max_length=64, blank=True)  # fake transaction id
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("user", "event")  # 1 payment per user per event

    def __str__(self):
        return f"{self.user_id}:{self.event_id} {self.status} {self.amount}"
