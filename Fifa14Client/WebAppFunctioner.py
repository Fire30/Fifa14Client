import LoginManager
import requests
import Card

class WebAppFunctioner(object):
    
    COIN_URL = 'https://utas.fut.ea.com/ut/game/fifa14/user/credits'
    TRANSFER_URL = 'https://utas.fut.ea.com/ut/game/fifa14/transfermarket?type=%s&lev=%s'\
                   '&pos=%s&num=%s&team=%s&macr=%s&micr=%s&minb=%s&nat=%s&maxb=%s'\
                   '&playStyle=%s&leaga=%s&start=%s&cat=%s&definitionId=%s&maskedDefId=%s'
    
    BID_URL = 'https://utas.fut.ea.com/ut/game/fifa14/trade/%s/bid'
    MOVE_URL = 'https://utas.fut.ea.com/ut/game/fifa14/item'
    UNASSIGNED_URL = 'https://utas.fut.ea.com/ut/game/fifa14/purchased/items'
    LIST_CARD_URL = 'https://utas.fut.ea.com/ut/game/fifa14/auctionhouse'
    TRADEPILE_URL = 'https://utas.fut.ea.com/ut/game/fifa14/tradepile'
    QUICKSELL_URL = 'https://utas.fut.ea.com/ut/game/fifa14/item/%s'
    WATCHLIST_URL = 'https://utas.fut.ea.com/ut/game/fifa14/watchlist'
    WATCHLIST_REMOVE_URL = 'https://utas.fut.ea.com/ut/game/fifa14/watchlist?tradeId=%s'
    TRADEPILE_REMOVE_URL = 'https://utas.fut.ea.com/ut/game/fifa14/trade/%s'
    
    def __init__(self,login_manager):
        self.login_manager = login_manager
    def get_coin_amount(self):
        """Returns amount of coins the account has"""
        headers = {'X-UT-PHISHING-TOKEN':self.login_manager.FUTWEBPHISHING,
                   'X-UT-SID':self.login_manager.X_UT_SID,
                   'X-HTTP-Method-Override':'GET'}
        
        r = requests.post(self.COIN_URL,headers = headers)
        coin_amount = dict(r.json())['credits']
        return coin_amount
    def search(self,type = "",lev = "",pos = "",num = 10,team = "",
               macr = "", micr = "",minb = "",nat = "",maxb = "",
               playStyle = "",leag = "",start = 0,cat = "",
               definitionId = "",maskedDefId = ""):
        """ Returns a list of Card objects from the search paramters given
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
        headers = {'X-UT-PHISHING-TOKEN':self.login_manager.FUTWEBPHISHING,
                   'X-UT-SID':self.login_manager.X_UT_SID,
                   'X-HTTP-Method-Override':'GET'}
        the_url = self.TRANSFER_URL % (type,lev,pos,num,team,macr,micr,minb,nat,maxb,
                                       playStyle,leag,start,cat,definitionId,maskedDefId)
        r = requests.post(the_url,headers = headers)
        auction_info  = r.json()['auctionInfo']
        return [Card.Card(card_dict) for card_dict in auction_info]
    def bid(self,card,price):
        """Bids on card that is specified in argument, returns True is succesfully bid on"""
        headers = {'X-UT-PHISHING-TOKEN':self.login_manager.FUTWEBPHISHING,
                   'X-UT-SID':self.login_manager.X_UT_SID,
                   'X-HTTP-Method-Override':'PUT'}
        payload = '{"bid":%s}' % (price)
        the_url = self.BID_URL % (card.tradeId)
        r = requests.post(the_url,headers = headers,data = payload)
        #There will be no code key in the json if the bid is sucessful
        return "code" not in dict(r.json())
    def move(self,card,pile):
        """Moves card to specified pile, returns True if successful"""
        headers = {'X-UT-PHISHING-TOKEN':self.login_manager.FUTWEBPHISHING,
                   'X-UT-SID':self.login_manager.X_UT_SID,
                   'X-HTTP-Method-Override':'PUT'}
        payload = '{"itemData":[{"id":"%s","pile":"%s"}]}' % (card.id,pile)
        r = requests.post(self.MOVE_URL,headers = headers,data = payload)
        #There will be no code key in the json if the move is sucessful
        return "code" not in dict(r.json())
    def get_unassigned_pile(self):
        """Returns a list of Card objects from the unnasigned pile"""
        headers = {'X-UT-PHISHING-TOKEN':self.login_manager.FUTWEBPHISHING,
                   'X-UT-SID':self.login_manager.X_UT_SID,
                   'X-HTTP-Method-Override':'GET'}
        r = requests.post(self.UNASSIGNED_URL,headers = headers)
        card_list  = r.json()['itemData']
        return [Card.Card(card_dict) for card_dict in card_list]
    def list_card(self,card,starting_bid, buy_now_price = 0,duration = 3600):
        """Lists card in transfer market for specified price and buy now price"""
        headers = {'X-UT-PHISHING-TOKEN':self.login_manager.FUTWEBPHISHING,
                   'X-UT-SID':self.login_manager.X_UT_SID,
                   'X-HTTP-Method-Override':'POST'}
        payload = '{"buyNowPrice":%s,"itemData":{"id":%s},"duration":%s,"startingBid":%s}' % (buy_now_price,card.id,duration,starting_bid) 
        r = requests.post(self.LIST_CARD_URL,headers = headers,data = payload)
        #There will be no code key in the json if the listing is sucessful
        return "code" not in dict(r.json())
    def get_tradepile(self):
        """Returns a list of Card objects from the tradepile"""
        headers = {'X-UT-PHISHING-TOKEN':self.login_manager.FUTWEBPHISHING,
                   'X-UT-SID':self.login_manager.X_UT_SID,
                   'X-HTTP-Method-Override':'GET'}
        r = requests.post(self.TRADEPILE_URL,headers = headers)
        card_list  = r.json()['auctionInfo']
        return [Card.Card(card_dict) for card_dict in card_list]
    def quicksell(self,card):
        """Quicksell's specified card, returns True if successful"""
        headers = {'X-UT-PHISHING-TOKEN':self.login_manager.FUTWEBPHISHING,
                   'X-UT-SID':self.login_manager.X_UT_SID,
                   'X-HTTP-Method-Override':'DELETE'}
        the_url = self.QUICKSELL_URL % (card.id)
        r = requests.post(the_url,headers = headers)
        return "code" not in dict(r.json())
    def get_watchlist(self):
        """Returns a list of Card objects from the watchlist"""
        headers = {'X-UT-PHISHING-TOKEN':self.login_manager.FUTWEBPHISHING,
                   'X-UT-SID':self.login_manager.X_UT_SID,
                   'X-HTTP-Method-Override':'GET'}
        r = requests.post(self.WATCHLIST_URL,headers = headers)
        card_list  = r.json()['auctionInfo']
        return [Card.Card(card_dict) for card_dict in card_list]
    def remove_card_from_watchlist(self,card):
        """Removes card from watchlist, returns True if successful"""
        headers = {'X-UT-PHISHING-TOKEN':self.login_manager.FUTWEBPHISHING,
                   'X-UT-SID':self.login_manager.X_UT_SID,
                   'X-HTTP-Method-Override':'DELETE'}
        the_url = self.WATCHLIST_REMOVE_URL % (card.tradeId)
        r = requests.post(the_url,headers = headers)
        return "code" not in dict(r.json())
    def remove_from_tradepile(self,card):
        """Removes card from tradepile, returns True if successful"""
        headers = {'X-UT-PHISHING-TOKEN':self.login_manager.FUTWEBPHISHING,
                   'X-UT-SID':self.login_manager.X_UT_SID,
                   'X-HTTP-Method-Override':'DELETE'}
        the_url = self.TRADEPILE_REMOVE_URL % (card.tradeId)
        r = requests.post(self.WATCHLIST_URL,headers = headers)
        return "code" not in dict(r.json())

