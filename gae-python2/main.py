import webapp2
import time
import base64
import urllib
import json
from google.appengine.api import app_identity
from google.appengine.api import urlfetch

class MainPage(webapp2.RequestHandler):
    def __base64(self, data):
        return base64.urlsafe_b64encode(data).replace("=", "")
        
    def __fetch_service_account_public_key_id(self):
        return  app_identity.sign_blob("dummydata")[0]
        
    def __create_self_signed_jwt(self, audience):
        kid = self.__fetch_service_account_public_key_id()
        iat = int(time.time()) 
        exp = iat + 3600
        iss = app_identity.get_service_account_name()
        
        header = "{\"typ\": \"JWT\", \"alg\": \"RS256\", \"kid\": \"%s\"}" % kid
        body  = "{\"aud\": \"https://www.googleapis.com/oauth2/v4/token\", \"iss\": \"%s\", \"exp\": %d, \"iat\": %d, \"target_audience\": \"%s\"}" % (iss, exp, iat, audience)
        
        header_base64 = self.__base64(header)
        body_base64 = self.__base64(body)
        signature_base64 = self.__base64(app_identity.sign_blob("%s.%s" %(header_base64, body_base64))[1])
        
        return "%s.%s.%s" % (header_base64, body_base64, signature_base64)
        
    def __fetch_idtoken(self, audience):
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        form_data = urllib.urlencode(
            { 
                "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                "assertion": self.__create_self_signed_jwt(audience)
            })
        response = urlfetch.fetch(
            url="https://www.googleapis.com/oauth2/v4/token",
            payload=form_data,
            method=urlfetch.POST,
            headers=headers)
        
        return json.loads(response.content)["id_token"]

    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        
        audience = "https://example.com"
        try:
            self.response.write("Service Account: %s\n" % app_identity.get_service_account_name())
            self.response.write("Service Account Key ID: %s\n" % self.__fetch_service_account_public_key_id())
            self.response.write("\n")
            self.response.write("Service Account-signed JWT for audience '%s': %s\n" % (audience, self.__create_self_signed_jwt(audience)))
            self.response.write("Service Account Certificate: https://www.googleapis.com/service_accounts/v1/metadata/x509/%s\n" % app_identity.get_service_account_name())
            self.response.write("\n")
            self.response.write("Google-signed ID Token for audience '%s': %s\n" % (audience, self.__fetch_idtoken(audience)))
            self.response.write("Google certificate: https://www.googleapis.com/oauth2/v1/certs\n")
            
        except Exception as e:
            self.response.write(e)
        

app = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)