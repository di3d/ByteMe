'use client';

import { createContext, useContext, useEffect, useState } from 'react';
import { 
  User, 
  signInWithEmailAndPassword, 
  signInWithPopup, 
  GoogleAuthProvider,
  signOut as firebaseSignOut,
  onAuthStateChanged 
} from 'firebase/auth';
import { doc, setDoc, serverTimestamp } from 'firebase/firestore';
import { auth, db } from './firebase';

type AuthContextType = {
  user: User | null;
  loading: boolean;
  signInWithEmail: (email: string, password: string) => Promise<User>;
  signInWithGoogle: () => Promise<User>;
  signOut: () => Promise<void>;
};

const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
  signInWithEmail: async () => { throw new Error('Not implemented'); },
  signInWithGoogle: async () => { throw new Error('Not implemented'); },
  signOut: async () => { throw new Error('Not implemented'); }
});

  // Modify the saveUserToDatabase function to check if the user already exists first

const saveUserToDatabase = async (user: User) => {
  try {
    // First check if user already exists
    const checkResponse = await fetch(`http://localhost:5001/customer/${user.uid}`);
    const checkData = await checkResponse.json();
    
    // If user already exists in database, don't update their information
    if (checkData.code === 200) {
      return; // User exists, no need to create or update
    }
    
    // Only create new user if they don't exist
    const response = await fetch('http://localhost:5001/customer', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        customer_id: user.uid,
        email: user.email,
        name: user.displayName || 'Unknown',
        address: 'Not provided', // This only applies to new users now
      }),
    });

    if (!response.ok) {
      console.error('Failed to save user to database');
    }
  } catch (error) {
    console.error('Error saving user to database:', error);
  }
};

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // Listen for auth state changes
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      setUser(user);
      
      if (user) {
        localStorage.setItem('user_id', user.uid);
        localStorage.setItem('user_email', user.email || '');
        
        // Save user to database
        saveUserToDatabase(user);
        
        // Check if we need to redirect to account setup
        checkAndRedirectIfNeeded(user);
      } else {
        localStorage.removeItem('user_id');
        localStorage.removeItem('user_email');
      }
      
      setLoading(false);
    });
  
    return () => unsubscribe();
  }, []);

  // Sign in with email and password
  const signInWithEmail = async (email: string, password: string): Promise<User> => {
    const userCredential = await signInWithEmailAndPassword(auth, email, password);
    
    // Update user's last login time in Firestore
    await setDoc(doc(db, "users", userCredential.user.uid), {
      email: userCredential.user.email,
      lastLogin: serverTimestamp()
    }, { merge: true });
    
    return userCredential.user;
  };

  // Sign in with Google
  const signInWithGoogle = async (): Promise<User> => {
    const provider = new GoogleAuthProvider();
    const result = await signInWithPopup(auth, provider);
    
    // Save user data to Firestore
    await setDoc(doc(db, "users", result.user.uid), {
      email: result.user.email,
      displayName: result.user.displayName,
      photoURL: result.user.photoURL,
      lastLogin: serverTimestamp()
    }, { merge: true });
    
    return result.user;
  };


  // Sign out
  const signOut = async (): Promise<void> => {
    await firebaseSignOut(auth);
  };

  return (
    <AuthContext.Provider value={{ 
      user, 
      loading, 
      signInWithEmail, 
      signInWithGoogle, 
      signOut 
    }}>
      {children}
    </AuthContext.Provider>
  );
}

const checkAndRedirectIfNeeded = async (user: User) => {
  try {
    const response = await fetch(`http://localhost:8000/customer/${user.uid}`);
    const data = await response.json();
    
    // If user doesn't exist or has no valid address
    if (
      data.code === 404 || 
      (data.code === 200 && (!data.data.address || data.data.address === "Not provided"))
    ) {
      // Redirect to account setup
      window.location.href = '/account-setup';
    }
  } catch (error) {
    console.error("Error checking user profile:", error);
  }
};

export const useAuth = () => useContext(AuthContext);
