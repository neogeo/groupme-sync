import logging
import sys

import arrow

import config
import event_model
import file_utils
from groupme import GroupMeAPI
from firebase import Firebase

# logging setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

stdoutput = logging.StreamHandler(sys.stdout)
stdoutput.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.addHandler(stdoutput)


def main():
    groupme_api = GroupMeAPI(config.GROUPME_URL, config.GROUP_ID, config.GROUP_NAME, config.GROUPME_ACCESS_TOKEN)
    firebase_db = Firebase(config.FIREBASE_SERVICE_ACCOUNT_PRIVATE_KEY, config.FIREBASE_DATABASE_URL)

    assert(groupme_api.verfify_group_exists())

    # save_all_multi_media_messages(groupme_api, firebase_db)
    # save_since_last_message(groupme_api, firebase_db)
    backup_images_to_s3(firebase_db)


def save_all_multi_media_messages(groupme_api, firebase_db):
    '''Save all messages in GroupMe since the beginning of group start date
    '''
    total_count = 0
    events = []

    for message in groupme_api.get_all_multi_media_messages_iter():
        media_attachment = groupme_api.get_first_image_or_video_attachment_from_groupme_message(message)

        event_obj = event_model.event_from_groupme_message(message, media_attachment)
        events.append(event_obj)

        total_count += 1

        # save events in chunks of 100
        if len(events) % 100 == 0:
            firebase_db.create_from_list(events)
            events = []

    # if there are any events remaining
    if events:
        firebase_db.create_from_list(events)

    logger.info('finished saving all {} events'.format(total_count))


def save_since_last_message(groupme_api, firebase_db):
    '''Save all messages in GroupMe group since the last saved message
    '''
    # get last saved messege in firebase
    latest_event = firebase_db.get_most_recent_event()
    logger.info('last saved event was {} on {}'.format(latest_event['id'], arrow.get(latest_event['created_at'])))

    total_count = 0
    events = []

    # get since id from groupme
    for message in groupme_api.get_all_multi_media_messages_after_iter(latest_event['id']):
        media_attachment = groupme_api.get_first_image_or_video_attachment_from_groupme_message(message)

        event_obj = event_model.event_from_groupme_message(message, media_attachment)
        events.append(event_obj)

        total_count += 1

        # save events in chunks of 100
        if len(events) % 100 == 0:
            firebase_db.create_from_list(events)
            events = []

    # if there are any events remaining
    if events:
        firebase_db.create_from_list(events)

    logger.info('finished saving all {} new events'.format(total_count))


def backup_images_to_s3(firebase_db):
    # get all events in firebase that do not have a 'backup_link'
    for event in firebase_db.get_events_that_need_backup_iter():
        src_url = event['source_url']
        media_type = event['type']

        filepath = file_utils.download_file_from_url(src_url, media_type)

        # save file to s3
        # delete file
        file_utils.delete_file(filepath)
        # update firebase with 'backup_link'

if __name__ == '__main__':
    # TODO: args to save all
    # TODO: args to get most recent messages
    # TODO: args to backup any None values
    main()
