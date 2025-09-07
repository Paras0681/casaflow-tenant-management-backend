from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .serializers import TenantsProfileSerializer
from apps.users.models import Account, User
from .models import TenantsFiles
from .serializers import TenantsFilesSerializer
from django.shortcuts import get_object_or_404
from .models import Room
from cloudinary.uploader import destroy as cloudinary_destroy

# View to handle fetching Tenants Profile creation and update
class TenantsProfilesAPIView(APIView):
    permission_classes = [IsAuthenticated]
    lookup_field = 'account_id'

    def get(self, request):
        tenants = Account.objects.all()
        serializer = TenantsProfileSerializer(tenants, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request, account_id=None):
        try:
            tenant = Account.objects.get(account_id=account_id)
        except Account.DoesNotExist:
            return Response({"error": "Tenant not found."}, status=status.HTTP_404_NOT_FOUND)
        allowed_fields = ['first_name', 'last_name', 'phone_number', 'email', 'occupation', 'room_number']
        request_data = {}
        for key, value in request.data.items():
            if key in allowed_fields:
                request_data[key] = value
        serializer = TenantsProfileSerializer(tenant, data=request_data, partial=True, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class TenantsFilesListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        files = TenantsFiles.objects.all().order_by('-uploaded_at')
        if not user.is_staff:
            account = Account.objects.filter(user=request.user).first()
            if not account:
                return Response(
                    {"error": "No account for this user."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            files = TenantsFiles.objects.filter(
                room__room_number=account.room_number
            ).order_by('-uploaded_at')
        serializer = TenantsFilesSerializer(files, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, id): 
        file_id = id
        file = get_object_or_404(TenantsFiles, id=file_id)
        if not file_id:
            return Response({"error": "File ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            tenants_file = TenantsFiles.objects.get(id=file_id)
            if file.public_id:  
                cloudinary_destroy(file.public_id)
                tenants_file.delete()
                return Response({"message": "File deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

        except TenantsFiles.DoesNotExist:
            return Response({"error": "File not found."}, status=status.HTTP_404_NOT_FOUND)
    
class TenantsFilesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        file = request.FILES.get("file")
        file_type = request.data.get("file_type")
        room_number = request.data.get("room_number")
        description = request.data.get("description", "")
        unit_reading = request.data.get("unit_reading", None)
        if not file or not file_type or not room_number:
            return Response(
                {"error": "file, file_type, and room_number are required."},
                status=400
            )
        try:
            room = Room.objects.get_or_create(room_number=room_number)
        except Room.DoesNotExist:
            return Response({"error": "Invalid room number."}, status=404)
        try:
            account = Account.objects.get(user=user)
        except Account.DoesNotExist:
            return Response({"error": "No account associated with this user."}, status=404)
        tenants_file = TenantsFiles.objects.create(
            account=account,
            room=room[0],
            file=file,
            file_type=file_type.lower(),
            description=description,
            unit_reading=unit_reading if unit_reading else None,
        )
        return Response({
            "id": tenants_file.id,
            "room": tenants_file.room.room_number,
            "file": tenants_file.file,
            "file_type": tenants_file.file_type,
            "description": tenants_file.description,
            "unit_reading": tenants_file.unit_reading,
            "uploaded_at": tenants_file.uploaded_at
        }, status=201)
     