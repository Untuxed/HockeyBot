import firebase_admin
from firebase_admin import credentials, firestore, storage
from dev.devTokens import firestore_creds

firebase_cred = credentials.Certificate(firestore_creds)
firebase_admin.initialize_app(firebase_cred, {
    'storageBucket': 'voodoobot.appspot.com'
})

db = firestore.client()

# Get a reference to your storage bucket
bucket = storage.bucket()