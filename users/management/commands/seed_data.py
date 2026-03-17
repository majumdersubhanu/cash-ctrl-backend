import random
from decimal import Decimal
from faker import Faker
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from accounts.models import Account
from transactions.models import Category, Transaction
from lending.models import Loan
from splits.models import SplitGroup, SplitExpense
from analytics.models import Budget, SavingsGoal

User = get_user_model()
fake = Faker()


class Command(BaseCommand):
    help = "Seeds database with high-volume data: 5k Users, 500k Transactions, plus Accounts, Loans, Splits etc."

    def handle(self, *args, **options):
        self.stdout.write(
            "Starting high-fidelity Mass Data Seeding (5K Users / 500K Transactions)..."
        )
        self.stdout.write("This may take a few minutes due to the high volume.")

        # -------------------------------------------------------------------------------------
        # 1. USERS & ACCOUNTS (5,000)
        # -------------------------------------------------------------------------------------
        user_count = 5000
        existing_users = User.objects.count()
        if existing_users < user_count:
            self.stdout.write(f"Generating {user_count - existing_users} users...")
            new_users = []
            emails = set()
            while len(emails) < (user_count - existing_users):
                emails.add(fake.unique.email())

            for email in emails:
                new_users.append(
                    User(
                        email=email,
                        first_name=fake.first_name(),
                        last_name=fake.last_name(),
                        password="password123",  # Not hashed for speed in dummy data, users won't log in
                    )
                )

            User.objects.bulk_create(new_users, batch_size=2000, ignore_conflicts=True)
            self.stdout.write("Users generated.")

        all_users = list(User.objects.all()[:user_count])

        # Ensure accounts exist
        existing_accounts_count = Account.objects.count()
        if existing_accounts_count < user_count:
            self.stdout.write("Generating Accounts for users...")
            existing_account_user_ids = set(
                Account.objects.values_list("user_id", flat=True)
            )
            new_accounts = []
            for u in all_users:
                if u.id not in existing_account_user_ids:
                    new_accounts.append(
                        Account(
                            user=u,
                            balance=Decimal(random.randint(500, 100000)),
                            currency="USD",
                        )
                    )
            if new_accounts:
                Account.objects.bulk_create(new_accounts, batch_size=2000)
            self.stdout.write("Accounts verified.")

        all_accounts = list(Account.objects.all()[:user_count])

        # -------------------------------------------------------------------------------------
        # 2. CATEGORIES (~20 global standard categories over users)
        # -------------------------------------------------------------------------------------
        self.stdout.write("Generating Categories...")
        cat_names = [
            "Groceries",
            "Rent",
            "Utilities",
            "Salary",
            "Entertainment",
            "Dining",
            "Travel",
            "Health",
        ]
        categories = []
        if not Category.objects.exists():
            for i in range(100):  # Create 100 random user categories
                u = random.choice(all_users)
                name = random.choice(cat_names) + str(random.randint(1, 5))
                typ = "INCOME" if "Salary" in name else "EXPENSE"
                categories.append(Category(user=u, name=name, type=typ))
            Category.objects.bulk_create(categories, ignore_conflicts=True)

        all_categories = list(Category.objects.all()[:100])

        # -------------------------------------------------------------------------------------
        # 3. TRANSACTIONS (500,000)
        # -------------------------------------------------------------------------------------
        target_tx_count = 500000
        existing_tx = Transaction.objects.count()

        if existing_tx < target_tx_count:
            needed = target_tx_count - existing_tx
            self.stdout.write(f"Generating {needed} Transactions...")
            types = ["INCOME", "EXPENSE", "TRANSFER"]
            statuses = ["POSTED", "CLEARED"]
            batch_size = 10000
            transactions_buffer = []

            # Using transaction.atomic speeds up bulk inserts significantly
            with transaction.atomic():
                for i in range(needed):
                    acc = random.choice(all_accounts)
                    cat = (
                        random.choice(all_categories)
                        if all_categories and random.random() > 0.3
                        else None
                    )
                    tx_type = random.choice(types)

                    transactions_buffer.append(
                        Transaction(
                            user=acc.user,
                            account=acc,
                            category=cat,
                            type=tx_type,
                            amount=Decimal(random.uniform(5.0, 2000.0)).quantize(
                                Decimal("0.01")
                            ),
                            description=fake.sentence(nb_words=4),
                            status=random.choice(statuses),
                        )
                    )

                    if len(transactions_buffer) >= batch_size:
                        Transaction.objects.bulk_create(transactions_buffer)
                        self.stdout.write(f"  ... inserted {i + 1} transactions")
                        transactions_buffer = []

                if transactions_buffer:
                    Transaction.objects.bulk_create(transactions_buffer)
            self.stdout.write("Transactions generated.")

        # -------------------------------------------------------------------------------------
        # 4. LOANS (P2P Connectivity)
        # -------------------------------------------------------------------------------------
        self.stdout.write("Generating P2P Loans to build network analytics...")
        if Loan.objects.count() < 1000:
            new_loans = []
            for i in range(2000):
                lender = random.choice(all_users)
                borrower = random.choice(all_users)
                if lender != borrower:
                    new_loans.append(
                        Loan(
                            lender=lender,
                            borrower=borrower,
                            amount=Decimal(random.randint(100, 5000)),
                            interest_rate=Decimal(random.uniform(2.0, 10.0)).quantize(
                                Decimal("0.01")
                            ),
                            duration_months=random.choice([6, 12, 24]),
                            status=random.choice(["ACTIVE", "FULLY_PAID", "DEFAULTED"]),
                        )
                    )
            Loan.objects.bulk_create(new_loans, batch_size=1000, ignore_conflicts=True)
            self.stdout.write("Loans generated.")

        # -------------------------------------------------------------------------------------
        # 5. SPLIT GROUPS & EXPENSES
        # -------------------------------------------------------------------------------------
        self.stdout.write("Generating Split Groups & Expenses...")
        if SplitGroup.objects.count() < 500:
            groups = []
            for i in range(500):
                creator = random.choice(all_users)
                groups.append(
                    SplitGroup(name=fake.company() + " Trip", creator=creator)
                )
            SplitGroup.objects.bulk_create(groups, batch_size=500)

        all_groups = list(SplitGroup.objects.all()[:500])
        for group in all_groups:
            members = random.sample(all_users, k=random.randint(2, 6))
            group.members.add(*members)
            group.members.add(group.creator)

            # Create a few expenses for each group
            for _ in range(5):
                payer = random.choice(list(group.members.all()))
                amount = Decimal(random.randint(50, 500))
                SplitExpense.objects.create(
                    group=group,
                    description=fake.catch_phrase(),
                    paid_by=payer,
                    amount=amount,
                    currency="USD",
                )

        # -------------------------------------------------------------------------------------
        # 6. BUDGETS & SAVINGS GOALS
        # -------------------------------------------------------------------------------------
        self.stdout.write("Generating Budgets and Savings Goals...")
        budgets = []
        for i in range(1000):
            budgets.append(
                Budget(
                    user=random.choice(all_users),
                    category=random.choice(all_categories) if all_categories else None,
                    amount=Decimal(random.randint(500, 5000)),
                    period=random.choice(["MONTHLY", "WEEKLY", "YEARLY"]),
                )
            )
        Budget.objects.bulk_create(budgets, batch_size=1000, ignore_conflicts=True)

        goals = []
        for i in range(500):
            target = Decimal(random.randint(1000, 50000))
            goals.append(
                SavingsGoal(
                    user=random.choice(all_users),
                    name=fake.bs(),
                    target_amount=target,
                    current_amount=target * Decimal(random.uniform(0.1, 0.9)),
                    target_date=timezone.now().date()
                    + timedelta(days=random.randint(30, 365)),
                )
            )
        SavingsGoal.objects.bulk_create(goals, batch_size=500, ignore_conflicts=True)

        # -------------------------------------------------------------------------------------
        # 7. KYC PROFILES & NOTIFICATIONS
        # -------------------------------------------------------------------------------------
        self.stdout.write("Generating KYC Profiles and Notifications...")
        from onboarding.models import KYCProfile

        if KYCProfile.objects.count() < user_count:
            profiles = []
            for u in all_users:
                profiles.append(
                    KYCProfile(
                        user=u,
                        first_name=u.first_name,
                        last_name=u.last_name,
                        date_of_birth=fake.date_of_birth(
                            minimum_age=18, maximum_age=80
                        ),
                        status=random.choice(["VERIFIED", "PENDING", "REJECTED"]),
                    )
                )
            KYCProfile.objects.bulk_create(
                profiles, batch_size=2000, ignore_conflicts=True
            )

        from notifications.models import Notification

        notifications = []
        for i in range(5000):
            notifications.append(
                Notification(
                    user=random.choice(all_users),
                    title=fake.sentence(nb_words=4),
                    message=fake.text(),
                    type=random.choice(["ALERT", "WARNING", "INFO"]),
                )
            )
        Notification.objects.bulk_create(
            notifications, batch_size=1000, ignore_conflicts=True
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"MASS DATA SEEDING COMPLETE! The DB has {User.objects.count()} Users and {Transaction.objects.count()} Transactions."
            )
        )
