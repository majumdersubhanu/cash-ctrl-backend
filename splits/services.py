from decimal import Decimal

from django.db import transaction

from .models import SplitExpense, SplitParticipation


class SplitService:
    @staticmethod
    @transaction.atomic
    def create_expense(
            group, paid_by, amount, description, participants_data, currency="USD"
    ):
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
            description=description,
        )

        for part in participants_data:
            SplitParticipation.objects.create(
                expense=expense,
                user=part["user"],
                share_amount=Decimal(str(part["share_amount"])),
            )

        return expense

    @staticmethod
    def calculate_equal_split(amount, members):
        """
        Calculates equal shares.
        """
        amount = Decimal(str(amount))
        count = len(members)
        if count == 0:
            return []

        share = (amount / Decimal(count)).quantize(Decimal("0.01"))

        participants = []
        total_calculated = Decimal("0.00")

        for i, member in enumerate(members):
            if i == count - 1:
                member_share = amount - total_calculated
            else:
                member_share = share
                total_calculated += share

            participants.append({"user": member, "share_amount": member_share})

        return participants

    @staticmethod
    def calculate_percentage_split(amount, user_percentages):
        """
        user_percentages: list of dicts {'user': user_obj, 'percentage': decimal}
        """
        amount = Decimal(str(amount))
        total_pct = sum(Decimal(str(p["percentage"])) for p in user_percentages)

        if total_pct != Decimal("100.00"):
            raise ValueError(f"Percentages must sum to 100. Total is {total_pct}")

        participants = []
        total_calculated = Decimal("0.00")

        for i, item in enumerate(user_percentages):
            if i == len(user_percentages) - 1:
                share = amount - total_calculated
            else:
                share = (
                        amount * Decimal(str(item["percentage"])) / Decimal("100")
                ).quantize(Decimal("0.01"))
                total_calculated += share

            participants.append({"user": item["user"], "share_amount": share})

        return participants

    @staticmethod
    def calculate_fixed_amounts(amount, user_amounts):
        """
        user_amounts: list of dicts {'user': user_obj, 'amount': decimal}
        """
        amount = Decimal(str(amount))
        total_fixed = sum(Decimal(str(a["amount"])) for a in user_amounts)

        if total_fixed != amount:
            raise ValueError(
                f"Fixed amounts must sum to total amount {amount}. Total is {total_fixed}"
            )

        return [
            {"user": item["user"], "share_amount": Decimal(str(item["amount"]))}
            for item in user_amounts
        ]
