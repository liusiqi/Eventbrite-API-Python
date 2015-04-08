import urllib
import argparse #for command-line interfaces
import webbrowser
import requests
import BaseHTTPServer
from urlparse import urlparse, parse_qs

EB_API_BASE = "https://www.eventbrite.com"
AUTH_CODE_ENDPOINT = "/oauth/authorize"
ACCESS_TOKEN_ENDPOINT = "/oauth/token"
HOST_NAME = '127.0.0.1'
PORT_NUMBER = 8000

Application_key = "CZGISCZYCNNAL5HXMB"
Client_secret = "5NN23LZE3IPLGQOTPFWTDEDADW5BXL2WF6TERUH6KZAI2EIHXE"
Personal_OAuth_token = "Q5Q3OP7BGUN5E32YZHGY"
Anonymous_access_OAuth_token = "Y3XAXDF62BIL5QNRBMTX"
authorization_code = "1"

def oauth_dialog(application_key):
    # Construct the oauth_dialog_url.
    url_parameters = urllib.urlencode({'client_id':application_key,'response_type':'code'})
    auth_dialog_url = EB_API_BASE + AUTH_CODE_ENDPOINT + '?' + url_parameters
    print "\nThe auth dialog url was " + auth_dialog_url + "\n"
    webbrowser.open(auth_dialog_url, new = 2)
    

class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    # A Base Classe to handle requests to and from Eventbrite
    

    def do_HEAD(self):
        # Sends Headers.
        self.send_response(200)
        self.send_header("Content-type","application/x-www-form-urlencoded")
        self.end_headers()

    def print_message(self,message):
        self.wfile.write("<body><p>%s</p>"%message)

    def do_GET(self):
        #Processes a response from Eventbrite
        # 1. Send a 200 OK status back to the server to let it know the request is received
        self.do_HEAD(self);

        # 2. do_GET means when receves a GET request, parses it. Here the temp_code is included in the query string of the path
        #    if the request is using POST method, then this class need to have a do_POST method which python 2.7 HTTPRequestHanlder doesn't have.
        self.wfile.write("<html><head><title>Eventbrite API - "
                      "OAuth Sample Redirect Page.</title></head>")

        # Parse authorization token from redirect response
        # 1) object s: self
        # 2) s.path is the URL of the browser
        # 3) urlparse: parses a URL into 6 components(a 6-tuple), each tuple item is a string, ex -> urlparse(scheme://netloc/path;parameters?query#fragment) => (scheme='http', netloc='www.blabla.edu:80', path='/.../Python.html', params = 'bla', query='code=sth', fragment=' ') 
        # 4) parse_qs: parses a query string and returns a dictionary of key: list pair.
        # 5) So .get('code') returns a list.
        authorization_code = parse_qs(urlparse(self.path).query).get('code',[])

        if len(authorization_code) > 0:
            authorization_code = authorization_code[0]
            self.print_message('Your temporary code is ' + authorization_code)
        else:
            authorization_code = None
            self.print_message('Error getting authorization code')

        if authorization_code:
            access_token = self.exchange_code_for_token(authorization_code, Application_key, Client_secret)
            if access_token:
                self.print_message('Your long lived access token is ' + access_token)
            else:
                self.print_message('No Authorization Code was returned. Were the username and password correct?')

        self.wfile.write("</body></html>")

    def exchange_code_for_token(self, auth_code, api_key, client_secret):
        data = {"client_secret": client_secret, "code": auth_code, "client_id":client_id,"grant_type":"authorization_code"}
        data_parameters = urllib.urlencode(data)
        access_token_uri = EB_API_BASE + ACCESS_TOKEN_ENDPOINT
        access_token_response = requests.post(access_token_uri, data=data_parameters)
        access_json = access_token_response.json()

        if 'access_token' in access_json:
            return access_json
        else:
            self.print_message('Problems exhanging the autho code for your access token. Error message :%s' % access_json)
            return None
        

if __name__ == "__main__":
    oauth_dialog(Application_key)
    server_class = BaseHTTPServer.HTTPServer
    # The server which is a HTTPServer sits and waits on the address/port. When a GET or POST request comes in, it parses it.
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
    httpd.handle_request() #if get_request returns nothing with a timeout and handle_request tries to handle that nothing.
