# frisque/scans/urls.py

from django.urls import path
from . import views

# App namespace for reverse lookups (e.g., {% url 'scans:run_scan' %})
app_name = 'scans'

urlpatterns = [
    # URL for initiating a new scan (maps to RunScanView)
    path('run/', views.RunScanView.as_view(), name='run_scan'),
    path('results/<uuid:pk>/', views.ScanResultView.as_view(), name='scan_result'),
    # Future: path('status/<uuid:scan_id>/', views.ScanStatusView.as_view(), name='scan_status'),
]
