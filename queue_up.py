import logging
import sys

import config

from groupme import GroupMeAPI
from firebase import Firebase

# logging setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

stdoutput = logging.StreamHandler(sys.stdout)
stdoutput.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.addHandler(stdoutput)


# TODO: create a GroupMe Class
def main():
    groupme_api = GroupMeAPI(config.GROUPME_URL, config.GROUP_ID, config.GROUP_NAME, config.GROUPME_ACCESS_TOKEN)

    assert(groupme_api.verfify_group_exists())
    for msg in groupme_api.get_all_multi_media_messages_iter():
        print(msg)

    firebase_db = Firebase(config.FIREBASE_SERVICE_ACCOUNT_PRIVATE_KEY, config.FIREBASE_DATABASE_URL)
    # save_all_multi_media_messages


def save_all_multi_media_messages(groupme_api, firebase_db):
    total_count = 0
    events = []

    for message in groupme_api.get_all_multi_media_messages_iter():
        event_obj = groupme_api.create_event_from_groupme_message(message)
        print(event_obj)
        total_count += 1

        # save events in chunks of 100
        if events % 100 == 0:
            firebase_db.create_from_list(events)
            events = []

    # if there are any events remaining
    if events:
        firebase_db.create_from_list(events)

    logger.info('finished saving all {} events'.format(total_count))


if __name__ == '__main__':
    main()
