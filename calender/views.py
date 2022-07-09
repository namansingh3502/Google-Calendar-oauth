import os
from django.http import HttpResponseRedirect, JsonResponse

from googleapiclient.discovery import build
import google_auth_oauthlib.flow

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


def GoogleCalendarInitView(request):
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'calender/cred.json',
        scopes=['https://www.googleapis.com/auth/calendar.events.readonly'])

    flow.redirect_uri = 'http://localhost:8000/rest/v1/calendar/redirect/'

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        state="dnksjnkjdsnv;l"
    )

    request.session['state'] = state

    return HttpResponseRedirect(authorization_url)


def GoogleCalendarRedirectView(request):
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'calender/cred.json',
        scopes=['https://www.googleapis.com/auth/calendar.events.readonly'],
    )

    flow.redirect_uri = 'http://localhost:8000/rest/v1/calendar/redirect/'

    authorization_response = request.build_absolute_uri()
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    request.session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes}

    service = build('calendar', 'v3', credentials=credentials)

    data = service.events().list(calendarId='primary', pageToken="").execute()

    return JsonResponse(data['items'], safe=False)
