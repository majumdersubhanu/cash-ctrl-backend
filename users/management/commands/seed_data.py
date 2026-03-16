import random
from decimal import Decimal
from faker import Faker
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import Account
from transactions.models import Transaction

User = get_user_model()
fake = Faker()

class Command(BaseCommand):
    help = 'Seeds the database with dummy data using Faker (500 users, 50k transactions)'

    def handle(self, *args, **options):
        self.stdout.write("Starting high-fidelity data seeding with Faker...")
        
        # 1. Create Users
        users_to_create = []
        for i in range(1, 501):
            email = fake.unique.email()
            if not User.objects.filter(email=email).exists():
                users_to_create.append(User(
                    email=email, 
                    username=email, 
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    password="password123"
                ))
        
        if users_to_create:
            User.objects.bulk_create(users_to_create)
            self.stdout.write(f"Created {len(users_to_create)} users.")
        
        all_users = list(User.objects.all())
        all_accounts = []
        for user in all_users:
            account, created = Account.objects.get_or_create(
                user=user, 
                defaults={'balance': Decimal(random.randint(5000, 50000)), 'currency': 'USD'}
            )
            all_accounts.append(account)
        
        self.stdout.write(f"Verified {len(all_accounts)} accounts.")

        # 3. Create Transactions (50,000)
        transactions = []
        count = 0
        batch_size = 5000
        
        types = ['INCOME', 'EXPENSE', 'TRANSFER']
        statuses = ['POSTED', 'CLEARED']

        self.stdout.write("Generating 50,000 realistic transactions...")
        for i in range(50000):
            sender_acc = random.choice(all_accounts)
            amount = Decimal(random.uniform(10, 500)).quantize(Decimal('0.01'))
            
            transactions.append(Transaction(
                user=sender_acc.user,
                account=sender_acc,
                type=random.choice(types),
                amount=amount,
                description=fake.sentence(nb_words=6),
                status=random.choice(statuses)
            ))
            
            if len(transactions) >= batch_size:
                Transaction.objects.bulk_create(transactions)
                count += len(transactions)
                transactions = []
                self.stdout.write(f"Seeded {count} transactions...")

        if transactions:
            Transaction.objects.bulk_create(transactions)
            count += len(transactions)
            self.stdout.write(f"Seeded {count} transactions.")

        self.stdout.write(self.style.SUCCESS("High-fidelity data seeding completed!"))
