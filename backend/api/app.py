import json
import requests
import sys
import time

from datetime import datetime
from flask import Flask, render_template, Response
from flask_cors import CORS, cross_origin
from flask_restful import Resource, Api
from sseclient import SSEClient


app = Flask(__name__)
api = Api(app)

REAL_TIME_PRICE_URL = "https://financialmodelingprep.com/api/v3/stock/real-time-price/"
quote_dict = dict()


class Quote(Resource):
    ''' Provide APIs for stock quote and magic index with the quotes'''
    
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
        
        # result = [quote_dict, {"%d(SPY)/%d(TVIX)"%(spy, tvix): round(spy/tvix,2)}]
        quote_dict.update({"%d(SPY)/%d(TVIX)"%(spy, tvix): round(spy/tvix,2)})

        return quote_dict

api.add_resource(Quote, '/quote/<string:symbol>')


def event_stream():
    ''' Push event stream implementation '''

    stream_url = ('https://cloud-sse.iexapis.com/stable/stocksUSNoUTP?'
           'token=sk_e0913d6674b74556b0b0263369814ecb&symbols=spy')
    messages = SSEClient(stream_url)
    current_time_str = datetime.now().strftime("%H:%M:%S")
    count = quote_count = current_price = 0 

    for msg in messages:
        event = json.loads(msg.data.replace("[", "").replace("]", ""))

        latest_update_unix = event["latestUpdate"][0:-3]
        latest_update_obj = datetime.fromtimestamp(latest_update_unix)
        latest_update_str = latest_update_obj.strftime("%H:%M:%S")

        latest_price = float(event['latestPrice'])
         
        if current_time_str == latest_update_str and current_price != latest_price:
            quote_count = quote_count + 1
        elif current_time_str == latest_update_str:
            count = count + 1
        else:  
            yield "%d : %d at %s\n" % (count, quote_count, latest_update_str)
            count = quote_count = 0
            current_time_str = latest_update_str
            current_price = latest_price


def test_stream():
    ''' Proof of concept for event stream function '''

    url = 'https://stream.wikimedia.org/v2/stream/recentchange'
    for event in SSEClient(url):
        d = event.data
        print(d["meta"])
        if event.event == 'message':
            try:
                # event.data["secret": "Yoon"]
                change = json.loads(event.data)
            except ValueError:
                pass
            else:
                # print('{user} edited {title}'.format(**change))
                # yield '{user} edited {title}\n'.format(**change)
                yield str(event)


@app.route('/stream')
@cross_origin()
def stream():
    ''' Event stream API '''

    # return Response(event_stream(), mimetype="text/event-stream")
    return Response(event_stream(), mimetype="text/event-stream")


@app.route('/')
def index():
    return 'Hello, World!'


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', threaded=True)
