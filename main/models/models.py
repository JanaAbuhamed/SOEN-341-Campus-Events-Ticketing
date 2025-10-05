from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None, role=0, status=0):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, role=role, status=status)
        user.set_password(password)  # hashes password properly
        user.save(using=self._db)
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

    user_id = models.AutoField(primary_key=True)  # matches your DB PK
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=50, unique=True)
    password = models.CharField(max_length=128)   # must be 128 for password hashes
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

# EVENT MODEL

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

    ticket_type = models.CharField(
        max_length = 20, 
        choices = TICKET_TYPES, 
        default = 'free'
    )
    
    status = models.CharField(
        max_length = 20,
        choices = EVENT_STATUS,
        default = 'draft'
    )

    attendees = models.ManyToManyField(
        User, 
        related_name = "events_attending",
        blank = True  
    )
    
    organizer = models.ForeignKey(
        User,
        on_delete = models.CASCADE,
        related_name = "organized_events",
        limit_choices_to={'role': 1}
    )
    
    created_at = models.DateTimeField(default = timezone.now)
    updated_at = models.DateTimeField(auto_now = True)

    def available_spots(self):
        return self.capacity - self.attendees.count()

    def __str__(self):
        return self.title
    