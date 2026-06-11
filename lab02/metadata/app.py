"""Simulated AWS metadata service (IMDS) for SSRF chain"""
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/latest/meta-data/')
def metadata_root():
    return "ami-id\ninstance-id\nlocal-ipv4\niam/\nhostname\n"

@app.route('/latest/meta-data/ami-id')
def ami_id():
    return "ami-0bot2root2026"

@app.route('/latest/meta-data/instance-id')
def instance_id():
    return "i-0b2r00tlab02"

@app.route('/latest/meta-data/local-ipv4')
def local_ip():
    return "10.10.3.50"

@app.route('/latest/meta-data/hostname')
def hostname():
    return "lab02-metadata.internal"

@app.route('/latest/meta-data/iam/')
def iam_root():
    return "security-credentials/"

@app.route('/latest/meta-data/iam/security-credentials/')
def iam_roles():
    return "lab02-admin-role"

@app.route('/latest/meta-data/iam/security-credentials/lab02-admin-role')
def iam_creds():
    return jsonify({
        "Code": "Success",
        "AccessKeyId": "AKIA-BOT2ROOT-FAKE-KEY",
        "SecretAccessKey": "bot2root-fake-secret-key-2026-do-not-use",
        "Token": "FakeSessionToken-Bot2Root-2026",
        "Expiration": "2026-12-31T23:59:59Z",
        "Note": "These are dummy credentials for CTF training only",
        "Flag": "FLAG{b2r_ssrf_metadata_exposure_6d4a}",
        "Hint": "Use the SSH credentials from /api/internal/credentials to pivot to lab02-ssh"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
