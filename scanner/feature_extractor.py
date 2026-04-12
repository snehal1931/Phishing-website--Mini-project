"""
Feature Extractor — extracts 16 numerical features from a URL.
These features are fed into the Random Forest ML model.
"""
import re
import urllib.parse


SUSPICIOUS_WORDS = [
    'login', 'signin', 'verify', 'secure', 'account', 'update', 'banking',
    'confirm', 'click', 'free', 'reward', 'prize', 'winner', 'kyc',
    'otp', 'urgent', 'lucky', 'claim', 'offer', 'limited', 'gift',
]


def extract_features(url: str) -> dict:
    """Return a dict of feature_name → value (all numeric)."""
    try:
        parsed = urllib.parse.urlparse(url)
    except Exception:
        parsed = None

    features = {}

    # 1. URL length (longer = more suspicious)
    features['url_length'] = len(url)

    # 2. Has @ symbol
    features['has_at_symbol'] = 1 if '@' in url else 0

    # 3. Has double slash redirect (//)
    features['has_double_slash'] = 1 if '//' in url.split('//', 1)[-1] else 0

    # 4. Dash in domain
    domain = parsed.netloc if parsed else ''
    features['has_dash_in_domain'] = 1 if '-' in domain else 0

    # 5. Subdomain count (dots in hostname)
    hostname = domain.split(':')[0]  # strip port
    dot_count = hostname.count('.')
    features['subdomain_count'] = max(0, dot_count - 1)

    # 6. Is HTTPS (1 = safe, 0 = suspicious)
    features['is_https'] = 1 if url.startswith('https://') else 0

    # 7. Has IP address instead of domain
    ip_pattern = re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
    features['has_ip_address'] = 1 if ip_pattern.search(domain) else 0

    # 8. URL depth (path depth)
    path = parsed.path if parsed else ''
    features['url_depth'] = path.count('/') if path else 0

    # 9. Has suspicious words
    url_lower = url.lower()
    features['suspicious_word_count'] = sum(1 for w in SUSPICIOUS_WORDS if w in url_lower)

    # 10. Domain length
    features['domain_length'] = len(hostname)

    # 11. Has query string
    features['has_query'] = 1 if (parsed.query if parsed else '') else 0

    # 12. Query string length
    features['query_length'] = len(parsed.query) if parsed else 0

    # 13. Number of digits in URL
    features['digit_count'] = sum(c.isdigit() for c in url)

    # 14. Number of special characters
    special_chars = re.findall(r'[!$%^&*()_+|~=`{}\[\]:;<>?,]', url)
    features['special_char_count'] = len(special_chars)

    # 15. Has port number (unusual ports = suspicious)
    try:
        port = parsed.port if parsed else None
    except ValueError:
        port = None  # Could not be cast to int, ignore and assume no valid port
    features['has_non_standard_port'] = 0 if port in (None, 80, 443, 8080) else 1

    # 16. TLD is suspicious (.xyz, .tk, .ml, .ga, .cf, .gq)
    suspicious_tlds = ['.xyz', '.tk', '.ml', '.ga', '.cf', '.gq', '.pw', '.top', '.click', '.link']
    features['suspicious_tld'] = 1 if any(hostname.endswith(t) for t in suspicious_tlds) else 0

    return features


def features_to_list(features: dict) -> list:
    """Convert feature dict to ordered list for ML model input."""
    keys = [
        'url_length', 'has_at_symbol', 'has_double_slash', 'has_dash_in_domain',
        'subdomain_count', 'is_https', 'has_ip_address', 'url_depth',
        'suspicious_word_count', 'domain_length', 'has_query', 'query_length',
        'digit_count', 'special_char_count', 'has_non_standard_port', 'suspicious_tld',
    ]
    return [features.get(k, 0) for k in keys]
