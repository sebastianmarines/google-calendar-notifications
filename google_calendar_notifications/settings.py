from pathlib import Path

_home = Path.home()

CREDENTIALS = {
    'installed': {
        'client_id':
        '542312399086-icgtqmiilth907lkvqrsuqpat8oqe2g0.apps.googleusercontent.com',
        'project_id': 'root-rampart-324919',
        'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
        'token_uri': 'https://oauth2.googleapis.com/token',
        'auth_provider_x509_cert_url':
        'https://www.googleapis.com/oauth2/v1/certs',
        'client_secret': 'xn8EAaKkIofraz75bA7z6GXN',
        'redirect_uris': ['urn:ietf:wg:oauth:2.0:oob', 'http://localhost']
    }
}

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

APP_DIRECTORY = _home / ".google-calendar-notifications"