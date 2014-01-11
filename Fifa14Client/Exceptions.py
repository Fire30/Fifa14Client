

class Fifa14Exception(Exception):
    pass

class BadRequestException(Fifa14Exception):
    pass

class FUTErrorCodeException(Fifa14Exception):
    def __init__(self,msg,json):
        #Possible keys in the json that will give more information
        for key in ['reason','message','code','debug','string']:
            if key in json:
                msg += '%s: %s\n' % (key,json[key])
        Fifa14Exception.__init__(self,msg)

class LoginException(Fifa14Exception):
    pass

