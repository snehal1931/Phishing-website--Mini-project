import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator

from .forms import ScanForm, find_url
from .models import ScanHistory
from .feature_extractor import extract_features, features_to_list
from .ml_predictor import predict
import re

@login_required
def dashboard(request):
    form = ScanForm()
    recent = ScanHistory.objects.filter(user=request.user)[:6]
    total  = ScanHistory.objects.filter(user=request.user).count()
    phish  = ScanHistory.objects.filter(user=request.user, result='Phishing').count()
    safe   = total - phish
    return render(request, 'scanner/dashboard.html', {
        'form': form,
        'recent_scans': recent,
        'total': total,
        'phish': phish,
        'safe': safe,
    })


@login_required
def scan_url(request):
    if request.method != 'POST':
        return redirect('scanner:dashboard')

    form = ScanForm(request.POST)
    if not form.is_valid():
        messages.error(request, 'Invalid URL. Please try again.')
        return redirect('scanner:dashboard')

    url = form.cleaned_data['url']

    try:
        features = extract_features(url)
        feat_list = features_to_list(features)
        prediction = predict(feat_list)
    except FileNotFoundError:
        messages.error(request, '⚠️ ML model not found! Run: py ml_model/train_model.py')
        return redirect('scanner:dashboard')
    except Exception as e:
        messages.error(request, f'Scan error: {e}')
        return redirect('scanner:dashboard')

    scan = ScanHistory.objects.create(
        user=request.user,
        url=url,
        category=form.cleaned_data.get('category', 'Link'),
        result=prediction['result'],
        confidence=prediction['confidence'],
        features_json=json.dumps(features),
    )
    return redirect('scanner:result', pk=scan.pk)


@login_required
def result_view(request, pk):
    scan = get_object_or_404(ScanHistory, pk=pk, user=request.user)
    features = scan.get_features()
    feature_labels = {
        'url_length':            'URL Length',
        'has_at_symbol':         'Has @ Symbol',
        'has_double_slash':      'Has Double Slash (//) Redirect',
        'has_dash_in_domain':    'Has Dash (-) in Domain',
        'subdomain_count':       'Subdomain Count',
        'is_https':              'Uses HTTPS',
        'has_ip_address':        'Has IP Address',
        'url_depth':             'URL Depth',
        'suspicious_word_count': 'Suspicious Keywords Found',
        'domain_length':         'Domain Length',
        'has_query':             'Has Query String',
        'query_length':          'Query String Length',
        'digit_count':           'Digit Count in URL',
        'special_char_count':    'Special Character Count',
        'has_non_standard_port': 'Non-Standard Port Used',
        'suspicious_tld':        'Suspicious TLD (.xyz, .tk…)',
    }
    feature_rows = [(feature_labels.get(k, k), v) for k, v in features.items()]

    # Type-specific advice
    category_advice = {
        'Email': [
            'Check the "From" address carefully — scammers often spoof names.',
            'Never click "Unsubscribe" in suspicious emails; it confirms your email is active.',
            'Be wary of emails creating extreme urgency or fear.'
        ],
        'Message': [
            'Do not reply "STOP" or "HELP" to unknown numbers.',
            'Scammers often use shortened URLs (bit.ly, tinyurl) in SMS.',
            'Official organizations (Banks, Govt) rarely use WhatsApp for first contact.'
        ],
        'Link': [
            'Look for subtle misspellings in the domain name (e.g., g00gle.com).',
            'Hover over links (on desktop) to see the actual destination before clicking.',
            'Use a VPN if you must visit unfamiliar websites.'
        ]
    }
    advice_list = category_advice.get(scan.category, category_advice['Link'])

    return render(request, 'scanner/result.html', {
        'scan': scan,
        'feature_rows': feature_rows,
        'advice_list': advice_list,
    })


@login_required
def history_view(request):
    qs = ScanHistory.objects.filter(user=request.user)
    filter_by = request.GET.get('filter', 'all')
    if filter_by == 'phishing':
        qs = qs.filter(result='Phishing')
    elif filter_by == 'safe':
        qs = qs.filter(result='Safe')

    paginator = Paginator(qs, 10)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'scanner/history.html', {
        'page_obj': page,
        'filter_by': filter_by,
        'total': qs.count(),
    })


@login_required
def delete_scan(request, pk):
    scan = get_object_or_404(ScanHistory, pk=pk, user=request.user)
    scan.delete()
    messages.success(request, 'Scan record deleted.')
    return redirect('scanner:history')


@login_required
def delete_all_scans(request):
    if request.method == 'POST':
        ScanHistory.objects.filter(user=request.user).delete()
        messages.success(request, 'All scan history cleared.')
    return redirect('scanner:history')


@login_required
def ajax_scan(request):
    """AJAX endpoint for instant scan from dashboard."""
    if request.method == 'POST':
        url = request.POST.get('url', '').strip()
        if not url:
            return JsonResponse({'error': 'No URL provided'}, status=400)
        
        url = find_url(url)
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        try:
            features  = extract_features(url)
            feat_list = features_to_list(features)
            prediction = predict(feat_list)
            scan = ScanHistory.objects.create(
                user=request.user,
                url=url,
                category=request.POST.get('category', 'Link'),
                result=prediction['result'],
                confidence=prediction['confidence'],
                features_json=json.dumps(features),
            )
            return JsonResponse({
                'result': prediction['result'],
                'confidence': prediction['confidence'],
                'scan_id': scan.pk,
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid method'}, status=405)
