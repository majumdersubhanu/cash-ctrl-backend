from django.utils.translation import gettext_lazy as _
from jet.dashboard import modules
from jet.dashboard.dashboard import Dashboard, AppIndexDashboard
from django.db.models import Sum
from accounts.models import Account
from transactions.models import Transaction
from lending.models import Loan
from users.models import User


class CustomIndexDashboard(Dashboard):
    columns = 3

    def init_with_context(self, context):
        # 1. Financial KPIs
        total_balance = Account.objects.aggregate(total=Sum("balance"))["total"] or 0
        total_volume = Transaction.objects.aggregate(total=Sum("amount"))["total"] or 0
        active_loans = (
            Loan.objects.filter(status="ACTIVE").aggregate(total=Sum("amount"))["total"]
            or 0
        )
        user_count = User.objects.count()

        self.children.append(
            modules.LinkList(
                _("Financial Pulse"),
                layout="inline",
                draggable=False,
                deletable=False,
                collapsible=False,
                children=[
                    [_("Users"), user_count],
                    [_("Total System Balance"), f"${total_balance:,.2f}"],
                    [_("Transaction Volume"), f"${total_volume:,.2f}"],
                    [_("Loan Exposure"), f"${active_loans:,.2f}"],
                ],
            )
        )

        # 2. Recent Actions
        self.children.append(
            modules.RecentActions(_("Recent Activity"), column=0, limit=5)
        )

        # 3. App list
        self.children.append(
            modules.AppList(
                _("Applications"),
                column=1,
                draggable=True,
                deletable=False,
                collapsible=True,
            )
        )

        # 4. User-to-User Networking (Simple stat)
        # In a real app, this could be a chart
        self.children.append(
            modules.LinkList(
                _("P2P Analytics"),
                column=2,
                children=[
                    {
                        "title": _("Lending Network Nodes"),
                        "url": "/admin/p2p-analytics/p2p-network/",
                        "external": False,
                        "description": f"{Loan.objects.values('lender', 'borrower').distinct().count()} unique peer relationships",
                    },
                    {
                        "title": _("Group Splits Active"),
                        "url": "/admin/p2p-analytics/p2p-network/",
                        "external": False,
                        "description": f"{Transaction.objects.filter(type='TRANSFER').count()} shared transactions",
                    },
                ],
            )
        )


class CustomAppIndexDashboard(AppIndexDashboard):
    def init_with_context(self, context):
        self.children.append(
            modules.ModelList(
                _("App Models"),
                models=self.models(),
            )
        )

        self.children.append(
            modules.RecentActions(
                _("Recent Actions"),
                include_list=self.get_app_content_types(),
            )
        )
