import os
import requests
import redis
from flask import Flask, request, jsonify

app = Flask(__name__)

REDIS_HOST = os.environ.get('REDIS_HOST', '10.10.3.30')
METADATA_HOST = os.environ.get('METADATA_HOST', '10.10.3.50')


@app.route('/')
def index():
    return jsonify({
        'service': 'Bot2Root Internal API',
        'version': '2.0',
        'endpoints': ['/api/health', '/api/fetch', '/api/cache', '/api/docs']
    })


@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'internal': True, 'network': 'lab02'})


@app.route('/api/docs')
def docs():
    """API documentation - discoverable via dir brute force"""
    return jsonify({
        'api_documentation': {
            '/api/health': 'Health check endpoint',
            '/api/fetch': 'URL fetcher - GET /api/fetch?url=<target>',
            '/api/cache': 'Redis cache interface - GET /api/cache?key=<key>',
            '/api/internal/credentials': 'Internal only - restricted to localhost',
            '/api/internal/config': 'Internal only - system configuration',
        },
        'note': 'Some endpoints are restricted to internal access only (127.0.0.1)',
        'hint': 'Can you make the server request its own endpoints?'
    })


@app.route('/api/fetch', methods=['POST', 'GET'])
def fetch_url():
    """SSRF vulnerability - fetches arbitrary URLs from internal network.
    
    This is the key attack vector:
    - Student reaches this endpoint via proxychains (lab02-net: 10.10.2.10)
    - lab02-api is also on lab03-net (10.10.3.10) where metadata/redis live
    - Student CANNOT reach lab03 directly (no route from gateway)
    - SSRF lets the API fetch from lab03 services on behalf of the student
    
    Key SSRF targets:
    1. http://127.0.0.1:3000/api/internal/credentials  (localhost bypass)
    2. http://10.10.3.50/latest/meta-data/              (metadata via lab03)
    3. http://10.10.3.50/latest/meta-data/iam/security-credentials/lab02-admin-role
    """
    url = request.args.get('url', '')
    if not url and request.is_json:
        url = request.json.get('url', '')

    if not url:
        return jsonify({
            'error': 'Missing url parameter',
            'usage': 'GET /api/fetch?url=<target_url>',
            'example': '/api/fetch?url=http://example.com'
        }), 400

    try:
        resp = requests.get(url, timeout=5, allow_redirects=True)
        return jsonify({
            'status': resp.status_code,
            'headers': dict(resp.headers),
            'body': resp.text[:10000]
        })
    except requests.exceptions.ConnectionError:
        return jsonify({'error': 'Connection failed', 'url': url}), 502
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/cache', methods=['GET', 'POST'])
def cache():
    """Redis interaction via lab03-net"""
    try:
        r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

        if request.method == 'POST':
            data = request.json or {}
            key = data.get('key', '')
            value = data.get('value', '')
            if key and value:
                r.set(key, value)
                return jsonify({'status': 'stored', 'key': key})

        key = request.args.get('key', '')
        if key:
            val = r.get(key)
            return jsonify({'key': key, 'value': val})

        keys = r.keys('*')
        return jsonify({'keys': keys})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/internal/credentials')
def internal_creds():
    """Internal endpoint - only accessible from localhost (SSRF bypass required).
    
    Returns SSH credentials for lab02-ssh and a hint about nmap.
    Does NOT give root password - student must use LOLBin.
    """
    if request.remote_addr not in ('127.0.0.1', '::1', '10.10.3.10'):
        return jsonify({'error': 'Access denied - internal only', 'hint': 'This endpoint is accessible from localhost'}), 403

    return jsonify({
        'ssh_credentials': {
            'host': '10.10.2.40',
            'port': 22,
            'username': 'developer',
            'password': 'dev_2026_bot2root!',
            'note': 'SSH into lab02-ssh for further exploitation'
        },
        'redis': {
            'host': '10.10.3.30',
            'port': 6379,
            'auth': 'none',
            'note': 'Redis has no authentication - check stored keys'
        },
        'flag': 'FLAG{b2r_ssrf_credential_leak_b2e7}',
        'hint': 'After SSH access, check what commands you can run with elevated privileges'
    })


@app.route('/api/internal/config')
def internal_config():
    """Another internal endpoint - system config info"""
    if request.remote_addr not in ('127.0.0.1', '::1', '10.10.3.10'):
        return jsonify({'error': 'Access denied - internal only'}), 403

    return jsonify({
        'system': {
            'lab03_network': '10.10.3.0/24',
            'services': {
                'metadata': '10.10.3.50:80',
                'redis': '10.10.3.30:6379',
                'java': '10.10.3.20:8443',
            }
        },
        'note': 'Lab03 is only accessible from this API server and lab02-ssh'
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=False)
