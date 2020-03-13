import requests

from flask import Flask
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

REAL_TIME_PRICE_URL = "https://financialmodelingprep.com/api/v3/stock/real-time-price/"
quote_dict = dict()

class Quote(Resource):
    
    def get(self, symbol):
        if symbol == 'magic':
            return self.get_magic_index()
        else:
            return self.get_stock_price(symbol)
    

    def get_stock_price(self, symbol):
        ''' Call realtime stock price API'''

        r = requests.get(REAL_TIME_PRICE_URL+symbol)

        return r.json()


    def get_magic_index(self):
        ''' Calculate an index with SPY and TVIX '''

        quotes = self.get_stock_price('spy,tvix')["companiesPriceList"]

        for quote in quotes:
            quote_dict[quote['symbol']] = quote['price']
 
        spy = float(quote_dict['spy'.upper()])
        tvix = float(quote_dict['tvix'.upper()])

        return {"%d(SPY)/%d(TVIX)"%(spy, tvix): round(spy/tvix,2)} 


api.add_resource(Quote, '/<string:symbol>')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
