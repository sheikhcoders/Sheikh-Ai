import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";
import { getDatabase } from "firebase/database";

const firebaseConfig = {
  apiKey: "AIzaSyBWmAGEysUKN-2RpKrFActitwjwUe9nPy0",
  authDomain: "banglacoder-ai.firebaseapp.com",
  projectId: "banglacoder-ai",
  storageBucket: "banglacoder-ai.firebasestorage.app",
  messagingSenderId: "864273914824",
  appId: "1:864273914824:web:b689b0ba9932d336db7efd",
  measurementId: "G-3R3HE2Q2MM"
};

const app = initializeApp(firebaseConfig);
const analytics = typeof window !== 'undefined' ? getAnalytics(app) : null;
const auth = getAuth(app);
const db = getFirestore(app);
const rtdb = getDatabase(app);

export { app, analytics, auth, db, rtdb };
