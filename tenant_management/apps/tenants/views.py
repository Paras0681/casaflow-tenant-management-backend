from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .serializers import TenantsProfileSerializer
from apps.users.models import Account, User
from .models import TenantsFiles, TenantsData
from .serializers import TenantsDataSerialzier, TenantsFilesSerializer, PropertySerializer,RoomSerializer
from django.shortcuts import get_object_or_404
from .models import Room, Property
from cloudinary.uploader import destroy as cloudinary_destroy
from django.db.models import Sum, Count, Q 
from apps.payments.models import Payments
from datetime import datetime

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
        files = TenantsFiles.objects.all().order_by('-uploaded_at').exclude(file_type__in=["payment_receipt", "invoice_bill"])
        if not user.is_staff:
            account = Account.objects.filter(user=request.user).first()
            if not account:
                return Response(
                    {"error": "No account for this user."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            files = TenantsFiles.objects.filter(
                account=account
            ).order_by('-uploaded_at').exclude(file_type="payment_receipt")
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
        file = request.FILES.get("file_url")
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
        tenants_file = TenantsFiles(
            account=account,
            room=room[0],
            file_url=file,
            file_type=file_type.lower(),
            description=description,
            unit_reading=unit_reading if unit_reading else None,
        )
        tenants_file.set_uploaded_file(file)
        tenants_file.save()
        return Response({
            "id": tenants_file.id,
            "room": tenants_file.room.room_number,
            "file": tenants_file.file_url,
            "file_type": tenants_file.file_type,
            "description": tenants_file.description,
            "unit_reading": tenants_file.unit_reading,
            "uploaded_at": tenants_file.uploaded_at
        }, status=201)
     
class GetReceiptsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        rooms = Room.objects.all()
        response_data = {
            "rooms":[],
            "receipts": []
        }
        for room in rooms:
            response_data["rooms"].append({
                "room": room.room_number,
                "occupants": room.active_tenants 
            })
        accounts = Account.objects.all()
        if not user.is_staff:
            accounts = Account.objects.filter(user=user)
        for accounts in accounts:
            tenants_data = accounts.tenants_data.all()
            if tenants_data.exists():
                for tenant_data in tenants_data:
                    receipt = {
                        "tenant_name": f"{tenant_data.account.first_name} {tenant_data.account.last_name}",
                        "room_number": tenant_data.room.room_number,
                        "payment_status": tenant_data.payment_status,
                        "paid_at": tenant_data.paid_at,
                        "rent_amount": tenant_data.rent_amount,
                        "lightbill_amount": tenant_data.lightbill_amount,
                        "other_charges": tenant_data.other_charges,
                        "per_tenant_share": tenant_data.per_tenant_share,
                        "invoice_id": tenant_data.invoice_id,
                        "invoice_url": tenant_data.invoice_url
                    }
                    response_data["receipts"].append(receipt)
        return Response(response_data, status=status.HTTP_200_OK)
    
class GenerateReceiptsAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        response = {"invoice_data": []}
        user = request.user
        if not user.is_staff:
            return Response({"error": "Only staff can access this endpoint."}, status=status.HTTP_403_FORBIDDEN)
        room = Room.objects.filter(room_number=request.data['room_number']).first()
        if room.active_tenants == 0:
            return Response({"message": "No Tenants in the Room yet."}, status=status.HTTP_404_NOT_FOUND)
        accounts = Account.objects.filter(room_number = request.data['room_number'])
        for account in accounts:
            room = Room.objects.filter(room_number=account.room_number).first()
            serializer = TenantsDataSerialzier(data=request.data, context={"account": account, "room": room})
            if serializer.is_valid():
                serializer.save()
                response["invoice_data"].append(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(response, status=status.HTTP_201_CREATED)


class PropertyAPIView(APIView):
    def get(self, request):
        data = Property.objects.all()
        serializer = PropertySerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = PropertySerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
class RoomAPIView(APIView):
    def get(self, request):
        rooms = Room.objects.all()
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serialzer = RoomSerializer(data=request.data)
        if serialzer.is_valid():
            serialzer.save()
            return Response(serialzer.data, status=status.HTTP_201_CREATED)
        return Response(serialzer.errors, status=status.HTTP_400_BAD_REQUEST)

class DataAnalyticsView(APIView):
    def get(self, request):
        total_revenue = Payments.objects.aggregate(total=Sum("amount"))["total"] or 0
        room_stats = Room.objects.aggregate(
            active_tenants=Sum("active_tenants"),
            max_occupants=Sum("max_occupants"),
        )
        active_tenants = room_stats["active_tenants"] or 0
        max_occupants = room_stats["max_occupants"] or 0
        vacant_beds = max_occupants - active_tenants
        pending_payments = (TenantsData.objects.filter(
            payment_status__in=["not_paid", "unpaid"]
        ).aggregate(
            total=Sum("total_amount")
        )["total"] or 0)
        payments = (
            TenantsData.objects.filter(payment_status__in = ["paid", "not_paid", "overdue"]).values(
                "payment_status"
            )
            .annotate(total=Sum("total_amount"))
        )
        piechart_data = {"paid": 0, "not_paid": 0, "overdue": 0}
        for payment in payments:
            status_key = payment["payment_status"]
            if status_key in piechart_data:
                piechart_data[payment["payment_status"]] = payment["total"] or 0
        data = {
            "card_data":{
                "total_revenue" : total_revenue,
                "active_tenants" : active_tenants,
                "pending_payments" : pending_payments,
                "vacant_beds" : vacant_beds,
            },
            "piechart_data" : piechart_data
        }
        return Response(data, status=status.HTTP_200_OK)


class YearlyDataView(APIView):
    def get(self, request):
        results = []
        if request.user.is_staff:
            payments = TenantsData.objects.filter(
                payment_status="paid"
            ).order_by("created_at")
        else:
            account = Account.objects.filter(user=request.user).first()
            payments = TenantsData.objects.filter(
                account=account,
                payment_status="paid"
            ).order_by("created_at")
        for payment in payments:
            per = payment.room.active_tenants
            rent_amount_share = payment.rent_amount/per
            lightbill_amount_share = payment.lightbill_amount/per
            other_charges_share = payment.other_charges/per
            results.append({
                "name": payment.account.first_name,
                "rent_amount": rent_amount_share,
                "lightbill_amount": lightbill_amount_share,
                "other_charges": other_charges_share,
                "created_at": payment.created_at
            })
        return Response(results, status=status.HTTP_200_OK)

class MarkInvoiceAPIView(APIView):
    def post(self, request):
        if request.user.is_staff:
            invoice_id = request.data["invoice_id"]
            tenants_data = TenantsData.objects.filter(invoice_id=invoice_id)
            tenants_data.payment_status = "paid"
            payment = Payments.objects.filter(invoice_id=invoice_id)
            if payment:
                marked_paid_at = datetime.now()
                payment.marked_at = marked_paid_at
                payment.save()
                return Response({"message: Invoice marked paid successfully!"}, status=status.HTTP_200_OK)
            return Response({"error: Payment has not be done yet."}, status=status.HTTP_404_NOT_FOUND)
        return Response({"error: Only Staff users allowed."}, status=status.HTTP_404_NOT_FOUND)