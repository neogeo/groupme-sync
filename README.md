# groupme-sync
Download all media (pictures and video) from a GroupMe group, and keep future updates in sync with S3. Uses Firebase as the database.

### Language
Python 2.7

### Usage
There are three command line arguments: ['save_all', 'save_most_recent', 'backup_to_s3']
- `save_all`: Saves all events from the group, and sets the `backup_link` to `None`. Each event will be backed up at a later time. This should only be run once
- `save_most_recent`: Saves all new events created since the last saved event. This set the `backup_link` to `None`.
- `back_up_to_s3`: Backs up all events with `backup_link=None` to S3

Example usage:
- 1 Run `>>python save_all` once
- 2 Then schedule `>>python save_most_recent` and `>>python backup_to_s3` to run peroidcally

### How to Run
1. Create a GroupMe, Firebase, and S3 account
2. [Configure](http://docs.aws.amazon.com/cli/latest/userguide/installing.html) `awscli`
3. Fill out `config.py` with your credentials
4. Replace `firebase_service_account_private_key.json` with your Firebase credential file. You can get this by creating a service account for your project [here](https://console.firebase.google.com/project/YOUR-PROJECT/settings/serviceaccounts) and generate a new private key json file
5. Your Firebase realtime database must have an index. Go the 'rules' page in Firebase, and set the following index rule:
```json
{
  "rules": {
    ".read": "auth != null",
    ".write": "auth != null",
    "events": {
      ".indexOn": ["created_at", "hearted", "backup_link"]
    }
  }
}
```
6. Run for the first time:
```
>> virtualenv .env
>> pip install -r requirements.txt
>> . .env/bin/activate
>> python save_all
```

### Design
```
get all events -> save in firebase --> upload to S3 ->
                        ^                            |
                        ^                            |
                        <- get most recent events <-<-
```

