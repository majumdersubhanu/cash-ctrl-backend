from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.utils import timezone
from transactions.models import Transaction
from accounts.models import Account
from lending.models import Loan

class FinancialSummaryView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = request.user
        
        # Calculate Total Balance across all accounts
        total_balance = Account.objects.filter(user=user).aggregate(total=Sum('balance'))['total'] or 0
        
        # Calculate Total Income (current month)
        income = Transaction.objects.filter(
            user=user, 
            type='INCOME', 
            status='POSTED'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Calculate Total Expense (current month)
        expense = Transaction.objects.filter(
            user=user, 
            type='EXPENSE', 
            status='POSTED'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Loan stats
        total_borrowed = Loan.objects.filter(borrower=user, status='ACTIVE').aggregate(total=Sum('amount'))['total'] or 0
        total_lent = Loan.objects.filter(lender=user, status='ACTIVE').aggregate(total=Sum('amount'))['total'] or 0

        return Response({
            "net_worth": total_balance + total_lent - total_borrowed,
            "total_balance": total_balance,
            "monthly_income": income,
            "monthly_expense": expense,
            "total_borrowed": total_borrowed,
            "total_lent": total_lent
        })

class ForecastingView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        from .services import ForecastingService
        
        predicted_spending = ForecastingService.predict_next_month_spending(request.user)
        cash_flow_forecast = ForecastingService.forecast_cash_flow(request.user)
        
        return Response({
            "predicted_next_month_expense": predicted_spending,
            "projected_30_day_cash_flow": cash_flow_forecast,
            "confidence_score": "High" if Transaction.objects.filter(user=request.user).count() > 50 else "Medium"
        })

class ReportExportView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        import csv
        from django.http import HttpResponse
        
        # Get transactions for the user
        queryset = Transaction.objects.filter(user=request.user).order_by('-date')
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="cash_ctrl_report_{request.user.email}_{timezone.now().date()}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Date', 'Account', 'Type', 'Amount', 'Currency', 'Category', 'Description', 'Status'])
        
        for tx in queryset:
            writer.writerow([
                tx.date,
                tx.account.name,
                tx.get_type_display(),
                tx.amount,
                tx.currency,
                tx.category.name if tx.category else 'N/A',
                tx.description,
                tx.get_status_display()
            ])
            
        return response
