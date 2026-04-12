from django.urls import path
from . import views

app_name = 'scanner'

urlpatterns = [
    path('dashboard/',        views.dashboard,       name='dashboard'),
    path('scan/',             views.scan_url,        name='scan'),
    path('result/<int:pk>/',  views.result_view,     name='result'),
    path('history/',          views.history_view,    name='history'),
    path('delete/<int:pk>/',  views.delete_scan,     name='delete_scan'),
    path('delete-all/',       views.delete_all_scans,name='delete_all'),
    path('ajax-scan/',        views.ajax_scan,       name='ajax_scan'),
]
