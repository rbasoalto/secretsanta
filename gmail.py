import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
import base64
from googleapiclient.errors import HttpError
from email.message import EmailMessage


class GMailAPIEmailSender(object):
    def __init__(self):
        print("Building GMail API email sender")

    def __enter__(self):
        # We expect client_secret.json to exist and have the OAuth2 stuff, get it from Cloud Console
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            'client_secret.json',
            scopes=['https://www.googleapis.com/auth/gmail.send'])

        # Irrelevant, we only need to paste it later
        flow.redirect_uri = 'http://localhost:8080/callback'

        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true')

        print(f"Go to {authorization_url}")

        redirect_url = input("Paste the redirected URL here: ")

        # Google's OAuth2 lib panics on http
        if redirect_url.startswith('http://'):
            redirect_url = 'https' + redirect_url.removeprefix('http')

        flow.fetch_token(authorization_response=redirect_url)
        credentials = flow.credentials
        self.gmail = build('gmail', 'v1', credentials=credentials)

    def __exit__(self, type, value, traceback):
        self.gmail = None

    def send_mail(self, recipient, subject, body):
        try:
            message = EmailMessage()

            message.set_content(body)
            message['To'] = recipient['email']
            message['From'] = 'secretsanta@basoalto.cl'
            message['Subject'] = subject

            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

            create_message = {
                'raw': encoded_message,
            }

            send_message = self.gmail.users().messages().send(userId="me", body=create_message).execute()

            print(f"Message ID {send_message['id']} sent to {recipient['email']}")
        except HttpError as error:
            print(f"Error!!!1: {error}")
            raise error
