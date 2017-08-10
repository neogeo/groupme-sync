import arrow
import logging
import requests
import json


GROUPME_URL = 'https://api.groupme.com/v3'
HEADERS = {
    'X-Access-Token': 'YOUR_TOKEN_HERE'
}
GROUP_NAME = 'YOUR_GROUP_NAME'
GROUP_ID = 'YOUR_GROUP_ID'

logger = logging.getLogger(__name__)


def main():
    assert(verfify_fishy_group_exists())
    get_all_multi_media_messages()


def get_groups():
    url = '{}/groups'.format(GROUPME_URL)
    res = requests.get(url, headers=HEADERS)
    res.raise_for_status()

    return res.json()['response']


def get_messages(limit=100):
    url = '{}/groups/{}/messages'.format(GROUPME_URL, GROUP_ID)
    res = requests.get(url, headers=HEADERS, params={'limit': limit})
    res.raise_for_status()

    return res.json()['response']['messages']


def create_event_from_groupme_message(message):
    # get the first attachment
    media_type, media_url = message['attachments'][0]['type'], message['attachments'][0]['url']
    groupme_id = message['id']
    created_at_ts = message['created_at']
    hearted = True if message['favorited_by'] else False
    caption = message['text']
    backup_link = None

    event_obj = {
        'groupme_id': groupme_id,
        'type': media_type,
        'source_url': media_url,
        'created_at': created_at_ts,
        'hearted': hearted,
        'caption': caption,
        'backup_link': backup_link,
    }
    return event_obj


def verfify_fishy_group_exists():
    groups = get_groups()

    for group in groups:
        if group['group_id'] == GROUP_ID and group['name'] == GROUP_NAME:
            logger.info('found group {} with {} messages'.format(GROUP_NAME, group['messages']['count']))
            return True

    raise Exception('working with invalid group {}'.format(groups))


# TODO: yeild, and paginate all messages, and log
def get_all_multi_media_messages():
    total_count = 0
    limit = 2
    messages = get_messages(limit)

    for message in messages:
        # if the message has a pic or video
        if message['attachments']:
            event_obj = create_event_from_groupme_message(message)
            print(event_obj)
            total_count += 1

    print(total_count)


if __name__ == '__main__':
    main()
