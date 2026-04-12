from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('',          views.admin_dashboard, name='dashboard'),
    path('all-scans/', views.all_scans,      name='all_scans'),
]
