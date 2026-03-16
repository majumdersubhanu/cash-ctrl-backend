from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum
from lending.models import Loan
from splits.models import SplitGroup
from users.models import User
from django.template.defaultfilters import register

@register.filter
def format_currency(value):
    try:
        return "{:,.2f}".format(float(value))
    except (ValueError, TypeError):
        return value

@staff_member_required
def p2p_network_analytics(request):
    """
    Custom admin view to visualize user-to-user connections.
    """
    # top lenders
    top_lenders = User.objects.annotate(
        loans_count=Count('loans_given'),
        total_lent=Sum('loans_given__amount')
    ).filter(loans_count__gt=0).order_by('-total_lent')[:10]

    # top borrowers
    top_borrowers = User.objects.annotate(
        loans_count=Count('loans_taken'),
        total_borrowed=Sum('loans_taken__amount')
    ).filter(loans_count__gt=0).order_by('-total_borrowed')[:10]

    # active groups
    groups = SplitGroup.objects.annotate(
        member_count=Count('members'),
        expense_count=Count('expenses')
    ).order_by('-expense_count')[:10]

    context = {
        'title': 'Peer-to-Peer Financial Network',
        'top_lenders': top_lenders,
        'top_borrowers': top_borrowers,
        'groups': groups,
    }
    return render(request, 'admin/p2p_analytics.html', context)
