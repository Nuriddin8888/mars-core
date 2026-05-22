from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager
)
from django.utils import timezone
import random
import string


# =====================================
# HELPERS
# =====================================

def generate_student_login():
    while True:

        login_id = str(
            random.randint(100000, 999999)
        )

        if not User.objects.filter(
            student_id=login_id
        ).exists():

            return login_id


def generate_random_password():

    chars = (
        string.ascii_letters +
        string.digits
    )

    return ''.join(
        random.choice(chars)
        for _ in range(8)
    )


def generate_group_name(direction):

    prefixes = {
        'frontend': 'nF',
        'backend': 'nB',
        'beginner': 'nBG',
    }

    prefix = prefixes.get(direction, 'GR')

    while True:

        number = random.randint(100, 999)

        group_name = f"{prefix}-{number}"

        if not Group.objects.filter(
            name=group_name
        ).exists():

            return group_name


# =====================================
# USER MANAGER
# =====================================

class UserManager(BaseUserManager):

    def create_user(
        self,
        phone_number,
        password=None,
        **extra_fields
    ):

        if not phone_number:
            raise ValueError(
                "Phone number is required"
            )

        user = self.model(
            phone_number=phone_number,
            **extra_fields
        )

        user.set_password(password)

        user.save(using=self._db)

        return user

    def create_superuser(
        self,
        phone_number,
        password=None,
        **extra_fields
    ):

        extra_fields.setdefault(
            'is_staff',
            True
        )

        extra_fields.setdefault(
            'is_superuser',
            True
        )

        extra_fields.setdefault(
            'role',
            'admin'
        )

        return self.create_user(
            phone_number,
            password,
            **extra_fields
        )


# =====================================
# USER
# =====================================

class User(
    AbstractBaseUser,
    PermissionsMixin
):

    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
    )

    full_name = models.CharField(
        max_length=255
    )

    phone_number = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True
    )

    student_id = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    is_staff = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        default=timezone.now
    )

    objects = UserManager()

    USERNAME_FIELD = 'phone_number'

    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):

        if (
            self.role == 'student'
            and not self.student_id
        ):

            self.student_id = (
                generate_student_login()
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name


# =====================================
# ROOM
# =====================================

class Room(models.Model):

    name = models.CharField(
        max_length=100
    )

    capacity = models.PositiveIntegerField(
        default=10
    )

    def __str__(self):
        return self.name


# =====================================
# TEACHER
# =====================================

class Teacher(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    specialization = models.CharField(
        max_length=255,
        blank=True
    )

    def __str__(self):
        return self.user.full_name


# =====================================
# GROUP
# =====================================

class Group(models.Model):

    DIRECTION_CHOICES = (
        ('frontend', 'Frontend'),
        ('backend', 'Backend'),
        ('beginner', 'Beginner'),
    )

    name = models.CharField(
        max_length=20,
        unique=True,
        blank=True
    )

    direction = models.CharField(
        max_length=50,
        choices=DIRECTION_CHOICES
    )

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True
    )

    room = models.ForeignKey(
        Room,
        on_delete=models.SET_NULL,
        null=True
    )

    start_date = models.DateField()

    end_date = models.DateField(
        null=True,
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    def save(self, *args, **kwargs):

        if not self.name:

            self.name = generate_group_name(
                self.direction
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# =====================================
# STUDENT
# =====================================

class Student(models.Model):

    STATUS_CHOICES = (
        ('active', 'Active'),
        ('frozen', 'Frozen'),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    avatar = models.ImageField(
        upload_to='students/',
        null=True,
        blank=True
    )

    parent_phone = models.CharField(
        max_length=20,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )

    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    joined_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.user.full_name


# =====================================
# LESSON SCHEDULE
# =====================================

class LessonSchedule(models.Model):

    WEEK_DAYS = (
        (1, 'Monday'),
        (2, 'Tuesday'),
        (3, 'Wednesday'),
        (4, 'Thursday'),
        (5, 'Friday'),
        (6, 'Saturday'),
    )

    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE
    )

    week_day = models.IntegerField(
        choices=WEEK_DAYS
    )

    start_time = models.TimeField()

    end_time = models.TimeField()

    def __str__(self):
        return self.group.name


# =====================================
# ATTENDANCE
# =====================================

class Attendance(models.Model):

    STATUS_CHOICES = (
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE
    )

    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE
    )

    date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES
    )

    comment = models.TextField(
        blank=True
    )

    class Meta:

        unique_together = (
            'student',
            'group',
            'date'
        )

    def __str__(self):

        return (
            f"{self.student} - "
            f"{self.date}"
        )
    


