# Open Source Python client for Chrome Google Cloud Messaging (GCM)
#
# Author: Chirag
# Email: b.like.no.other@gmail.com

import requests

try:
    import json
except ImportError:
    import omnijson as json

# required class
__all__ = ('ChromeGcmAuthenticationError', 'ChromeGcmBadRequestError',
           'ChromeGcmUnexpectedError', 'JSONMessage', 'PlainTextMessage',
           'ChromeGCM', 'Result')

# More info: http://developer.chrome.com/apps/cloudMessaging.html
#: Default URL to GCM service.
GCM_URL = 'https://www.googleapis.com/gcm_for_chrome/v1/messages'

#: Default URL to Google oauth2 token
REFRESH_TOKEN_URL = 'https://accounts.google.com/o/oauth2/token'


class ChromeGcmAuthenticationError(Exception):
    """ Raised if your Google API key is rejected. """
    pass


class ChromeGcmBadRequestError(Exception):
    """ Raised if value passed in request are wrong. """
    pass


class ChromeGcmUnexpectedError(Exception):
    """ Raised if any unknown exception occurred. """
    pass


class Message(object):
    """ Base message class. """

    # recognized options
    __options = {
        'subchannel_id': 0,
        'message_lenght': 130
    }

    def __init__(self, message, channel_ids, options={}):
        """ Abstract message.

            :Arguments:
                - `message` (str or dict): payload of this message.
                - `channel_ids` (lists): chrome channel id's to send message.
                - `options` (dict): optional
                    - `subchannel_id` (int): default is 0.
                    - `message_lenght` (int): truncate message if length exceeds payload size limit, default is 130 char.

            Refer to `Send message <http://developer.chrome.com/apps/cloudMessaging.html#message>`_
            for more explanation on available options.
        """
        self._message = message
        self.__channel_ids = channel_ids

        if not isinstance(options, dict):
            raise ValueError('Invalid options type. Please refer docstring.')

        self.__options = dict(self.__options.items() + options.items())

    def _prepare_payload(self):
        """ Hook to format message data payload. """
        return self._message

    @property
    def channel_ids(self):
        """ Target channel id's. """
        return self.__channel_ids

    @property
    def options(self):
        """ Options (known keys: subchannel_id, message_lenght). """
        return self.__options


class PlainTextMessage(Message):
    """ Plain-text unicast message. """
    pass


class JSONMessage(Message):
    """ JSON formatted message. """

    def _prepare_payload(self):
        """ Serializes message to JSON. """
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
        """ Create new connection if auth_info is dict.

            :Arguments:
                - auth_info (str or dict): google oauth2 access_token in string or google app credentials in dict to generate access_token ``{'client_id': '', 'client_secret': '', 'refresh_token': '', 'grant_type': 'refresh_token'}``.

            Refer to `Get refresh token <http://developer.chrome.com/apps/cloudMessaging.html#refresh>`_
            for more explanation on available options.

            :Raises:
                - ``ValueError`` if auth_info is not basestring or dict.
                - ``requests.exceptions.RequestException`` on any network problem.
                - :class:`ChromeGcmBadRequestError` auth_info is invalid.
                - :class:`ChromeGcmUnexpectedError` unknown exception occurred with explanation.
        """
        if isinstance(auth_info, basestring):
            self.access_token = auth_info

        elif isinstance(auth_info, dict):
            self._renew_access_token(auth_info)

        else:
            raise ValueError('Invalid auth_info type. Please refer docstring.')

    def send(self, message):
        """ Send message.

            :Arguments:
                `message` (:class:`Message`): plain text or JSON message.

            :Returns:
                :class:`Result` interpreting the results.

            :Raises:
                - ``ValueError`` if message is not :class:`Message` object.
                - ``requests.exceptions.RequestException`` on any network problem.
                - :class:`ChromeGcmAuthenticationError` access_token is invalid.
        """

        if not isinstance(message, Message):
            raise ValueError('Invalid message object.')

        headers = {
                'Authorization': 'Bearer %s' % self.access_token,
                'Content-Type': 'application/json'
            }

        payload = message._prepare_payload()
        payload = payload[:message.options.get('message_lenght')]
        subchannel_id = message.options.get('subchannel_id')

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
