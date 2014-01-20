# Open Source Python client for Chrome Google Cloud Messaging (GCM)
#
# Author: Chirag
# Email: b.like.no.other@gmail.com

import unittest
from chromegcmclient import ChromeGCM
from chromegcmclient import ChromeGcmBadRequestError
from chromegcmclient import PlainTextMessage
from chromegcmclient import JSONMessage
from chromegcmclient import ChromeGcmAuthenticationError


class ChromeGCMClientTest(unittest.TestCase):

    def setUp(self):
        self.auth_info = {
                'client_id': 'PASTE_CLIENT_ID_HERE',
                'client_secret': 'PASTE_CLIENT_SECRET_HERE',
                'refresh_token': 'PASTE_REFRESH_TOKEN_HERE',
                'grant_type': 'refresh_token'
            }
        self.access_token = 'PASTE_ACCESS_TOKEN_HERE'

        self.text_message = 'this is plain text message'
        self.json_message = {'title': 'this is title', 'body': 'this is body'}

        self.valid_channel_ids = ['PASTE_CHROME_CHANNEL_ID_HERE']
        self.invalid_channel_ids = ['THIS_IS_INVALID_CHANNEL_ID']
        self.channel_ids = self.valid_channel_ids + self.invalid_channel_ids

        self.options = {'message_lenght': 50}

    def test_auth(self):
        # should raise error when auth_info type is not in [str, dict]
        self.assertRaises(ValueError, ChromeGCM, 123)

        # should raise error when auth_info type data is invalid
        auth_info = self.auth_info.copy()
        auth_info.pop('refresh_token', None)
        self.assertRaises(ChromeGcmBadRequestError, ChromeGCM, auth_info)

        # should raise error when auth_info correct but access token not found
        cgcm = ChromeGCM(self.auth_info)
        self.assertIsInstance(cgcm.access_token, basestring)

        # should raise error when auth_info correct but expires_in not found
        self.assertIsInstance(cgcm.token_expires_in, long)

    def test_send(self):
        # should raise error when options is not dict
        self.assertRaises(ValueError, PlainTextMessage,
                          message='msg', channel_ids=[], options='not_dict')

        # message objects
        tmsg = PlainTextMessage(self.text_message, self.channel_ids,
                                self.options)
        jmsg = JSONMessage(self.json_message, self.channel_ids)

        # should raise error when access_token is invalid
        access_token = '123'
        cgcm = ChromeGCM(access_token)
        self.assertRaises(ChromeGcmAuthenticationError, cgcm.send, tmsg)
        self.assertRaises(ChromeGcmAuthenticationError, cgcm.send, jmsg)

        # get valid access_token
        cgcm = ChromeGCM(self.auth_info)

        # should raise error when send method has argument
        # which is not Message object
        self.assertRaises(ValueError, cgcm.send, 'not message object')

        # should raise error when message could not sent to valid channel id
        result = cgcm.send(tmsg)
        self.assertEqual(self.valid_channel_ids, result.success,
                         'Could not send PlainTextMessage to valid channel id')
        result = cgcm.send(jmsg)
        self.assertEqual(self.valid_channel_ids, result.success,
                         'Could not send JSONMessage to valid channel id')

        # should raise error when message sent to invalid channel id
        result = cgcm.send(tmsg)
        self.assertEqual(self.invalid_channel_ids, result.failed,
                         'PlainTextMessage sent to invalid channel id')
        result = cgcm.send(jmsg)
        self.assertEqual(self.invalid_channel_ids, result.failed,
                        'JSONMessage sent to invalid channel id')


if __name__ == '__main__':
    unittest.main()
