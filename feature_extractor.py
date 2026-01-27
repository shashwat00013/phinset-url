def extract_url_features(url):
    features = []
    try:
        from urllib.parse import urlparse
        import re

        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        path = parsed.path.lower()
        query = parsed.query.lower()

        # Length-based
        features.append(len(url))
        features.append(len(domain))
        features.append(len(path))
        features.append(len(query))

        # Domain-based
        features.append(domain.count('.'))
        features.append(len(domain.split('.')))  # subdomain depth
        features.append(domain.count('-'))

        # TLD checks
        features.append(int(domain.endswith(('.com', '.org', '.net', '.edu', '.gov'))))
        features.append(int(domain.endswith(('.xyz', '.top', '.club', '.online', '.site', '.info', '.biz', '.ru', '.cn'))))

        # Protocol
        features.append(int(parsed.scheme == 'https'))
        features.append(int(parsed.scheme == 'http'))

        # Suspicious words
        suspicious_words = [
            'login', 'verify', 'update', 'secure', 'account', 'signin',
            'confirm', 'password', 'bank', 'paypal', 'alert', 'free',
            'gift', 'claim'
        ]
        features.append(int(any(word in url.lower() for word in suspicious_words)))

        # Special characters
        features.append(url.count('@'))
        features.append(url.count('_'))
        features.append(int('//' in url[8:]))

        # Digits
        features.append(sum(c.isdigit() for c in url) / len(url))
        features.append(int(bool(re.match(r'\d+\.\d+\.\d+\.\d+', domain))))

        # Encoded & unusual chars
        features.append(int('%20' in url or '%3a' in url))
        features.append(int('~' in url))

    except Exception:
        features = [0] * 19  # ✅ MATCHED FEATURE COUNT

    return features

extract_url_features("python test_url.py")

