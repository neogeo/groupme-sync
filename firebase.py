import copy
import logging
import sys

import event_model
import firebase_admin
from firebase_admin import credentials, db

# logging setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

stdoutput = logging.StreamHandler(sys.stdout)
stdoutput.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.addHandler(stdoutput)


class Firebase():
    def __init__(self, path_to_firebase_service_account_private_key, firebase_database_url):
        self.root = self._firebase_login(path_to_firebase_service_account_private_key, firebase_database_url)

    def _firebase_login(self, creds_path, database_url):
        cred = credentials.Certificate(creds_path)
        #  Initialize the app with a service account, granting admin privileges
        firebase_admin.initialize_app(cred, {
            'databaseURL': database_url,
        })
        root = db.reference()

        return root

    def get_root_for_query(self):
        return self.root

    def get_json(self, event_id):
        path = 'events/{}'.format(event_id)
        event = self.root.child(path).get()

        if event is None:
            raise Exception('event with id {} not found'.format(event_id))

        return event_model.event_from_firebase_response(event)

    def create_from_list(self, event_objs):
        if not isinstance(event_objs, list):
            raise Exception('must have a list of events to save {}'.format(event_objs))

        for event in event_objs:
            self.create(event)

        logger.info('finished saving {} events'.format(len(event_objs)))

    def create(self, event_obj):
        path = 'events/{}'.format(event_obj['id'])
        # save with a specified id
        self.root.child(path).set(event_obj)

        logger.info('saved event {}'.format(event_obj['id']))

    def update(self, event_obj):
        path = 'events/{}'.format(event_obj['id'])
        self.root.child(path).update(event_obj)

    def delete(self, event_id):
        path = 'events/{}'.format(event_id)
        self.root.child(path).delete()

    def get_most_recent_event(self):
        # order by 'created_at' in descending order
        res = self.root.child('events').order_by_child('created_at').limit_to_last(1).get()
        event_json = res.values()[0]

        return event_model.event_from_firebase_response(event_json)

    def get_events_that_need_backup(self):
        '''Get events with 'backup_link == none'
        returns a list of events
        '''
        res = self.root.child('events').order_by_child('backup_link').limit_to_first(5).get()

        return [event_model.event_from_firebase_response(event_json) for event_json in res.values()]

    def get_events_that_need_backup_iter(self):
        '''***Assumes the client updates the 'backup_link' field***
        Firebase sucks because it doesn't handle pagination correctly https://github.com/firebase/FirebaseUI-iOS/issues/9
        So the client must update the 'backup_link' field inorder for this iter to eventually stop. there is a safe guard
        to prevent it from going into an infinite loop
        '''
        last_res = None
        next_res = self.get_events_that_need_backup()
        total = 0

        while next_res:
            for event_json in next_res:
                event = event_model.event_from_firebase_response(event_json)
                total += 1
                yield event

            last_res = copy.deepcopy(next_res)
            next_res = self.get_events_that_need_backup()

            if last_res == next_res:
                raise Exception('please update the backup_links, or this could go on forever')

        logger.info('finished fetching all {} events that need backup messages'.format())
