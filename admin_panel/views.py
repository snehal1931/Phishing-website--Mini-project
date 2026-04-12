from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
import json

from scanner.models import ScanHistory


@staff_member_required
def admin_dashboard(request):
    total_users  = User.objects.count()
    total_scans  = ScanHistory.objects.count()
    phish_scans  = ScanHistory.objects.filter(result='Phishing').count()
    safe_scans   = total_scans - phish_scans
    phish_pct    = round((phish_scans / total_scans * 100), 1) if total_scans else 0

    # Last 7 days scan trend
    seven_days = timezone.now() - timedelta(days=7)
    daily = (
        ScanHistory.objects
        .filter(scanned_at__gte=seven_days)
        .annotate(day=TruncDate('scanned_at'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )
    chart_labels = [str(d['day']) for d in daily]
    chart_data   = [d['count'] for d in daily]

    recent_scans = ScanHistory.objects.select_related('user').order_by('-scanned_at')[:20]
    top_users = (
        User.objects
        .annotate(scan_count=Count('scanhistory'))
        .order_by('-scan_count')[:10]
    )

    return render(request, 'admin_panel/dashboard.html', {
        'total_users': total_users,
        'total_scans': total_scans,
        'phish_scans': phish_scans,
        'safe_scans':  safe_scans,
        'phish_pct':   phish_pct,
        'chart_labels': json.dumps(chart_labels),
        'chart_data':   json.dumps(chart_data),
        'recent_scans': recent_scans,
        'top_users':    top_users,
    })


@staff_member_required
def all_scans(request):
    scans = ScanHistory.objects.select_related('user').order_by('-scanned_at')
    return render(request, 'admin_panel/all_scans.html', {'scans': scans})
