import logging
import sys

import arrow
import requests

GROUPME_NO_MESSAGE_STATUS_CODE = 304

# logging setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

stdoutput = logging.StreamHandler(sys.stdout)
stdoutput.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.addHandler(stdoutput)


class GroupMeAPI():
    headers = {
        'X-Access-Token': None
    }

    #
    def __init__(self, base_url, group_id, group_name, access_token):
        self.base_url = base_url
        self.group_id = group_id
        self.group_name = group_name
        self.headers['X-Access-Token'] = access_token

    @classmethod
    def groupme_message_has_image_or_video(cls, message):
        attachments = message['attachments']
        for attach in attachments:
            if attach['type'] == 'image' or attach['type'] == 'video':
                return True

        return False

    @classmethod
    def get_first_image_or_video_attachment_from_groupme_message(cls, message):
        attachments = message['attachments']
        for attach in attachments:
            if attach['type'] == 'image' or attach['type'] == 'video':
                return attach

        raise Exception('No image or Video Attchment: {}'.format(message))

    def get_groups(self):
        url = '{}/groups'.format(self.base_url)
        res = requests.get(url, headers=self.headers)
        res.raise_for_status()

        return res.json()['response']

    def verfify_group_exists(self):
        groups = self.get_groups()

        for group in groups:
            if group['group_id'] == self.group_id and group['name'] == self.group_name:
                logger.info('found group {} with {} messages'.format(self.group_name, group['messages']['count']))
                return True

        raise Exception('working with invalid group {}'.format(groups))

    def get_all_multi_media_messages_iter(self):
        '''Get only those messages that contain a picure or video
        '''
        for message in self._get_all_messages_iter():
            if self.groupme_message_has_image_or_video(message):
                yield message

    def get_all_multi_media_messages_after_iter(self, message_id):
        '''Get only those messages that contain a picure or video
        '''
        for message in self._get_messages_after(message_id):
            if self.groupme_message_has_image_or_video(message):
                yield message

    def _get_messages(self, limit=100):
        url = '{}/groups/{}/messages'.format(self.base_url, self.group_id)
        res = requests.get(url, headers=self.headers, params={'limit': limit})
        res.raise_for_status()

        return res.json()['response']['messages']

    def _get_all_messages_iter(self):
        '''Gets all messages in descending order of date created
        '''
        # Get most recent message becuase it's ID is needed to paginate backwards in time
        most_recent_message = self._get_messages(1)[0]
        yield most_recent_message

        oldest_message_id = most_recent_message['id']
        messages = self._get_messages_before(oldest_message_id)

        while messages:
            logger.info('found {} messages, from {} to {}'.format(len(messages), arrow.get(messages[1]['created_at']), arrow.get(messages[-1]['created_at'])))
            for message in messages:
                yield message

            oldest_message_id = messages[-1]['id']
            messages = self._get_messages_before(oldest_message_id)

        logger.info('finished fetching all messages')

    def _get_all_messages_after_iter(self, og_message_id):
        '''Gets all messages in descending order of date created
        '''
        oldest_message_id = og_message_id
        messages = self._get_messages_after(oldest_message_id)

        while messages:
            logger.info('found {} messages, from {} to {}'.format(len(messages), arrow.get(messages[1]['created_at']), arrow.get(messages[-1]['created_at'])))
            for message in messages:
                yield message

            oldest_message_id = messages[0]['id']
            messages = self._get_messages_after(oldest_message_id)

        logger.info('finished fetching all messages created after {}'.format(og_message_id))

    def _get_messages_before(self, groupme_message_id):
        '''Gets 100 messages that occurred immediately before the given id
        This will return an empty list if no messages exist before
        '''
        limit = 100
        url = '{}/groups/{}/messages'.format(self.base_url, self.group_id)
        res = requests.get(url, headers=self.headers, params={'limit': limit, 'before_id': groupme_message_id})

        if res.status_code == GROUPME_NO_MESSAGE_STATUS_CODE:
            logging.info('no more messages before {}'.format(groupme_message_id))
            return []

        res.raise_for_status()

        return res.json()['response']['messages']

    def _get_messages_after(self, groupme_message_id):
        '''Gets 100 messages that occurred immediately after the given id
        This will return an empty list if no messages exist after
        '''
        limit = 100
        url = '{}/groups/{}/messages'.format(self.base_url, self.group_id)
        res = requests.get(url, headers=self.headers, params={'limit': limit, 'after_id': groupme_message_id})

        if res.status_code == GROUPME_NO_MESSAGE_STATUS_CODE:
            logging.info('no more messages after {}'.format(groupme_message_id))
            return []

        res.raise_for_status()

        return res.json()['response']['messages']
