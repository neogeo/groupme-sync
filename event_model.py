

def event_from_groupme_message(groupme_message, media_attachment):
    # get the first mdeia attachment
    media_type, media_url = media_attachment['type'], media_attachment['url']
    # Only images can have captions
    caption = groupme_message['text'] if media_type == 'image' else None

    groupme_id = groupme_message['id']
    created_at_ts = groupme_message['created_at']
    hearted = True if groupme_message['favorited_by'] else False
    backup_link = None

    event_obj = {
        'id': groupme_id,
        'type': media_type,
        'source_url': media_url,
        'created_at': created_at_ts,
        'hearted': hearted,
        'caption': caption,
        'backup_link': backup_link,
    }
    return event_obj


def event_from_firebase_response(firebase_event_json):
    '''Firebase does not save objs with none as the value.
    Replace non-existant fields with None
    '''
    event_obj = {
        'id': firebase_event_json['id'],
        'type': firebase_event_json['type'] if 'type' in firebase_event_json else None,
        'source_url': firebase_event_json['source_url'] if 'source_url' in firebase_event_json else None,
        'created_at': firebase_event_json['created_at'] if 'created_at' in firebase_event_json else None,
        'hearted': firebase_event_json['hearted'] if 'hearted' in firebase_event_json else None,
        'caption': firebase_event_json['caption'] if 'caption' in firebase_event_json else None,
        'backup_link': firebase_event_json['backup_link'] if 'backup_link' in firebase_event_json else None,
    }

    return event_obj
