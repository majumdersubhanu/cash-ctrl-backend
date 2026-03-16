from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from onboarding.models import KYCDocument
from onboarding.services import KYCService
from lending.models import Loan
from audit.models import AuditLog
from decimal import Decimal

User = get_user_model()

class OnboardingLendingIntegrationTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='testuser@example.com', password='password123')
        self.client.force_authenticate(user=self.user)

    def test_onboarding_to_loan_flow(self):
        # 1. Setup profile and document
        profile = KYCService.get_or_create_profile(self.user)
        profile.first_name = "John"
        profile.last_name = "Doe"
        profile.save()
        
        doc_file = SimpleUploadedFile("id.jpg", b"fake_content", content_type="image/jpeg")
        KYCDocument.objects.create(
            profile=profile, 
            document_type='ID_CARD', 
            document_file=doc_file
        )

        # 2. Submit KYC
        url = reverse('kyc-submit')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'PENDING')
        
        # Verify Audit Log
        self.assertTrue(AuditLog.objects.filter(user=self.user, action='KYC_SUBMITTED').exists())

        # 3. Admin verifies KYC
        KYCService.verify_profile(profile)

        # 4. Request a Loan
        url = reverse('loan-list')
        loan_data = {
            "amount": "1000.00",
            "interest_rate": "5.0",
            "duration_months": 12
        }
        response = self.client.post(url, loan_data)
        if response.status_code != 201:
            print(f"\nDEBUG: Loan Request URL: {url}")
            print(f"DEBUG: Response Status: {response.status_code}")
            print(f"DEBUG: Response Content: {response.content}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify Loan created and installments generated
        loan_id = response.data['id']
        loan = Loan.objects.get(id=loan_id)
        self.assertEqual(loan.amount, Decimal('1000.00'))
        self.assertEqual(loan.installments.count(), 12)
        
        # Verify Audit Log for loan
        self.assertTrue(AuditLog.objects.filter(action='LOAN_CREATED', resource_id=loan.id).exists())
