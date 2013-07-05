import json
import urllib
import oauth2 as oauth

from .oauth import OAuthContacts


class TwitterFollowers(OAuthContacts):
    request_token_url = "https://api.twitter.com/oauth/request_token"
    authorize_url = "https://api.twitter.com/oauth/authorize"
    access_token_url = "https://api.twitter.com/oauth/access_token"

    verify_credentials_url = "https://api.twitter.com/1.1/account/verify_credentials.json"
    get_followers_list_url = "https://api.twitter.com/1.1/followers/list.json?screen_name=%s&cursor=%d&skip_status=true&include_user_entities=false"
    send_direct_message_url = "https://api.twitter.com/1.1/direct_messages/new.json"

    def __init__(self, *args, **kwargs):
        self.screen_name = None
        super(TwitterFollowers, self).__init__(*args, **kwargs)

    def get_user_screen_name(self):
        if self.screen_name is None:
            token = oauth.Token(self.access_token, self.access_token_secret)
            client = oauth.Client(self.consumer, token)
            resp, content = client.request(self.verify_credentials_url, "GET")
            if resp.get('status') == '200':
                data = json.loads(content)
                self.screen_name = data.get('screen_name')
            else:
                raise Exception("Cannot retrieve user screen name")
        return self.screen_name

    def get_contacts(self):
        super(TwitterFollowers, self).get_contacts()
        token = oauth.Token(self.access_token, self.access_token_secret)
        client = oauth.Client(self.consumer, token)

        screen_name = self.get_user_screen_name()

        followers = []

        next_cursor = -1
        while next_cursor != 0:
            resp, content = client.request(self.get_followers_list_url % (screen_name, next_cursor), "GET")
            if resp.get('status') == '200':
                data = json.loads(content)
                next_cursor = data['next_cursor']
                followers.extend(data['users'])
            else:
                raise Exception("There was an error while fetching followers: %s" % content)

        return followers

    def send_direct_message(self, user, message):
        if len(message) > 140:
            raise Exception("The message is too long. Maximum length is 140 characters.")

        token = oauth.Token(self.access_token, self.access_token_secret)
        client = oauth.Client(self.consumer, token)

        params = {'screen_name': user,
                  'text': message.encode('utf-8')}
        encoded_params = urllib.urlencode(params)
        resp, content = client.request("%s?%s" % (self.send_direct_message_url, encoded_params), "POST")
        print "Sent?", resp['status'], content
        if resp.get('status') != '200':
            print content
            raise Exception("There was an error when sending the direct message: %s" % content)
