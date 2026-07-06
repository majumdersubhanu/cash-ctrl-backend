from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from django.contrib.auth import get_user_model
from model_bakery import baker

from splits.services import SplitService
from splits.models import SplitExpense, SplitParticipation

User = get_user_model()


@pytest.mark.django_db
class TestSplitServiceCreateExpense:
    """Tests for SplitService.create_expense"""

    def test_creates_expense_record(self):
        group = baker.make("splits.SplitGroup")
        paid_by = baker.make("users.User")
        member1 = baker.make("users.User")
        member2 = baker.make("users.User")

        participants_data = [
            {"user": member1, "share_amount": Decimal("50.00")},
            {"user": member2, "share_amount": Decimal("50.00")},
        ]

        expense = SplitService.create_expense(
            group=group,
            paid_by=paid_by,
            amount=Decimal("100.00"),
            description="Test Dinner",
            participants_data=participants_data,
        )

        assert SplitExpense.objects.filter(pk=expense.pk).exists()
        assert expense.amount == Decimal("100.00")
        assert expense.description == "Test Dinner"

    def test_creates_participation_records(self):
        group = baker.make("splits.SplitGroup")
        paid_by = baker.make("users.User")
        member1 = baker.make("users.User")
        member2 = baker.make("users.User")

        participants_data = [
            {"user": member1, "share_amount": Decimal("30.00")},
            {"user": member2, "share_amount": Decimal("70.00")},
        ]

        expense = SplitService.create_expense(
            group=group,
            paid_by=paid_by,
            amount=Decimal("100.00"),
            description="Concert Tickets",
            participants_data=participants_data,
        )

        assert SplitParticipation.objects.filter(expense=expense).count() == 2

    def test_default_currency_is_usd(self):
        group = baker.make("splits.SplitGroup")
        paid_by = baker.make("users.User")
        member = baker.make("users.User")

        expense = SplitService.create_expense(
            group=group,
            paid_by=paid_by,
            amount=Decimal("50.00"),
            description="Coffee",
            participants_data=[{"user": member, "share_amount": Decimal("50.00")}],
        )

        assert expense.currency == "USD"

    def test_custom_currency_is_saved(self):
        group = baker.make("splits.SplitGroup")
        paid_by = baker.make("users.User")
        member = baker.make("users.User")

        expense = SplitService.create_expense(
            group=group,
            paid_by=paid_by,
            amount=Decimal("50.00"),
            description="Euro trip",
            participants_data=[{"user": member, "share_amount": Decimal("50.00")}],
            currency="EUR",
        )

        assert expense.currency == "EUR"

    def test_amount_accepts_string_input(self):
        """create_expense should handle string amounts (Decimal conversion)."""
        group = baker.make("splits.SplitGroup")
        paid_by = baker.make("users.User")
        member = baker.make("users.User")

        expense = SplitService.create_expense(
            group=group,
            paid_by=paid_by,
            amount="75.50",
            description="Taxi",
            participants_data=[{"user": member, "share_amount": Decimal("75.50")}],
        )

        assert expense.amount == Decimal("75.50")


class TestSplitServiceCalculateEqualSplit:
    """Tests for SplitService.calculate_equal_split"""

    def _make_fake_members(self, n):
        """Return simple mock objects with no DB needed."""
        return [MagicMock() for _ in range(n)]

    def test_empty_members_returns_empty_list(self):
        result = SplitService.calculate_equal_split(Decimal("100"), [])
        assert result == []

    def test_single_member_gets_whole_amount(self):
        member = object()
        result = SplitService.calculate_equal_split(Decimal("100.00"), [member])
        assert len(result) == 1
        assert result[0]["share_amount"] == Decimal("100.00")
        assert result[0]["user"] is member

    def test_two_members_equal_split(self):
        m1, m2 = object(), object()
        result = SplitService.calculate_equal_split(Decimal("100.00"), [m1, m2])
        assert result[0]["share_amount"] == Decimal("50.00")
        assert result[1]["share_amount"] == Decimal("50.00")

    def test_three_members_sum_equals_total(self):
        members = [object(), object(), object()]
        result = SplitService.calculate_equal_split(Decimal("100.00"), members)
        total = sum(r["share_amount"] for r in result)
        assert total == Decimal("100.00")

    def test_uneven_split_last_member_absorbs_remainder(self):
        """For $10 / 3 = $3.33, last member gets the rounding remainder."""
        members = [object(), object(), object()]
        result = SplitService.calculate_equal_split(Decimal("10.00"), members)
        total = sum(r["share_amount"] for r in result)
        assert total == Decimal("10.00")

    def test_string_amount_input(self):
        m1, m2 = object(), object()
        result = SplitService.calculate_equal_split("200.00", [m1, m2])
        assert sum(r["share_amount"] for r in result) == Decimal("200.00")


class TestSplitServiceCalculatePercentageSplit:
    """Tests for SplitService.calculate_percentage_split"""

    def test_valid_percentage_split(self):
        m1, m2 = object(), object()
        user_percentages = [
            {"user": m1, "percentage": "60"},
            {"user": m2, "percentage": "40"},
        ]
        result = SplitService.calculate_percentage_split(
            Decimal("100.00"), user_percentages
        )
        total = sum(r["share_amount"] for r in result)
        assert total == Decimal("100.00")

    def test_percentages_not_100_raises_value_error(self):
        m1, m2 = object(), object()
        user_percentages = [
            {"user": m1, "percentage": "60"},
            {"user": m2, "percentage": "30"},  # total = 90
        ]
        with pytest.raises(ValueError, match="Percentages must sum to 100"):
            SplitService.calculate_percentage_split(Decimal("100.00"), user_percentages)

    def test_three_way_split_sums_correctly(self):
        m1, m2, m3 = object(), object(), object()
        user_percentages = [
            {"user": m1, "percentage": "33.33"},
            {"user": m2, "percentage": "33.33"},
            {"user": m3, "percentage": "33.34"},
        ]
        result = SplitService.calculate_percentage_split(
            Decimal("100.00"), user_percentages
        )
        total = sum(r["share_amount"] for r in result)
        assert total == Decimal("100.00")

    def test_each_participant_gets_correct_share(self):
        m1, m2 = object(), object()
        user_percentages = [
            {"user": m1, "percentage": "75"},
            {"user": m2, "percentage": "25"},
        ]
        result = SplitService.calculate_percentage_split(
            Decimal("200.00"), user_percentages
        )
        shares = {item["user"]: item["share_amount"] for item in result}
        assert shares[m1] == Decimal("150.00")
        assert shares[m2] == Decimal("50.00")


class TestSplitServiceCalculateFixedAmounts:
    """Tests for SplitService.calculate_fixed_amounts"""

    def test_valid_fixed_split(self):
        m1, m2 = object(), object()
        user_amounts = [
            {"user": m1, "amount": "60"},
            {"user": m2, "amount": "40"},
        ]
        result = SplitService.calculate_fixed_amounts(Decimal("100.00"), user_amounts)
        assert len(result) == 2
        total = sum(r["share_amount"] for r in result)
        assert total == Decimal("100.00")

    def test_fixed_amounts_not_matching_total_raises(self):
        m1, m2 = object(), object()
        user_amounts = [
            {"user": m1, "amount": "60"},
            {"user": m2, "amount": "30"},  # total = 90, not 100
        ]
        with pytest.raises(ValueError, match="Fixed amounts must sum to total amount"):
            SplitService.calculate_fixed_amounts(Decimal("100.00"), user_amounts)

    def test_returns_decimal_share_amounts(self):
        m1 = object()
        user_amounts = [{"user": m1, "amount": "55.50"}]
        result = SplitService.calculate_fixed_amounts(Decimal("55.50"), user_amounts)
        assert isinstance(result[0]["share_amount"], Decimal)
        assert result[0]["share_amount"] == Decimal("55.50")


@pytest.mark.django_db
class TestSplitModelsStr:
    def test_split_group_str(self):
        group = baker.make("splits.SplitGroup", name="Roommates")
        assert str(group) == "Roommates"

    def test_split_expense_str(self):
        paid_by = baker.make("users.User", email="paidby@example.com")
        group = baker.make("splits.SplitGroup")
        expense = SplitExpense.objects.create(
            group=group,
            paid_by=paid_by,
            amount=Decimal("150.00"),
            currency="EUR",
            description="Electric Bill",
        )
        assert str(expense) == "Electric Bill (150.00 EUR)"

    def test_split_participation_str(self):
        paid_by = baker.make("users.User")
        user = baker.make("users.User", email="member@example.com")
        group = baker.make("splits.SplitGroup")
        expense = SplitExpense.objects.create(
            group=group,
            paid_by=paid_by,
            amount=Decimal("150.00"),
            currency="EUR",
            description="Electric Bill",
        )
        participation = SplitParticipation.objects.create(
            expense=expense, user=user, share_amount=Decimal("75.00")
        )
        assert str(participation) == "member@example.com owes 75.00 for Electric Bill"
