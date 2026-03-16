from django.urls import path
from .views import FinancialSummaryView, ForecastingView

urlpatterns = [
    path('summary/', FinancialSummaryView.as_view(), name='financial-summary'),
    path('forecast/', ForecastingView.as_view(), name='financial-forecast'),
]
