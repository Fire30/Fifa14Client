class Card(object):
    def __init__(self,card_dict):
        """Object that gets dict from a Card Object
        and sets each key as an atrribute
        """
        self.card_dict = card_dict
        for key in card_dict:
            setattr(self, key, card_dict[key])
        try:
            for key in self.itemData:
               setattr(self, key, self.itemData[key])
        except:
            pass
    def __repr__(self):
        return str(self.card_dict)
