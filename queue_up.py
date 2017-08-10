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
GROUPME_NO_MESSAGE_STATUS_CODE = 304

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


def get_messages_before(groupme_message_id):
    '''Gets 100 messages that occurred immediately before the given id
    This will return an empty list if no messages exist before
    '''
    limit = 100
    url = '{}/groups/{}/messages'.format(GROUPME_URL, GROUP_ID)
    res = requests.get(url, headers=HEADERS, params={'limit': limit, 'before_id': groupme_message_id})

    if res.status_code == GROUPME_NO_MESSAGE_STATUS_CODE:
        logging.info('no more messages before {}'.format(groupme_message_id))
        return []

    res.raise_for_status()

    return res.json()['response']['messages']


def get_all_messages_iter():
    '''Gets all messages in descending order of date created
    '''
    # Get most recent message becuase it's ID is needed to paginate backwards in time
    most_recent_message = get_messages(1)[0]
    yield most_recent_message

    oldest_message_id = most_recent_message['id']
    messages = get_messages_before(oldest_message_id)

    while messages:
        logger.info('found {} messages, from {} to {}'.format(len(messages), arrow.get(messages[1]['created_at']), arrow.get(messages[-1]['created_at'])))
        for message in messages:
            yield message

        oldest_message_id = messages[-1]
        messages = get_messages_before(oldest_message_id)

    logger.info('finished fetching all messages')


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


def get_all_multi_media_messages():
    total_count = 0

    for message in get_all_messages_iter():
        # only interested in messages with a picture or video
        if message['attachments']:
            event_obj = create_event_from_groupme_message(message)
            total_count += 1

        # TODO: save events in chunks of 100

    logger.info('finished saving {} events')


if __name__ == '__main__':
    main()
