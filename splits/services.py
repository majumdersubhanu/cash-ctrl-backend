from django.db import transaction
from decimal import Decimal
from .models import SplitExpense, SplitParticipation

class SplitService:
    @staticmethod
    @transaction.atomic
    def create_expense(group, paid_by, amount, description, participants_data, currency='USD'):
        """
        Creates an expense and split participations.
        participants_data: list of dicts {'user': user_obj, 'share_amount': decimal}
        """
        amount = Decimal(str(amount))
        
        expense = SplitExpense.objects.create(
            group=group,
            paid_by=paid_by,
            amount=amount,
            currency=currency,
            description=description
        )
        
        for part in participants_data:
            SplitParticipation.objects.create(
                expense=expense,
                user=part['user'],
                share_amount=Decimal(str(part['share_amount']))
            )
            
        return expense

    @staticmethod
    def calculate_equal_split(amount, members):
        """
        Helper to calculate equal shares.
        """
        amount = Decimal(str(amount))
        count = len(members)
        if count == 0:
            return []
            
        share = (amount / Decimal(count)).quantize(Decimal('0.01'))
        
        participants = []
        total_calculated = Decimal('0.00')
        
        for i, member in enumerate(members):
            # Add remaining cents to the last member to ensure total matches exactly
            if i == count - 1:
                member_share = amount - total_calculated
            else:
                member_share = share
                total_calculated += share
                
            participants.append({'user': member, 'share_amount': member_share})
            
        return participants
