import json
import oauth2 as oauth
import urllib

from .oauth import OAuthContacts


class LinkedInConnections(OAuthContacts):
    request_token_url = "https://api.linkedin.com/uas/oauth/requestToken"
    authorize_url = "https://api.linkedin.com/uas/oauth/authorize"
    access_token_url = "https://api.linkedin.com/uas/oauth/accessToken"

    get_connections_url = "http://api.linkedin.com/v1/people/~/connections?format=json"
    send_messages_url = "http://api.linkedin.com/v1/people/~/mailbox"

    def get_contacts(self):
        super(LinkedInConnections, self).get_contacts()
        token = oauth.Token(self.access_token, self.access_token_secret)
        client = oauth.Client(self.consumer, token)

        resp, content = client.request(self.get_connections_url, "GET")
        if resp.get('status') == '200':
            data = json.loads(content)
            return [i for i in data['values'] if i['id']!="private"]

    def send_messages(self, receivers, subject, message):
        token = oauth.Token(self.access_token, self.access_token_secret)
        client = oauth.Client(self.consumer, token)

        recipients = [{"person": {"_path": "/people/%s" % r }}
                          for r in receivers]
        request = {'recipients': {'values': recipients},
                   'subject': subject.encode('utf-8'),
                   'body': message.encode('utf-8')}

        json_request = json.dumps(request)

        resp, content = client.request(self.send_messages_url, method="POST", body=json_request, headers={'Content-Type':'application/json'} )
