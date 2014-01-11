import json
import requests
import re
import time
from Fifa14Client.Exceptions import LoginException


class LoginManager(object):
    MAIN_ULTIMATE_TEAM_URL = 'http://www.easports.com/uk/fifa/football-club/ultimate-team'
    IFRAME_FUT_URL = 'http://www.easports.com/iframe/fut/'
    ACCOUNT_INFORMATION_URL = 'http://www.easports.com/iframe/fut/p/ut/game/fifa14/user/accountinfo?_=%s000'
    AUTH_URL = 'http://www.easports.com/iframe/fut/p/ut/auth'
    PHISH_URL = 'http://www.easports.com/iframe/fut/p/ut/game/fifa14/phishing/validate'
    HOST_URL = 'https://utas.%sfut.ea.com:443'

    def __init__(self, email, password, security_hash,ini_platform):
        self.email = email
        self.password = password
        self.security_hash = security_hash
        self.ini_platform = ini_platform
        if self.ini_platform in ['pc','ps3']:
            self.HOST_URL = self.HOST_URL % ('s2.')
        elif self.ini_platform in ['xbox','ios','android']:
            self.HOST_URL = self.HOST_URL % ('')
        else:
            raise ValueError("Platform is invalid:platform must be xbox,ps3,pc,android,or ios")
        #things that will be grabbed from the login process
        self.easfc = None
        self.xsrf = None
        self.jsessionid = None
        self.futweb = None
        self.nucid = None
        self.persona_id = None
        self.platform = None
        self.persona_name = None
        self.form_data = None
        self.x_ut_sid = None
        self.fut_web_phishing = None

    def login(self):
        """ returns a tuple of (X-UT-SID, FUTWebPhishing)
            as there are the only two keys needed for doing tasks in ultimate team
            Though FutWebPhishing is renamed to X-UT-PHISHING-TOKEN when it is used for things such as bidding
        """
        #Start off by getting the XSRF-Token,EASFC-WEB-SESSION, and the next url that we need to go to
        #the XSRF-Token and EASFC-WEB-SESSION are needed for later requests
        tokens = self.get_easfc_and_xsrf()

        self.easfc = tokens['easfc']
        self.xsrf = tokens['xsrf']
        next_loc = tokens['next_loc']

        #Next step is to grab the JSESSIONID
        tokens = self.get_jsessionid(next_loc)

        self.jsessionid = tokens['jsessionid']
        next_loc = tokens['next_loc']

        #Now the next step is to post the login info and get remid and sid
        tokens = self.get_sid_and_remid(next_loc)

        self.sid = tokens['sid']
        self.remid = tokens['remid']
        next_loc = tokens['next_loc']

        #The EASFC-WEB-SESSION token is refreshed and we need to grab it
        self.easfc = self.get_easfc_second_time(next_loc)

        #The redirects are now done for a little bit
        #We now need to grab the futweb token
        tokens = self.get_futweb()
        self.futweb = tokens['futweb']
        next_loc = tokens['next_loc']

        #here comes some more redirects...
        #Now the sid token is refreshed and we need to grab it again
        tokens = self.get_sid_second_time(next_loc)
        self.sid = tokens['sid']
        next_loc = tokens['next_loc']

        #Next step is to refresh futweb token
        self.futweb = self.get_futweb_second_time(next_loc)

        #Now we need to get the NucleusID
        #it is used later as a header
        #and is needed as a variable to post for the phishing answer
        self.nucid = self.get_nucleusid()

        #We now need various account details to complete the information needed for the /auth POST
        account_info_dict = self.get_account_info()

        self.persona_id = account_info_dict['persona_id']
        self.persona_name = account_info_dict['persona_name']
        self.platform = account_info_dict['platform']

        #Now we need to set up the form_data
        self.form_data = {
            'isReadOnly':False,
            'sku':'FUT14WEB',
            'clientVersion':1,
            'nuc':int(self.nucid),
            'nucleusPersonaId':self.persona_id,
            'nucleusPersonaDisplayName':self.persona_name,
            'nucleusPersonaPlatform':self.platform,
            'locale':'en-GB',
            'method':'authcode',
            'priorityLevel':4,
            'identification':{ "authCode": "" }
        }
        self.form_data = json.dumps(self.form_data, separators=(',', ':'))
        #Now we need to go to /auth and grab the X-UT-SID token
        self.x_ut_sid = self.get_x_ut_sid()
        #The last step is to grab the FUTPhishing token
        self.fut_web_phishing = self.get_fut_web_phishing()
        #return the two keys that we need to make requests on the web app
        return (self.x_ut_sid, self.fut_web_phishing)
        #Fun stuff logging in right?

    def get_easfc_and_xsrf(self):
        """
        Requests the main ultimate team page url
        extracts the XSRF-Token,EASFC-WEB-SESSION, and next location from the response headers
        returns a dict of the three values with the keys being ['xsrf','easfc','next_loc']
        """
        r = requests.get(self.MAIN_ULTIMATE_TEAM_URL, allow_redirects=False)
        return {
                'xsrf':r.cookies['XSRF-TOKEN'],
                'easfc':r.cookies['EASFC-WEB-SESSION'],
                'next_loc':r.headers['location']
        }
    def get_jsessionid(self,url):
        """
        Goes to the url argument and follows that until it can get the JSESSIONID in the response headers
        returns a dict containing the JSESSIONID and the location headers from the last response
        the keys are ['jsessionid','next_loc']
        """
        r = requests.get(url, allow_redirects=False)
        next_loc = r.headers['location']
        r = requests.get(next_loc, allow_redirects=False)
        return {
            'jsessionid': r.cookies['JSESSIONID'],
            'next_loc': r.headers['location']
        }
    def get_sid_and_remid(self,url):
        """
        Goes to url and follows redirects until the sid and remid are in the response headers
        This method POSTs the login information
        returns a dict containing sid,remid,and location headers
        the keys are ['sid','remid',next_loc]
        """
        #The only cookie that we have accumulated so far is the JSESSIONID
        cookies = {'JSESSIONID': self.jsessionid}
        #login information that needs to be posted
        payload = {'email': self.email, 'password': self.password, '_rememberMe': 'on', 'rememberMe': 'on',
                   '_eventId': 'submit', 'facebookAuth': ''}
        r = requests.post(url, data=payload, allow_redirects=False, cookies=cookies)
        next_loc = r.headers['location']
        r = requests.get(next_loc, allow_redirects=False, headers={'Host': 'accounts.ea.com'})
        try:
            return{
                'sid':r.cookies['sid'],
                'remid':r.cookies['remid'],
                'next_loc':r.headers['location']
            }
        except:
            raise LoginException("Login Failed: Email or Password is wrong.")
    def get_easfc_second_time(self,url):
        """
        Goes to the specified url and returns the new EASFC-WEB-SESSION cookie
        returns the EASFC-WEB-SESSION token
        """
        cookies = {'EASFC-WEB-SESSION': self.easfc, 'hl': 'uk', 'XSRF-TOKEN': self.xsrf}
        r = requests.get(url, cookies=cookies, allow_redirects=False)
        return r.cookies['EASFC-WEB-SESSION']
    def get_futweb(self):
        """
        Goes to the /iframe/fut endpoint and grabs the futweb cookie
        returns a dict of the futweb token and location response header
        keys are ['futweb','location']
        """
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        cookies = {'EASFC-WEB-SESSION': self.easfc, 'hl': 'uk', 'XSRF-TOKEN': self.xsrf}
        r = requests.get(self.IFRAME_FUT_URL, headers=headers, cookies=cookies, allow_redirects=False)
        return {
            'futweb':r.cookies['futweb'],
            'next_loc':r.headers['location']
        }
    def get_sid_second_time(self,url):
        """
        Goes to the url specified and grabs the sid cookie
        returns a dict of the sid token and the location response header
        keys are ['sid','next_loc']
        """
        cookies = {'sid': self.sid, 'remid': self.remid}
        r = requests.get(url, cookies=cookies, allow_redirects=False)
        return{
            'sid':r.cookies['sid'],
            'next_loc':r.headers['location']
        }
    def get_futweb_second_time(self,url):
        """
        Goes to the url specified and grabs the futweb token
        returns the futweb token
        """
        #we now go to http://www.easports.com/iframe/fut/login_check?state=xxx
        #we get a new futweb value here
        cookies = {'futweb': self.futweb, 'EASFC-WEB-SESSION': self.easfc, 'hl': 'uk',
                   'XSRF-TOKEN': self.xsrf}
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        r = requests.get(url,headers=headers, cookies=cookies, allow_redirects=False)
        return r.cookies['futweb']
    def get_nucleusid(self):
        """
        Goes to /iframe/fut/ and parses the html to find the NucleusId
        returns the NucleusId
        """
        cookies = {'futweb': self.futweb, 'EASFC-WEB-SESSION': self.easfc, 'hl': 'uk',
                   'XSRF-TOKEN': self.xsrf}
        r = requests.get(self.IFRAME_FUT_URL, cookies=cookies, allow_redirects=False)
        #regex to find the nucleus id
        m = re.findall("var EASW_ID = \'\d+\'", r.text)
        return m[0].split("'")[1]
    def get_account_info(self):
        """
        Goes to the account information url and grabs the gamertag,platform,and personaId
        Returns a dict of gamertag,platform,and personaId
        keys are ['persona_name,platform,persona_id']
        """
        headers = {'Content-Type': 'application/json','Easw-Session-Data-Nucleus-Id': self.nucid,
                   'X-UT-Route': self.HOST_URL}
        cookies = {'futweb': self.futweb, 'EASFC-WEB-SESSION': self.easfc, 'hl': 'uk',
                   'XSRF-TOKEN': self.xsrf}
        #The argument for the url is php time
        #There is a padding of three zeros at the end of the url
        #This is due to python not going to the same amount of digits as php does
        the_url = self.ACCOUNT_INFORMATION_URL % (int(time.time()))
        r = requests.get(the_url, headers=headers, cookies=cookies, allow_redirects=False)
        #This is the main part of the json that we need
        personas = r.json()['userAccountInfo']['personas'][0]

        return{
            'persona_name':personas['personaName'],
            'platform':personas['userClubList'][0]['platform'],
            'persona_id':personas['personaId']
        }
    def get_x_ut_sid(self):
        """
        Goes to the /auth endpoint and POSTs the form data
        Returns the X-UT-SID token
        """
        headers = {'Content-Type': 'application/json', 'Easw-Session-Data-Nucleus-Id': self.nucid,
                   'Content-Length': len(self.form_data), 'X-UT-Route': self.HOST_URL}
        cookies = {'futweb': self.futweb, 'EASFC-WEB-SESSION': self.easfc, 'hl': 'uk',
                   'XSRF-TOKEN': self.xsrf, 'device_view': 'not_mobile'}
        r = requests.post(self.AUTH_URL, headers=headers, cookies=cookies,
                          data=self.form_data)
        return r.json()['sid']

    def get_fut_web_phishing(self):
        """
        Goes to the phishing url and posts the security question hash.
        returns the FutWebPhishing token which is needed to do things such as bidding
        """
        headers = {'Content-Type': 'application/x-www-form-urlencoded',
                   'Easw-Session-Data-Nucleus-Id': self.nucid,
                   'Content-Length': len(self.form_data),
                   'X-UT-Route': self.HOST_URL,
                   'X-UT-SID': self.x_ut_sid}

        cookies = {'futweb': self.futweb, 'EASFC-WEB-SESSION': self.easfc, 'hl': 'uk',
                   'XSRF-TOKEN': self.xsrf, 'device_view': 'not_mobile'}
        payload = {'answer': self.security_hash}
        r = requests.post(self.PHISH_URL, headers=headers,cookies=cookies, data=payload)
        #The name is not always the same, but it is always the first cookie.
        try:
            fut_string = r.headers['Set-Cookie'].split(';')[0]
            return fut_string.split('=')[1]
        except:
            raise LoginException("Login Failed:Security answer is incorrect.")