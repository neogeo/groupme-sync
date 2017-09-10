import config
from queue_up import save_since_last_message, backup_media_to_s3
from groupme import GroupMeAPI
from firebase import Firebase


def handler(event, context):
    '''Save all messages since last, and backup all media to S3
    '''
    groupme_api = GroupMeAPI(config.GROUPME_URL, config.GROUP_ID, config.GROUP_NAME, config.GROUPME_ACCESS_TOKEN)
    firebase_db = Firebase(config.FIREBASE_SERVICE_ACCOUNT_PRIVATE_KEY, config.FIREBASE_DATABASE_URL)

    save_since_last_message(groupme_api, firebase_db)
    backup_media_to_s3(firebase_db)

    print('done')
    return True
