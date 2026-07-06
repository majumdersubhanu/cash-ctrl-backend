import random
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from faker import Faker

from accounts.models import Account
from analytics.models import Budget, SavingsGoal
from lending.models import Loan
from splits.models import SplitGroup, SplitExpense
from transactions.models import Category, Transaction

User = get_user_model()
fake = Faker()


class Command(BaseCommand):
    help = "Seeds database with high-volume data: 5k Users, 500k Transactions, plus Accounts, Loans, Splits etc."

    def handle(self, *args, **options):
        self.stdout.write(
            "Starting high-fidelity Mass Data Seeding (5K Users / 500K Transactions)..."
        )
        self.stdout.write("This may take a few minutes due to the high volume.")

        all_users = self._seed_users()
        all_accounts = self._seed_accounts(all_users)
        all_categories = self._seed_categories(all_users)
        self._seed_transactions(all_accounts, all_categories)
        self._seed_loans(all_users)
        self._seed_splits(all_users)
        self._seed_budgets_and_goals(all_users, all_categories)
        self._seed_kyc(all_users)
        self._seed_notifications(all_users)

        self.stdout.write(
            self.style.SUCCESS(
                f"MASS DATA SEEDING COMPLETE! The DB has {User.objects.count()} Users and {Transaction.objects.count()} Transactions."
            )
        )

    def _seed_users(self):
        user_count = 5000
        existing_users = User.objects.count()
        if existing_users < user_count:
            self.stdout.write(f"Generating {user_count - existing_users} users...")
            new_users = []
            emails = set()
            while len(emails) < (user_count - existing_users):
                emails.add(fake.unique.email())
            for idx, email in enumerate(emails):
                ident = email.split("@")[0]
                new_users.append(
                    User(
                        username=f"{ident}_{idx}",
                        email=email,
                        first_name=fake.first_name(),
                        last_name=fake.last_name(),
                        password="password123",
                    )
                )
            User.objects.bulk_create(new_users, batch_size=2000, ignore_conflicts=True)
            self.stdout.write("Users generated.")
        return list(User.objects.all()[:user_count])

    def _seed_accounts(self, all_users):
        existing_accounts_count = Account.objects.count()
        if existing_accounts_count < len(all_users):
            self.stdout.write("Generating Accounts for users...")
            existing_account_user_ids = set(Account.objects.values_list("user_id", flat=True))
            new_accounts = [
                Account(user=u, balance=Decimal(random.randint(500, 100000)), currency="USD")
                for u in all_users if u.id not in existing_account_user_ids
            ]
            if new_accounts:
                Account.objects.bulk_create(new_accounts, batch_size=2000)
            self.stdout.write("Accounts verified.")
        return list(Account.objects.all()[:len(all_users)])

    def _seed_categories(self, all_users):
        self.stdout.write("Generating Categories...")
        cat_names = ["Groceries", "Rent", "Utilities", "Salary", "Entertainment", "Dining", "Travel", "Health"]
        if not Category.objects.exists():
            categories = [
                Category(user=random.choice(all_users), 
                         name=random.choice(cat_names) + str(random.randint(1, 5)), 
                         type="INCOME" if "Salary" in cat_names else "EXPENSE")
                for _ in range(100)
            ]
            Category.objects.bulk_create(categories, ignore_conflicts=True)
        return list(Category.objects.all()[:100])

    def _seed_transactions(self, all_accounts, all_categories):
        target_tx_count = 500000
        existing_tx = Transaction.objects.count()
        if existing_tx < target_tx_count:
            needed = target_tx_count - existing_tx
            self.stdout.write(f"Generating {needed} Transactions...")
            types, statuses, batch_size = ["INCOME", "EXPENSE", "TRANSFER"], ["POSTED", "CLEARED"], 10000
            transactions_buffer = []
            with transaction.atomic():
                for i in range(needed):
                    acc = random.choice(all_accounts)
                    cat = random.choice(all_categories) if all_categories and random.random() > 0.3 else None
                    transactions_buffer.append(Transaction(user=acc.user, account=acc, category=cat, type=random.choice(types),
                                                            amount=Decimal(random.uniform(5.0, 2000.0)).quantize(Decimal("0.01")),
                                                            description=fake.sentence(nb_words=4), status=random.choice(statuses)))
                    if len(transactions_buffer) >= batch_size:
                        Transaction.objects.bulk_create(transactions_buffer)
                        self.stdout.write(f"  ... inserted {i + 1} transactions")
                        transactions_buffer = []
                if transactions_buffer:
                    Transaction.objects.bulk_create(transactions_buffer)
            self.stdout.write("Transactions generated.")

    def _seed_loans(self, all_users):
        self.stdout.write("Generating P2P Loans to build network analytics...")
        if Loan.objects.count() < 1000:
            new_loans = []
            for _ in range(2000):
                lender, borrower = random.choice(all_users), random.choice(all_users)
                if lender != borrower:
                    new_loans.append(Loan(lender=lender, borrower=borrower, amount=Decimal(random.randint(100, 5000)),
                                          interest_rate=Decimal(random.uniform(2.0, 10.0)).quantize(Decimal("0.01")),
                                          duration_months=random.choice([6, 12, 24]), status=random.choice(["ACTIVE", "FULLY_PAID", "DEFAULTED"])))
            Loan.objects.bulk_create(new_loans, batch_size=1000, ignore_conflicts=True)
            self.stdout.write("Loans generated.")

    def _seed_splits(self, all_users):
        self.stdout.write("Generating Split Groups & Expenses...")
        if SplitGroup.objects.count() < 500:
            groups = [SplitGroup(name=fake.company() + " Trip", creator=random.choice(all_users)) for _ in range(500)]
            SplitGroup.objects.bulk_create(groups, batch_size=500)
        for group in SplitGroup.objects.all()[:500]:
            members = random.sample(all_users, k=random.randint(2, 6))
            group.members.add(*members, group.creator)
            for _ in range(5):
                SplitExpense.objects.create(group=group, description=fake.catch_phrase(), 
                                            paid_by=random.choice(list(group.members.all())), 
                                            amount=Decimal(random.randint(50, 500)), currency="USD")

    def _seed_budgets_and_goals(self, all_users, all_categories):
        self.stdout.write("Generating Budgets and Savings Goals...")
        budgets = [Budget(user=random.choice(all_users), category=random.choice(all_categories) if all_categories else None,
                          amount=Decimal(random.randint(500, 5000)), period=random.choice(["MONTHLY", "WEEKLY", "YEARLY"]),
                          start_date=timezone.now().date()) for _ in range(1000)]
        Budget.objects.bulk_create(budgets, batch_size=1000, ignore_conflicts=True)
        goals = [SavingsGoal(user=random.choice(all_users), name=fake.bs(), target_amount=(t := Decimal(random.randint(1000, 50000))),
                             current_amount=t * Decimal(random.uniform(0.1, 0.9)),
                             target_date=timezone.now().date() + timedelta(days=random.randint(30, 365))) for _ in range(500)]
        SavingsGoal.objects.bulk_create(goals, batch_size=500, ignore_conflicts=True)

    def _seed_kyc(self, all_users):
        self.stdout.write("Generating KYC Profiles and Notifications...")
        from onboarding.models import KYCProfile
        if KYCProfile.objects.count() < len(all_users):
            profiles = [KYCProfile(user=u, first_name=u.first_name, last_name=u.last_name,
                                   date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=80),
                                   status=random.choice(["VERIFIED", "PENDING", "REJECTED"])) for u in all_users]
            KYCProfile.objects.bulk_create(profiles, batch_size=2000, ignore_conflicts=True)

    def _seed_notifications(self, all_users):
        from notifications.models import Notification
        notifications = [Notification(user=random.choice(all_users), title=fake.sentence(nb_words=4), 
                                      message=fake.text(), type=random.choice(["ALERT", "WARNING", "INFO"])) for _ in range(5000)]
        Notification.objects.bulk_create(notifications, batch_size=1000, ignore_conflicts=True)
