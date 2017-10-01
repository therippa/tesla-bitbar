#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# <bitbar.title>Tesla BitBar</bitbar.title>
# <bitbar.version>v1.0</bitbar.version>
# <bitbar.author>therippa@gmail.com</bitbar.author>
# <bitbar.author.github>therippa</bitbar.author.github>
# <bitbar.desc>Control your Tesla from the menubar</bitbar.desc>
# <bitbar.image>https://i.imgur.com/XbwiemY.png</bitbar.image>
# <bitbar.dependencies>python</bitbar.dependencies>
# <bitbar.abouturl>https://github.com/therippa/tesla-bitbar</bitbar.abouturl>
#
# by therippa@gmail.com

try: # Python 3
    from urllib.parse import urlencode
    from urllib.request import Request, urlopen, build_opener
    from urllib.request import ProxyHandler, HTTPBasicAuthHandler, HTTPHandler
    from urllib.request import HTTPError # <- is this right???
except: # Python 2
    from urllib import urlencode
    from urllib2 import Request, urlopen, build_opener
    from urllib2 import ProxyHandler, HTTPBasicAuthHandler, HTTPHandler
    from urllib2 import HTTPError
import json
import sys, os
import datetime
import calendar
import base64
import keyring
import time
from pprint import pprint

TEMP_UNIT='F' # 'F' or whatever else, it'll end up 'C'

VEHICLES = { 
    # map vehicle ID numbers to real names
    #'012345': 'Example Vehicle Name',
}

# ----------------------------------
# Thank you to Greg Glockner for the code below - https://github.com/gglockner/teslajson
# ----------------------------------

class Connection(object):
    """Connection to Tesla Motors API"""
    def __init__(self,
            email='',
            password='',
            access_token='',
            proxy_url = '',
            proxy_user = '',
            proxy_password = ''):
        """Initialize connection object
        
        Sets the vehicles field, a list of Vehicle objects
        associated with your account
        Required parameters:
        email: your login for teslamotors.com
        password: your password for teslamotors.com
        
        Optional parameters:
        access_token: API access token
        proxy_url: URL for proxy server
        proxy_user: username for proxy server
        proxy_password: password for proxy server
        """
        self.proxy_url = proxy_url
        self.proxy_user = proxy_user
        self.proxy_password = proxy_password
        tesla_client = {
            'v1': {
                'id': 'e4a9949fcfa04068f59abb5a658f2bac0a3428e4652315490b659d5ab3f35a9e', 
                'secret': 'c75f14bbadc8bee3a7594412c31416f8300256d7668ea7e6e7f06727bfb9d220', 
                'baseurl': 'https://owner-api.teslamotors.com', 
                'api': '/api/1/'
            }
        }
        current_client = tesla_client['v1']
        self.baseurl = current_client['baseurl']
        self.api = current_client['api']
        self.access_token = None
        self.expiration = 0
        if access_token:
            self.__sethead(access_token)
        else:
            self.oauth = {
                "grant_type" : "password",
                "client_id" : current_client['id'],
                "client_secret" : current_client['secret'],
                "email" : email,
                "password" : password }

        # This is now a vechicles() function
        #self.vehicles = [Vehicle(v, self) for v in self.get('vehicles')['response']]
   
    def vehicles(self):
        return [Vehicle(v, self) for v in self.get('vehicles')['response']]

    def get_token(self):
        if self.access_token and self.expiration < time.time():
            return self.access_token

        try:
            auth = self.__open("/oauth/token", data=self.oauth)
        except HTTPError as e:
            # Typically, this means non 200 response code
            return None

        if 'access_token' in auth and auth['access_token']:
            self.access_token = auth['access_token']
            self.expiration = int(time.time()) + auth['expires_in'] - 86400
            return self.access_token

        return None


    def get(self, command):
        """Utility command to get data from API"""
        return self.post(command, None)
    
    def post(self, command, data={}):
        """Utility command to post data to API"""
        now = time.time()
        if now > self.expiration:
            auth = self.__open("/oauth/token", data=self.oauth)
            self.__sethead(auth['access_token'],
                           auth['created_at'] + auth['expires_in'] - 86400)
        return self.__open("%s%s" % (self.api, command), headers=self.head, data=data)
    
    def __sethead(self, access_token, expiration=float('inf')):
        """Set HTTP header"""
        self.access_token = access_token
        self.expiration = expiration
        self.head = {"Authorization": "Bearer %s" % access_token}
    
    def __open(self, url, headers={}, data=None, baseurl=""):
        """Raw urlopen command"""
        if not baseurl:
            baseurl = self.baseurl
        req = Request("%s%s" % (baseurl, url), headers=headers)
        try:
            req.data = urlencode(data).encode('utf-8') # Python 3
        except:
            try:
                req.add_data(urlencode(data)) # Python 2
            except:
                pass

        # Proxy support
        if self.proxy_url:
            if self.proxy_user:
                proxy = ProxyHandler({'https': 'https://%s:%s@%s' % (self.proxy_user,
                                                                     self.proxy_password,
                                                                     self.proxy_url)})
                auth = HTTPBasicAuthHandler()
                opener = build_opener(proxy, auth, HTTPHandler)
            else:
                handler = ProxyHandler({'https': self.proxy_url})
                opener = build_opener(handler)
        else:
            opener = build_opener()
        resp = opener.open(req)
        charset = resp.info().get('charset', 'utf-8')
        return json.loads(resp.read().decode(charset))
        

class Vehicle(dict):
    """Vehicle class, subclassed from dictionary.
    
    There are 3 primary methods: wake_up, data_request and command.
    data_request and command both require a name to specify the data
    or command, respectively. These names can be found in the
    Tesla JSON API."""
    def __init__(self, data, connection):
        """Initialize vehicle class
        
        Called automatically by the Connection class
        """
        super(Vehicle, self).__init__(data)
        self.connection = connection
    
    def data_request(self, name):
        """Get vehicle data"""
        result = self.get('data_request/%s' % name)
        return result['response']
    
    def wake_up(self):
        """Wake the vehicle"""
        return self.post('wake_up')
    
    def command(self, name, data={}):
        """Run the command for the vehicle"""
        return self.post('command/%s' % name, data)
    
    def get(self, command):
        """Utility command to get data from API"""
        return self.connection.get('vehicles/%i/%s' % (self['id'], command))
    
    def post(self, command, data={}):
        """Utility command to post data to API"""
        return self.connection.post('vehicles/%i/%s' % (self['id'], command), data)

def get_name(id):
    # check name mapping array for humanized vehicle names
    if id in VEHICLES:
        return VEHICLES[id]
    else:
        return id

def convert_temp(temp):
    if TEMP_UNIT == 'F':
        return (temp * 1.8) + 32
    else:
        return temp

def prompt_login():
    for attempt in range(3):
        sys.stdout.write("\ntesla.com username (will not be saved): ")
        username = sys.stdin.readline()

        sys.stdout.write("tesla.com password (will not be saved): ")
        os.system("stty -echo")  # Don't echo typed characters to terminal
        password = sys.stdin.readline()
        os.system("stty echo")   # Echo characters to terminal, as normal

        sys.stdout.write("\nChecking...")
        sys.stdout.flush()

        c = Connection(username, password)
        access_token = c.get_token()

        if not access_token:
            print ("Access denied")
            time.sleep(0.5)
            continue

        tesla_access_token=keyring.set_password('tesla-bitbar', 'access-token', access_token)
        print ('Success!')
        print ("\nType \"exit\" and hit enter to close this window")
        return

    print ("Sorry, double check your username and password then try again")
    print ("\nType \"exit\" and hit enter to close this window")


def abort_credentials():
    print ('Click to login | refresh=true terminal=true bash="%s" param1=login' % (sys.argv[0]))

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "login":
        prompt_login()
        return

    # print menu - below is icon.png encoded as base64
    print ('|image=iVBORw0KGgoAAAANSUhEUgAAABYAAAAWCAYAAADEtGw7AAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAA/xpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tldCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUuMy1jMDExIDY2LjE0NTY2MSwgMjAxMi8wMi8wNi0xNDo1NjoyNyAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wTU09Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9tbS8iIHhtbG5zOnN0UmVmPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvc1R5cGUvUmVzb3VyY2VSZWYjIiB4bWxuczp4bXA9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC8iIHhtbG5zOmRjPSJodHRwOi8vcHVybC5vcmcvZGMvZWxlbWVudHMvMS4xLyIgeG1wTU06T3JpZ2luYWxEb2N1bWVudElEPSJ1dWlkOjI3MzY3NDg0MTg2QkRGMTE5NjZBQjM5RDc2MkZFOTlGIiB4bXBNTTpEb2N1bWVudElEPSJ4bXAuZGlkOkI2QzU0RTM0OURFMDExRTdBNEU0QTExMzAxRjlCQkE1IiB4bXBNTTpJbnN0YW5jZUlEPSJ4bXAuaWlkOkI2QzU0RTMzOURFMDExRTdBNEU0QTExMzAxRjlCQkE1IiB4bXA6Q3JlYXRvclRvb2w9IkFkb2JlIElsbHVzdHJhdG9yIENDIDIwMTUgKE1hY2ludG9zaCkiPiA8eG1wTU06RGVyaXZlZEZyb20gc3RSZWY6aW5zdGFuY2VJRD0ieG1wLmlpZDo2MWU4Yzc5OS1kOTYyLTRjYmUtYWI0Mi1jYWZiOWY5NjFjZWUiIHN0UmVmOmRvY3VtZW50SUQ9InhtcC5kaWQ6NjFlOGM3OTktZDk2Mi00Y2JlLWFiNDItY2FmYjlmOTYxY2VlIi8+IDxkYzp0aXRsZT4gPHJkZjpBbHQ+IDxyZGY6bGkgeG1sOmxhbmc9IngtZGVmYXVsdCI+dGVzbGFfVF9CVzwvcmRmOmxpPiA8L3JkZjpBbHQ+IDwvZGM6dGl0bGU+IDwvcmRmOkRlc2NyaXB0aW9uPiA8L3JkZjpSREY+IDwveDp4bXBtZXRhPiA8P3hwYWNrZXQgZW5kPSJyIj8+ux4+7QAAALlJREFUeNpi/P//PwMtABMDjcDQM5gFmyAjI2MAkLIHYgMgdsCh9wAQXwDig8B42oAhC4o8ZAwE74H4PpQ+D6XXA7EAFK9HkwOrxTAHi8ENUA3/0fB6KEYXB6ltIMZgkKv6oS4xgIqhGAYVM4CqmQ/SQ9BgbBjqbZjB54nRQ2yqeICDTXFyu4iDTbHBB3CwKTaY5KBgJLYQAmaa/9B0z0h2ziMiOKhq8AVaGfxwULiYcbQGobnBAAEGADCCwy7PWQ+qAAAAAElFTkSuQmCC')
    print ('---')

    tesla_access_token=keyring.get_password('tesla-bitbar', 'access-token')
    if not tesla_access_token:
        abort_credentials()
        return

    # create connection to tesla account
    c = Connection(access_token = tesla_access_token)

    try:
        vehicles = c.vehicles()
    except HTTPError as e:
        if e.code == 401:
            abort_credentials()
            return
        raise

    # see if args are passed, if so, pass commands and bail
    if len(sys.argv) > 1:
        v = vehicles[int(sys.argv[1])]
        v.wake_up()
        if sys.argv[2] != "wakeup":
            v.command(sys.argv[2])
        return

    # only do submenu if multiple vehicles
    prefix = ''
    if len(vehicles) > 1:
        prefix = '--'

    # loop through vehicles, print menu with relevant info       
    for i, vehicle in enumerate(vehicles):
        if prefix:
            print get_name(vehicle['display_name'])

        if vehicle['state'] != "online":
            print ('%sState: %s| color=black' %  (prefix, vehicle['state']))
            print ('%sWakeup | refresh=true terminal=false bash="%s" param1=%s param2=wakeup' % (prefix, sys.argv[0], str(i)))
            print ('%sStart HVAC | refresh=true terminal=false bash="%s" param1=%s param2=auto_conditioning_start' % (prefix, sys.argv[0], str(i)))
        else:
            charge_state = vehicle.data_request('charge_state')
            climate_state = vehicle.data_request('climate_state')
            print ('%sBattery Level: %s%%| color=black' % (prefix, str(charge_state['battery_level'])))
            print ('%sCharging State: %s| color=black' % (prefix, charge_state['charging_state']))
            print ('%s---' % prefix)
            try:
                print ('%sInside Temp: %.1f°| color=black' % (prefix, convert_temp(climate_state['inside_temp'])))
            except:
                print ('%sInside Temp: Unavailable' % prefix)
            try:
                print ('%sOutside Temp: %.1f°| color=black' % (prefix, convert_temp(climate_state['outside_temp'])))
            except:
                print ('%sOutside Temp: Unavailable' % prefix)

            if climate_state['is_climate_on']:
                print ('%sStop HVAC | refresh=true terminal=false bash="%s" param1=%s param2=auto_conditioning_stop' % (prefix, sys.argv[0], str(i)))
            else:
                print ('%sStart HVAC | refresh=true terminal=false bash="%s" param1=%s param2=auto_conditioning_start' % (prefix, sys.argv[0], str(i)))


if __name__ == '__main__':
    main()
