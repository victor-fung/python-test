# Ghost Name Picker

Ghost Name Picker is an example application showing basic usage of Google App
Engine. Users can see a list of ghost names & pick a ghost name from 3 random available names
after they log-in with their Google account. Names are stored in App Engine (NoSQL)
High Replication Datastore (HRD) and retrieved using a strongly consistent
(ancestor) query.

## Products
- [App Engine][1]

## Language
- [Python][2]

## APIs
- [NDB Datastore API][3]
- [Users API][4]

## Dependencies
- [webapp2][5]
- [jinja2][6]
- [Twitter Bootstrap][7]

## Installation
- Install Python 2.7, gcloud components and extra libraries [8]

## Running on local machine
- dev_appserver.py app.yaml

## Deployment
- For deployment setup, run gcloud init and follow the step prompts
- Deploying index file: gcloud app deploy index.yaml, it is recommended to deploy index file first as indexing can take some time
- App deployment: gcloud app deploy

## View your app on live
- To browse your app on live, run gcloud app browse

## Adding ghost names
- You will be able to see a button to add ghost names after you logged in as an admin, admin is defaulted to the owner of the project

## Accessing your Google App Engine console
- https://console.cloud.google.com/

## Limitations
- This app doesn't scale well in regards to picking up 3 random ghost names as we can only fetch all available names first then pick 3 random names.


[1]: https://developers.google.com/appengine
[2]: https://python.org
[3]: https://developers.google.com/appengine/docs/python/ndb/
[4]: https://developers.google.com/appengine/docs/python/users/
[5]: http://webapp-improved.appspot.com/
[6]: http://jinja.pocoo.org/docs/
[7]: http://twitter.github.com/bootstrap/
[8]: https://cloud.google.com/appengine/docs/standard/python/download
