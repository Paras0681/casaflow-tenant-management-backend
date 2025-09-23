from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Payments 
from apps.tenants.models import Account, Room
from .serializers import PaymentSerializer
from apps.tenants.models import TenantsFiles, TenantsData


# Create your views here.
class GetPaymentsAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        if user.is_staff:
            payments = Payments.objects.all()
        else:
            account = Account.objects.filter(user=request.user).first()
            payments = Payments.objects.filter(account = account)
        serialzier = PaymentSerializer(payments, many=True)
        return Response(serialzier.data, status=status.HTTP_200_OK)
    

class MarkPaymentsAPIView(APIView):
    def post(self, request):
        data = request.data
        invoice_id = data.get("invoice_id")
        tenant_data = TenantsData.objects.filter(invoice_id = invoice_id).first()
        tenant_data.payment_status = "not_reviewed"
        tenant_data.save()
        screenshot = request.FILES.get("screenshot")
        if not screenshot:
            return Response({"error": "No file provided"}, status=400)
        account = Account.objects.get(user=request.user)
        room = Room.objects.filter(room_number=account.room_number).first()
        payload = {
            "account": account.id,
            "uploaded_by": f"{account.first_name + account.last_name}",
            "invoice_id": invoice_id,
            "payment_id": data.get("payment_id"),
            "payment_utr": data.get("payment_utr"),
            "amount": data.get("amount"),
            "paid_at": data.get("paid_at"),
        }
        serializer = PaymentSerializer(data=payload)
        if serializer.is_valid():
            serializer.save()
            tenants_file = TenantsFiles(
                account=account,
                room=room,
                file_type="payment_receipt",
                description=f"Payment Received for {invoice_id}",
            )
            tenants_file._invoice_id =invoice_id
            tenants_file.set_uploaded_file(screenshot)
            tenants_file.save()
            data = serializer.data.copy()
            data["payment_receipt_url"] = tenants_file.file_url
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

