# Open Source Python client for Chrome Google Cloud Messaging (GCM)
#
# Author: Chirag
# Email: b.like.no.other@gmail.com

import requests

try:
    import json
except ImportError:
    import omnijson as json

# all you need
__all__ = ('ChromeGcmAuthenticationError', 'ChromeGcmBadRequestError',
           'ChromeGcmUnexpectedError', 'JSONMessage', 'PlainTextMessage',
           'ChromeGCM', 'Result')

# More info: http://developer.chrome.com/apps/cloudMessaging.html
#: Default URL to GCM service.
GCM_URL = 'https://www.googleapis.com/gcm_for_chrome/v1/messages'

#: Default URL to GCM service.
REFRESH_TOKEN_URL = 'https://accounts.google.com/o/oauth2/token'


class ChromeGcmAuthenticationError(Exception):
    """ Raised if your Google API key is rejected. """
    pass


class ChromeGcmBadRequestError(Exception):
    """ Raised if value passed in request are wrong. """
    pass


class ChromeGcmUnexpectedError(Exception):
    """ Raised if unknown exception occurred. """
    pass


class Message(object):
    """ Base message class. """

    def __init__(self, message, channel_ids, subchannel_id=0):
        self._message = message
        self.__channel_ids = channel_ids
        self.__subchannel_id = subchannel_id

    def _prepare_payload(self):
        return self._message

    @property
    def channel_ids(self):
        return self.__channel_ids

    @property
    def subchannel_id(self):
        return self.__subchannel_id


class PlainTextMessage(Message):
    """ Plain-text unicast message. """
    pass


class JSONMessage(Message):
    """ JSON formatted message. """

    def _prepare_payload(self):
        return json.dumps(self._message)


class Result(object):
    """ Result of send operation. """

    def __init__(self, success, failed):
        self.__success = success
        self.__failed = failed

    @property
    def success(self):
        """ Successfully processed channel ID's ``[channel_id]``. """
        return self.__success

    @property
    def failed(self):
        """ Failed channel ID's ``[channel_id]``. """
        return self.__failed


class ChromeGCM(object):
    """ GCM client. """

    access_token = None
    token_expires_in = None

    def __init__(self, auth_info):

        if isinstance(auth_info, basestring):
            self.access_token = auth_info

        elif isinstance(auth_info, dict):
            self._renew_access_token(auth_info)

        else:
            raise ValueError('Invalid auth_info type. Please refer docstring.')

    def send(self, message):
        """ Send message. """

        if not isinstance(message, Message):
            raise ValueError('Invalid message object.')

        headers = {
                'Authorization': 'Bearer %s' % self.access_token,
                'Content-Type': 'application/json'
            }

        payload = message._prepare_payload()
        subchannel_id = message.subchannel_id

        # send notification
        success = []
        failed = []
        for channel_id in message.channel_ids:
            data = {
                    'channelId': channel_id,
                    'payload': payload,
                    'subchannelId': subchannel_id
                }
            data = json.dumps(data)
            headers['Content-Length'] = len(data)
            response = requests.post(GCM_URL, data=data, headers=headers)

            if response.status_code == 204:
                success.append(channel_id)

            elif response.status_code == 401:
                raise ChromeGcmAuthenticationError('Invalid Credentials.')

            else:
                failed.append(channel_id)

        return Result(success, failed)

    def _renew_access_token(self, auth_info):
        response = requests.post(REFRESH_TOKEN_URL, data=auth_info)

        if response.status_code != 200:
            raise ChromeGcmBadRequestError('Invalid auth info.'\
                                           ' Please refer docstring')
        try:
            content = json.loads(response.text)
            self.access_token = content.get('access_token')
            self.token_expires_in = long(content.get('expires_in'))
        except Exception, e:
            raise ChromeGcmUnexpectedError(e)
