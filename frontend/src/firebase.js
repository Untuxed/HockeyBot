import { initializeApp } from "firebase/app";
import { getFirestore } from "firebase/firestore";

// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

const firebaseConfig = {
  apiKey: "AIzaSyA_dDkB9GtRBQ1KxIuB8c3aRolwyDMaaN0",
  authDomain: "voodoobot.firebaseapp.com",
  projectId: "voodoobot",
  storageBucket: "voodoobot.appspot.com",
  messagingSenderId: "192978520841",
  appId: "1:192978520841:web:56b8d3a7dfb10c8dcee1d8"
};

const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

export { db };