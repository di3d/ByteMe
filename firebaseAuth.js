const admin = require('firebase-admin');
const serviceAccount = require('./privateKey.json');

// Initialize the Firebase Admin SDK
admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
  databaseURL: `https://${serviceAccount.project_id}.firebaseio.com`
});

// Function to create a new user
async function createUser(email, password) {
  try {
    const userRecord = await admin.auth().createUser({
      email: email,
      password: password,
    });
    console.log('Successfully created new user:', userRecord.uid);
  } catch (error) {
    console.error('Error creating new user:', error);
  }
}

// Function to verify a user token
async function verifyUserToken(idToken) {
  try {
    const decodedToken = await admin.auth().verifyIdToken(idToken);
    console.log('Token verified successfully:', decodedToken.uid);
    return decodedToken;
  } catch (error) {
    console.error('Error verifying token:', error);
  }
}

module.exports = {
  createUser,
  verifyUserToken,
};