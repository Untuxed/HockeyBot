import firebase_admin
from firebase_admin import credentials, firestore
from dev.devTokens import google_creds

firebase_cred = credentials.Certificate(google_creds)
firebase_admin.initialize_app(firebase_cred)

db = firestore.client()

# # Create a reference to the 'hello-world' collection
# collection_ref = db.collection('hello-world')

# # Add a document with ID 'greeting' and data {'message': 'Hello, world!'}
# collection_ref.document('greeting').set({'message': 'Hello, world!'})