from Fifa14Client import Card
import requests
from Fifa14Client.Exceptions import BadRequestException,FUTErrorCodeException

class WebAppFunctioner(object):
    COIN_URL = 'https://utas.%sfut.ea.com/ut/game/fifa14/user/credits'
    TRANSFER_URL = 'https://utas.%sfut.ea.com/ut/game/fifa14/transfermarket?type=%s&lev=%s' \
                   '&pos=%s&num=%s&team=%s&macr=%s&micr=%s&minb=%s&nat=%s&maxb=%s' \
                   '&playStyle=%s&leaga=%s&start=%s&cat=%s&definitionId=%s&maskedDefId=%s'

    BID_URL = 'https://utas.%sfut.ea.com/ut/game/fifa14/trade/%s/bid'
    MOVE_URL = 'https://utas.%sfut.ea.com/ut/game/fifa14/item'
    UNASSIGNED_URL = 'https://utas.%sfut.ea.com/ut/game/fifa14/purchased/items'
    LIST_CARD_URL = 'https://utas.%sfut.ea.com/ut/game/fifa14/auctionhouse'
    TRADEPILE_URL = 'https://utas.%sfut.ea.com/ut/game/fifa14/tradepile'
    QUICKSELL_URL = 'https://utas.%sfut.ea.com/ut/game/fifa14/item/%s'
    WATCHLIST_URL = 'https://utas.%sfut.ea.com/ut/game/fifa14/watchlist'
    WATCHLIST_REMOVE_URL = 'https://utas.%sfut.ea.com/ut/game/fifa14/watchlist?tradeId=%s'
    TRADEPILE_REMOVE_URL = 'https://utas.%sfut.ea.com/ut/game/fifa14/trade/%s'

    def __init__(self, login_manager):
        self.login_manager = login_manager
        if self.login_manager.ini_platform in ['ps3','pc']:
            self.platform_string = 's2.'
        else:
            self.platform_string = ''

    def get_headers(self, http_method):
        """ Returns the headers yo be used in the request
            header_type is the http method ex GET,POST,PUT,DELETE,etc
        """
        return {'X-UT-PHISHING-TOKEN': self.login_manager.fut_web_phishing,
                'X-UT-SID': self.login_manager.x_ut_sid,
                'X-HTTP-Method-Override': http_method}

    def get_coin_amount(self):
        """Returns amount of coins the account has
           Raises Exception if unavailable to get coins
        """
        r = requests.post(self.COIN_URL % self.platform_string, headers=self.get_headers('GET'))
        try:
            json = r.json()
        except ValueError:
            raise BadRequestException('Json could not be decoded.')
        if 'credits' in json:
            return json['credits']
        elif 'code' in json:
            raise FUTErrorCodeException('Error retrieving coins\n',json)
        else:
            raise BadRequestException('Can not retrieve coins.')

    def search(self, type="", lev="", pos="", num=10, team="",
               macr="", micr="", minb="", nat="", maxb="",
               playStyle="", leag="", start=0, cat="",
               definitionId="", maskedDefId=""):
        """ Returns a list of Card objects from the search paramters given
            Raises an exception if the request fails.
            Args-
            type - type of card eg player, development
            lev -  quality of card = gold,bronze
            pos - position
            num - amount of cards to return
            team - teamid
            macr - max price
            micr - min price
            minb - min buy now
            maxb - max buy now
            playStyle - type of chemistry style
            leag - league id
            start - where to start
            cat - category, ex contract
            definitionId - you pass the assetId to it and it responds with only those types of cards
            maskeddefId - not certain but seems to do the same as definitionId
        """
        the_url = self.TRANSFER_URL % (self.platform_string,type, lev, pos, num, team, macr, micr, minb, nat, maxb,
                                       playStyle, leag, start, cat, definitionId, maskedDefId)
        r = requests.post(the_url, headers=self.get_headers('GET'))
        try:
            json = r.json()
        except:
            raise BadRequestException("Could not complete search. No JSON object could be decoded")
        if 'auctionInfo' in  json:
            card_list = r.json()['auctionInfo']
            return [Card.Card(card_dict) for card_dict in card_list]
        elif 'code' in json:
            raise FUTErrorCodeException("Could not get complete search.",json)

    def bid(self, card, price):
        """Bids on card that is specified in argument, raises exception if bid fails."""
        payload = '{"bid":%s}' % (price)
        the_url = self.BID_URL % (self.platform_string, card.tradeId)
        r = requests.post(the_url, headers=self.get_headers('PUT'), data=payload)
        #There will be no code key in the json if the bid is sucessful
        try:
            json = r.json()
        except:
            raise BadRequestException("Could not bid. No JSON Object could be decoded.")
        if 'code' in json:
            raise FUTErrorCodeException("Could not place bid.",json)


    def move(self, card, pile):
        """Moves card to specified pile, raises an exception on failure"""
        payload = '{"itemData":[{"id":"%s","pile":"%s"}]}' % (card.id, pile)
        r = requests.post(self.MOVE_URL % self.platform_string, headers=self.get_headers('PUT'), data=payload)
        #There will be no code key in the json if the move is sucessful
        try:
            json = r.json()
        except:
            raise BadRequestException("Could not move card to %s. No JSON Object could be decoded." % pile)
        if 'code' in json:
            raise FUTErrorCodeException("Could not move card to %s" % pile,json)

    def get_unassigned_pile(self):
        """Returns a list of Card objects from the unnasigned pile,raises exception on failure."""
        r = requests.post(self.UNASSIGNED_URL % self.platform_string, headers=self.get_headers('GET'))
        try:
            json = r.json()
        except:
            raise BadRequestException("Could not get unassigned pile. No JSON object could be decoded")
        if 'itemData' in  json:
            card_list = r.json()['itemData']
            return [Card.Card(card_dict) for card_dict in card_list]
        elif 'code' in json:
            raise FUTErrorCodeException("Could not get unassigned pile.",json)


    def list_card(self, card, starting_bid, buy_now_price=0, duration=3600):
        """Lists card in transfer market for specified price and buy now price"""
        payload = '{"buyNowPrice":%s,"itemData":{"id":%s},"duration":%s,"startingBid":%s}' % \
                  (buy_now_price, card.id, duration, starting_bid)
        r = requests.post(self.LIST_CARD_URL % self.platform_string, headers=self.get_headers('POST'), data=payload)
        #There will be no code key in the json if the listing is sucessful
        try:
            json = r.json()
        except:
            raise BadRequestException("Could not list card to tradepile. No JSON Object could be decoded.")
        if 'code' in json:
            raise FUTErrorCodeException("Could not list card in tradepile.",json)

    def get_tradepile(self):
        """Returns a list of Card objects from the tradepile"""
        r = requests.post(self.TRADEPILE_URL % self.platform_string, headers=self.get_headers('GET'))
        card_list = r.json()['auctionInfo']
        return [Card.Card(card_dict) for card_dict in card_list]

    def quicksell(self, card):
        """Quicksell's specified card, returns True if successful"""
        the_url = self.QUICKSELL_URL % (self.platform_string,card.id)
        r = requests.post(the_url, headers=self.get_headers('DELETE'))
        return "code" not in dict(r.json())

    def get_watchlist(self):
        """Returns a list of Card objects from the watchlist"""
        r = requests.post(self.WATCHLIST_URL % self.platform_string, headers=self.get_headers('GET'))
        card_list = r.json()['auctionInfo']
        return [Card.Card(card_dict) for card_dict in card_list]

    def remove_card_from_watchlist(self, card):
        """Removes card from watchlist, returns True if successful"""
        the_url = self.WATCHLIST_REMOVE_URL % (self.platform_string, card.tradeId)
        r = requests.post(the_url, headers=self.get_headers('DELETE'))
        try:
            return "code" not in dict(r.json())
        except:
            return False

    def remove_from_tradepile(self, card):
        """Removes card from tradepile, returns True if successful"""
        the_url = self.TRADEPILE_REMOVE_URL % (self.platform_string, card.tradeId)
        r = requests.post(the_url, headers=self.get_headers('DELETE'))
        return "code" not in dict(r.json())

