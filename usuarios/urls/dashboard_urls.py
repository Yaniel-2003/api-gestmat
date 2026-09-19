from django.urls import path
from ..views.dashboard_views import DashboardExportView, DashboardStatsView

urlpatterns = [
    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('dashboard/export/', DashboardExportView.as_view(), name='dashboard_export'),
]