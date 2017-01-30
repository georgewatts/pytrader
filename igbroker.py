import json
import requests

"""
An interface for interacting with the IG trading platform

"""
class IGBroker(object):

    # Connection to IG API
    valid = 0

    # Endpoints TODO Tidy up
    base_point = 'https://demo-api.ig.com/gateway/deal/'
    login      = base_point + 'session/'
    markets    = base_point + 'markets/'
    market_nav = base_point + 'marketnavigation/'

    # Header data for API requests
    headers = {
                'Accept': 'application/json; charset=UTF-8',
                'Content-Type': 'application/json; charset=UTF-8',
                'X-IG-API-KEY': '4be4623e3ec7897f94549aff7b44d18202fa6e22',
                'VERSION': 2
              }

    # Body data for API session creation
    body    = {
                'identifier': '',
                'password': '',
              }

    # Login account information
    account = None

    def __init__(self, username, password):
        self.body['identifier'] = username
        self.body['password']   = password

        response = requests.post(self.login, headers=self.headers, json=self.body)

        self.valid = (response.status_code == 200)

        if self.valid:
            self.headers.update({
                                'CST' : response.headers['CST'],
                                'X-SECURITY-TOKEN' : response.headers['X-SECURITY-TOKEN'],
                                })
            self.account = self.__json_decode(response.text)
        else:
            self.account = self.__json_decode(response.text)
            print self.account
        #TODO Add error checking for incorrect login

    def __json_decode(self, text):
        return json.loads(text)

    def __debug_json(self, json_object):
        print "JSON DEBUG: " + json.dumps(json_object, sort_keys=True, indent=2, separators=(',', ': '))

    def __get_request(self, URL):
        self.headers['method_'] = 'null'
        json_text = (requests.get(URL, headers=self.headers)).text
        return self.__json_decode(json_text)

    def __post_request(self, URL, json):
        self.headers['method_'] = 'null'
        json_text = (requests.post(URL, headers=self.headers, json=json)).text
        return self.__json_decode(json_text)

    def __delete_request(self, URL, json):
        self.headers['method_'] = 'DELETE'
        json_text = (requests.post(URL, headers=self.headers, json=json)).text
        return self.__json_decode(json_text)

    def get_account_details(self):
        return self.account

    def get_lightstream_details(self):
        params = {
                    'lightstreamerEndpoint': self.account['lightstreamerEndpoint'],
                    'clientId': self.account['clientId'],
                    'password': 'CST-%s|XST-%s' % (self.headers['CST'], self.headers['X-SECURITY-TOKEN'])
                 }
        return params

    def get_market_details(self, epic):
        market = self.markets + epic
        return self.__get_request(market)

    def browse_markets(self, node_id=0):
        if not node_id:
            return self.__get_request(self.market_nav)
        else:
            node = self.market_nav + node_id
            return self.__get_request(node)

    def create_open_position(self, currency_code, direction, epic, expiry, force_open, guaranteed_stop,
                             level, limit_distance, limit_level, order_type, quote_id, size,
                             stop_distance, stop_level):
        params = {
                    'currencyCode': currency_code,
                    'direction': direction,
                    'epic': epic,
                    'expiry': expiry,
                    'forceOpen': force_open,
                    'guaranteedStop': guaranteed_stop,
                    'level': level,
                    'limitDistance': limit_distance,
                    'limitLevel': limit_level,
                    'orderType': order_type,
                    'quoteId': quote_id,
                    'size': size,
                    'stopDistance': stop_distance,
                    'stopLevel': stop_level
                 }
