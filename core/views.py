from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    StudentCreateSerializer,
    GroupSerializer
)


# =====================================
# REGISTER
# =====================================

class RegisterView(APIView):

    def post(self, request):

        serializer = RegisterSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        user = serializer.save()

        return Response(
            {
                'message': 'Registered successfully'
            },
            status=status.HTTP_201_CREATED
        )


# =====================================
# LOGIN
# =====================================

class LoginView(APIView):

    def post(self, request):

        serializer = LoginSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        user = serializer.validated_data[
            'user'
        ]

        refresh = RefreshToken.for_user(
            user
        )

        return Response({
            'refresh': str(refresh),
            'access': str(
                refresh.access_token
            ),
            'role': user.role,
            'full_name': user.full_name,
        })


# =====================================
# STUDENT CREATE
# =====================================

class StudentCreateView(APIView):

    def post(self, request):

        serializer = (
            StudentCreateSerializer(
                data=request.data
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        student = serializer.save()

        return Response({

            'message':
                'Student created',

            'student_id':
                student.user.student_id,

            'password':
                student.generated_password,

        })
    



class GroupCreateView(APIView):

    def post(self, request):

        serializer = GroupSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )