from django.contrib import admin
from django.contrib.admin.apps import AdminConfig
from django.db.models import Sum, Count
from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone
from django.urls import path
from decimal import Decimal
from django.core.cache import cache
from django.db import connection

class CashCtrlAdminSite(admin.AdminSite):
    site_header = "CashCtrl Admin Portal"
    site_title = "CashCtrl Admin"
    index_title = "System Overview & Analytics"

    def index(self, request, extra_context=None):
        from users.models import User
        from transactions.models import Transaction
        from lending.models import Loan
        from splits.models import SplitGroup
        from onboarding.models import KYCProfile

        # 1. Gather stats
        total_users = User.objects.count()
        
        # Transaction volume & counts
        posted_transactions = Transaction.objects.filter(status='POSTED')
        total_volume = posted_transactions.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        total_transactions = Transaction.objects.count()
        
        # Split groups
        total_groups = SplitGroup.objects.count()
        
        # Lending
        active_loans = Loan.objects.filter(status='ACTIVE')
        total_lent = active_loans.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        total_loans = Loan.objects.count()
        
        # KYC profiles
        pending_kyc_profiles = KYCProfile.objects.filter(status='PENDING').select_related('user')
        pending_kyc_count = pending_kyc_profiles.count()
        
        # 2. Connection checks
        # Redis Status
        try:
            cache.set("admin_redis_check", "ok", timeout=5)
            redis_status = "Healthy" if cache.get("admin_redis_check") == "ok" else "Unhealthy"
        except Exception:
            redis_status = "Unhealthy"
            
        # Database Status
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            db_status = "Healthy"
        except Exception:
            db_status = "Unhealthy"

        # 3. Chart Data (distributes transactions and loan states)
        # Transaction Type Split
        tx_types = list(Transaction.objects.values('type').annotate(count=Count('id')))
        tx_type_labels = [item['type'] for item in tx_types]
        tx_type_data = [item['count'] for item in tx_types]
        
        # KYC Status Split
        kyc_states = list(KYCProfile.objects.values('status').annotate(count=Count('id')))
        kyc_status_labels = [item['status'] for item in kyc_states]
        kyc_status_data = [item['count'] for item in kyc_states]
        
        # Loan Status Split
        loan_states = list(Loan.objects.values('status').annotate(count=Count('id')))
        loan_status_labels = [item['status'] for item in loan_states]
        loan_status_data = [item['count'] for item in loan_states]

        # 4. Recent Transactions Table
        recent_transactions = Transaction.objects.select_related('user', 'account').order_by('-date')[:10]

        # Context aggregation
        dashboard_context = {
            'total_users': total_users,
            'total_volume': float(total_volume),
            'total_transactions': total_transactions,
            'total_groups': total_groups,
            'total_lent': float(total_lent),
            'total_loans': total_loans,
            'pending_kyc_count': pending_kyc_count,
            'pending_kyc_profiles': pending_kyc_profiles,
            'redis_status': redis_status,
            'db_status': db_status,
            'tx_type_labels': tx_type_labels,
            'tx_type_data': tx_type_data,
            'kyc_status_labels': kyc_status_labels,
            'kyc_status_data': kyc_status_data,
            'loan_status_labels': loan_status_labels,
            'loan_status_data': loan_status_data,
            'recent_transactions': recent_transactions,
        }

        # Merge with extra_context
        if extra_context:
            dashboard_context.update(extra_context)
            
        return super().index(request, extra_context=dashboard_context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('kyc/<uuid:profile_id>/approve/', self.admin_view(self.approve_kyc), name='approve_kyc'),
            path('kyc/<uuid:profile_id>/reject/', self.admin_view(self.reject_kyc), name='reject_kyc'),
        ]
        return custom_urls + urls

    def approve_kyc(self, request, profile_id):
        from onboarding.models import KYCProfile
        if not request.user.is_staff:
            return redirect('admin:index')
        try:
            profile = KYCProfile.objects.get(id=profile_id)
            profile.status = KYCProfile.KYCStatus.VERIFIED
            profile.verified_at = timezone.now()
            profile.save()
            
            # also verify all its documents
            profile.documents.all().update(is_verified=True)
            
            messages.success(request, f"KYC approved successfully for {profile.user.email}")
        except KYCProfile.DoesNotExist:
            messages.error(request, "KYC profile not found")
        return redirect('admin:index')

    def reject_kyc(self, request, profile_id):
        from onboarding.models import KYCProfile
        if not request.user.is_staff:
            return redirect('admin:index')
        try:
            profile = KYCProfile.objects.get(id=profile_id)
            profile.status = KYCProfile.KYCStatus.REJECTED
            profile.save()
            messages.warning(request, f"KYC rejected for {profile.user.email}")
        except KYCProfile.DoesNotExist:
            messages.error(request, "KYC profile not found")
        return redirect('admin:index')

class CashCtrlAdminConfig(AdminConfig):
    default_site = "app.admin.CashCtrlAdminSite"
