from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Student, Group
import random
import string


# =====================================
# HELPERS
# =====================================

def generate_random_password():

    chars = (
        string.ascii_letters +
        string.digits
    )

    return ''.join(
        random.choice(chars)
        for _ in range(8)
    )


# =====================================
# REGISTER
# =====================================

class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True
    )

    class Meta:

        model = User

        fields = (
            'full_name',
            'phone_number',
            'password',
            'role',
        )

    def validate_role(self, value):

        if value == 'student':
            raise serializers.ValidationError(
                "Students cannot register"
            )

        return value

    def create(self, validated_data):

        password = validated_data.pop(
            'password'
        )

        user = User.objects.create_user(
            **validated_data
        )

        user.set_password(password)

        if user.role == 'admin':
            user.is_staff = True

        user.save()

        return user


# =====================================
# LOGIN
# =====================================

class LoginSerializer(serializers.Serializer):

    login = serializers.CharField()

    password = serializers.CharField(
        write_only=True
    )

    def validate(self, attrs):

        login = attrs.get('login')
        password = attrs.get('password')

        user = None

        # =========================
        # STUDENT LOGIN
        # =========================

        if login.isdigit():

            try:

                user = User.objects.get(
                    student_id=login
                )

            except User.DoesNotExist:

                raise serializers.ValidationError(
                    "Student not found"
                )

        # =========================
        # PHONE LOGIN
        # =========================

        else:

            try:

                user = User.objects.get(
                    phone_number=login
                )

            except User.DoesNotExist:

                raise serializers.ValidationError(
                    "User not found"
                )

        # =========================
        # PASSWORD CHECK
        # =========================

        if not user.check_password(password):

            raise serializers.ValidationError(
                "Invalid password"
            )

        if not user.is_active:

            raise serializers.ValidationError(
                "User inactive"
            )

        attrs['user'] = user

        return attrs


# =====================================
# STUDENT CREATE
# =====================================

class StudentCreateSerializer(
    serializers.ModelSerializer
):

    full_name = serializers.CharField(
        write_only=True
    )

    class Meta:

        model = Student

        fields = (
            'full_name',
            'avatar',
            'parent_phone',
            'group',
        )

    def create(self, validated_data):

        full_name = validated_data.pop(
            'full_name'
        )

        password = generate_random_password()

        user = User.objects.create_user(
            full_name=full_name,
            role='student',
            password=password,
        )

        student = Student.objects.create(
            user=user,
            **validated_data
        )

        student.generated_password = password

        return student
    




# =====================================
# GROUP CREATE
# =====================================

class GroupSerializer(serializers.ModelSerializer):

    class Meta:

        model = Group

        fields = (
            'id',
            'name',
            'direction',
            'teacher',
            'room',
            'start_date',
            'end_date',
            'is_active',
        )

        read_only_fields = (
            'name',
        )



