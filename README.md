# chrome-gcm-client
Python client for [Chrome Google Cloud Messaging (GCM)](http://developer.chrome.com/apps/cloudMessaging.html).

## Requirements
*   [requests](http://docs.python-requests.org/) - HTTP request, handles proxies etc.
*   [omnijson](https://pypi.python.org/pypi/omnijson/) if you use Python 2.5 or older.

## Installation
Install via pip

    sudo pip install -e git@github.com:blikenoother/chrome-gcm-client.git@master
    
or download source code and install via setup.py

    sudo python setup.py install

## Usage
```python    
from chromegcmclient import PlainTextMessage
from chromegcmclient import JSONMessage
from chromegcmclient import ChromeGCM
from chromegcmclient import ChromeGcmAuthenticationError
from chromegcmclient import ChromeGcmBadRequestError
from chromegcmclient import ChromeGcmUnexpectedError


# your app info and authorized token
auth_info = {
        'client_id': '<app client id>',
        'client_secret': '<app secret>',
        'refresh_token': '<authorisez refresh token>',
        'grant_type': 'refresh_token'
    }

# chrome channel_ids to send message
channel_ids = ['channel_id_1', 'channel_id_2', 'channel_id_3']

# plain text message object
plain_text_msg = PlainTextMessage('test message', channel_ids)

# json message object
json_msg = JSONMessage({'title': 'this is title', 'body':'this is body'}, channel_ids)

try:
    # init with auth detail
    cgcm = ChromeGCM(auth_info)
    
    # send plain text message
    result = cgcm.send(plain_text_msg)
    
    # you can use access_token to send further messages till token expires
    access_token = cgcm.access_token
    token_expires_in = cgcm.token_expires_in
    
    # init with access_token
    cgcm = ChromeGCM(access_token)
    
    # send json message
    result = cgcm.send(json_msg)
    
    # get list of channel_ids which received message
    success_channel_ids = result.success
    
    # get list of channel_ids which could not received message
    failed_channel_ids = result.failed

except ValueError, e:
    print "Invalid message or options"
    print e.args[0]

except ChromeGcmAuthenticationError, e:
    print "Invalid auth_info/access_token"
    print e.args[0]
    
except ChromeGcmBadRequestError, e:
    print "Invalid or unexpected response from GCM"
    print e.args[0]
    
except ChromeGcmUnexpectedError, e:
    print "Some unknown error occurred"
    print e.args[0]

```

As per google constraints, maximum message length should be 256 bytes. But when we tested, message was unable to send when message length is more than 130 char. So by default message will be truncated to 130 char. You can over write message length argument in `options` as well.
```python
# chrome channel_ids to send message
channel_ids = ['channel_id_1', 'channel_id_2', 'channel_id_3']
options = {'message_lenght': 50}

plain_text_msg = PlainTextMessage('test message', channel_ids, options)

```

Chirag (blikenoother -[at]- gmail [dot] com)