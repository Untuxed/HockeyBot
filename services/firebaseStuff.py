import firebase_admin
from firebase_admin import credentials, firestore

firebase_cred = credentials.Certificate("./dev/voodoobot-firebase-adminsdk-f1enb-2774617ac1.json")
firebase_admin.initialize_app(firebase_cred)

db = firestore.client()

# Create a reference to the 'hello-world' collection
collection_ref = db.collection('hello-world')

# Add a document with ID 'greeting' and data {'message': 'Hello, world!'}
collection_ref.document('greeting').set({'message': 'Hello, world!'})