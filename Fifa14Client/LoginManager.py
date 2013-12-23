import json
import requests


class LoginManager(object):
    def __init__(self, email, password, security_hash, form_data):
        self.email = email
        self.password = password
        self.security_hash = security_hash
        self.NUCID = form_data['nuc']
        self.form_data = json.dumps(form_data, separators=(',', ':'))
        #Belows are the things we will need in login process
        self.EASFC_WEB_SESSION = ""
        self.XSRF_TOKEN = ""
        self.JSESSIONID = ""
        self.REMID = ""
        self.SID = ""
        self.FUTWEB = ""
        self.X_UT_SID = ""
        self.FUTWEBPHISHING = ""

    def login(self):
        '''returns a tuple of (FUTWEBPHISHING,EASF-WEB-SESSION) as there are the only two keys needed for doing tasks in ultimate team'''
        #This years ultimate teams login system is pointlessly complicated
        #go to ultimate team login and get XSRF and EASFC tokens.
        r = requests.get('http://www.easports.com/uk/fifa/football-club/ultimate-team', allow_redirects=False)
        self.EASFC_WEB_SESSION = r.cookies['EASFC-WEB-SESSION']
        self.XSRF_TOKEN = r.cookies['XSRF-TOKEN']
        #next we go to /connect/?auth so we can get the next url in line
        next_loc = r.headers['location']#/connect/?auth=xxx
        r = requests.get(next_loc, allow_redirects=False)
        #Now we go to /p/web/login?fid=xxx to once again get the next url and JSESSIONID
        next_loc = r.headers['location']# /p/web/login?fid=xxx
        r = requests.get(next_loc, allow_redirects=False)
        self.JSESSIONID = r.cookies['JSESSIONID']
        #url = https://signin.ea.com/p/web/login?execution=xxx
        #we post login info here
        #needed items = We get next location
        next_loc = r.headers['location']#https://signin.ea.com/p/web/login?execution=xxx
        headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Host': 'signin.ea.com',
                   'Origin': 'https://signin.ea.com'}
        cookies = {'JSESSIONID': self.JSESSIONID}
        payload = {'email': self.email, 'password': self.password, '_rememberMe': 'on', 'rememberMe': 'on',
                   '_eventId': 'submit', 'facebookAuth': ''}
        r = requests.post(next_loc, headers=headers, data=payload, allow_redirects=False, cookies=cookies)
        #next_loc leads us to https://accounts.ea.com/connect/auth?scope=basic...
        #We need to get sid and remid
        next_loc = r.headers['location']#https://accounts.ea.com/connect/auth?scope=basic...
        r = requests.get(next_loc, allow_redirects=False, headers={'Host': 'accounts.ea.com'})
        #If no REMID username or password is wrong
        try:
            self.REMID = r.cookies['remid']
        except Exception:
            return False
        self.SID = r.cookies['sid']
        #next_loc goes to http://www.easports.com/fifa/football-club/login_check?state=
        #we get new EASFC-WEB-SESSION
        next_loc = r.headers['location']#http://www.easports.com/fifa/football-club/login_check?state=
        headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Host': 'www.easports.com'}
        cookies = {'EASFC-WEB-SESSION': self.EASFC_WEB_SESSION, 'hl': 'uk', 'XSRF-TOKEN': self.XSRF_TOKEN}
        r = requests.get(next_loc, headers=headers, cookies=cookies, allow_redirects=False)
        self.EASFC_WEB_SESSION = r.cookies['EASFC-WEB-SESSION']
        #We are now done with the first round of idiotic redirects
        new_url = 'http://www.easports.com/iframe/fut/'
        #go here to get futweb
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        cookies = {'EASFC-WEB-SESSION': self.EASFC_WEB_SESSION, 'hl': 'uk', 'XSRF-TOKEN': self.XSRF_TOKEN}
        r = requests.get(new_url, headers=headers, cookies=cookies, allow_redirects=False)
        self.FUTWEB = r.cookies['futweb']
        #here comes some more redirects...
        #next_loc goes https://accounts.ea.com/connect/auth?response_type=code&client_id=
        #we get new sid value
        next_loc = r.headers['location']#https://accounts.ea.com/connect/auth?response_type=code&client_id=
        cookies = {'sid': self.SID, 'remid': self.REMID}
        r = requests.get(next_loc, cookies=cookies, allow_redirects=False)
        self.SID = r.cookies['sid']
        #we now go to http://www.easports.com/iframe/fut/login_check?state=xxx
        #we get a new futweb value here
        next_loc = r.headers['location']#http://www.easports.com/fifa/football-club/login_check?state=
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        cookies = {'futweb': self.FUTWEB, 'EASFC-WEB-SESSION': self.EASFC_WEB_SESSION, 'hl': 'uk',
                   'XSRF-TOKEN': self.XSRF_TOKEN}
        r = requests.get(next_loc, headers=headers, cookies=cookies, allow_redirects=False)
        self.FUTWEB = r.cookies['futweb']
        #Now time to go to http://www.easports.com/iframe/fut/p/ut/auth
        #We need to post the form_data
        #the response gives us the X-UT-SID that we need
        headers = {'Content-Type': 'application/json', 'Easw-Session-Data-Nucleus-Id': self.NUCID,
                   'Content-Length': len(self.form_data), 'X-UT-Route': 'https://utas.fut.ea.com:443'}
        cookies = {'futweb': self.FUTWEB, 'EASFC-WEB-SESSION': self.EASFC_WEB_SESSION, 'hl': 'uk',
                   'XSRF-TOKEN': self.XSRF_TOKEN, 'device_view': 'not_mobile'}
        r = requests.post('http://www.easports.com/iframe/fut/p/ut/auth', headers=headers, cookies=cookies,
                          data=self.form_data)
        #This will fail if the fomr_data is invalid or wrong
        try:
            self.X_UT_SID = dict(r.json())['sid']
        except:
            return False
            #We now need the FUTWebPhishing key
        #This is gotten by answereing the securtiy question
        headers = {'Content-Type': 'application/x-www-form-urlencoded',
                   'Easw-Session-Data-Nucleus-Id': self.NUCID,
                   'Content-Length': len(self.form_data),
                   'X-UT-Route': 'https://utas.fut.ea.com:443',
                   'X-UT-SID': self.X_UT_SID}

        cookies = {'futweb': self.FUTWEB, 'EASFC-WEB-SESSION': self.EASFC_WEB_SESSION, 'hl': 'uk',
                   'XSRF-TOKEN': self.XSRF_TOKEN, 'device_view': 'not_mobile'}
        payload = {'answer': self.security_hash}
        r = requests.post('http://www.easports.com/iframe/fut/p/ut/game/fifa14/phishing/validate', headers=headers,
                          cookies=cookies, data=payload)
        fut_string = r.headers['Set-Cookie'].split(';')[0]
        #we need both sides of futwebphishing so we spit it and store it in a dict
        #if it fails it is due not having valid security_hash
        try:
            self.FUTWEBPHISHING = fut_string.split('=')[1]
        except:
            return False
            #return the two keys that we need to make requests on the web app
        return (self.X_UT_SID, self.FUTWEBPHISHING)
        #Fun stuff logging in right?

    def get_FUTWEBPHISHING(self):
        return self.FUTWEBPHISHING

    def get_X_UT_SID(self):
        return self.X_UT_SID

