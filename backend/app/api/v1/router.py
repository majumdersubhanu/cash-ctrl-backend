from fastapi import APIRouter
from app.api.v1 import (
    accounts,
    categories,
    transactions,
    p2p,
    social,
    mfa,
    audit,
    analytics,
    budgets,
    goals,
    recurring_transactions,
    data,
    gamification,
    notifications
)

api_router = APIRouter()
api_router.include_router(accounts.router, prefix="/accounts")
api_router.include_router(categories.router, prefix="/categories")
api_router.include_router(transactions.router, prefix="/transactions")
api_router.include_router(p2p.router, prefix="/p2p")
api_router.include_router(social.router, prefix="/social")
api_router.include_router(mfa.router, prefix="/mfa")
api_router.include_router(audit.router, prefix="/audit")
api_router.include_router(analytics.router, prefix="/analytics")
api_router.include_router(budgets.router, prefix="/budgets")
api_router.include_router(goals.router, prefix="/goals")
api_router.include_router(recurring_transactions.router, prefix="/recurring-transactions")
api_router.include_router(data.router, prefix="/data")
api_router.include_router(gamification.router, prefix="/gamification", tags=["gamification"])
api_router.include_router(notifications.router, prefix="/notifications")
