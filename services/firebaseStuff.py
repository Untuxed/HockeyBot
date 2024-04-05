import firebase_admin
from firebase_admin import credentials, firestore
from dev.devTokens import firestore_creds

firebase_cred = credentials.Certificate(firestore_creds)
firebase_admin.initialize_app(firebase_cred)

db = firestore.client()
