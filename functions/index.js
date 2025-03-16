// /**
//  * Import function triggers from their respective submodules:
//  *
//  * const {onCall} = require("firebase-functions/v2/https");
//  * const {onDocumentWritten} = require("firebase-functions/v2/firestore");
//  *
//  * See a full list of supported triggers at https://firebase.google.com/docs/functions
//  */

// const functions = require('firebase-functions');
// const admin = require('firebase-admin');
// const express = require('express');
// const cors = require('cors');

// const {onRequest} = require("firebase-functions/v2/https");
// const logger = require("firebase-functions/logger");

// // Initialize Firebase Admin SDK
// admin.initializeApp({
//   credential: admin.credential.applicationDefault(),
//   databaseURL: 'https://esdteam3g7-73a7b-default-rtdb.asia-southeast1.firebasedatabase.app/'
// });

// // Create an Express app
// const app = express();
// app.use(cors());
// app.use(express.json());

// // Reference to the Customers node in Firebase Realtime Database
// const ref = admin.database().ref('Customers');

// // Define the endpoints
// app.get('/customer/:customer_id', async (req, res) => {
//   try {
//     const customer_id = req.params.customer_id;
//     const snapshot = await ref.child(customer_id).once('value');
//     const customer = snapshot.val();

//     if (customer) {
//       return res.status(200).json({
//         code: 200,
//         data: customer
//       });
//     } else {
//       return res.status(404).json({
//         code: 404,
//         message: 'Customer not found'
//       });
//     }
//   } catch (e) {
//     return res.status(500).json({ code: 500, message: e.message });
//   }
// });

// app.post('/customer', async (req, res) => {
//   try {
//     const data = req.body;

//     // Validate required fields
//     const required_fields = ['customer_id', 'name', 'address', 'email'];
//     for (const field of required_fields) {
//       if (!data[field]) {
//         return res.status(400).json({
//           code: 400,
//           message: `Missing required field: ${field}`
//         });
//       }
//     }

//     // Create customer data
//     const customer_id = data.customer_id;
//     const customer_data = {
//       name: data.name,
//       address: data.address,
//       email: data.email
//     };

//     // Store in Firebase
//     await ref.child(customer_id).set(customer_data);

//     return res.status(201).json({
//       code: 201,
//       message: 'Customer created successfully',
//       data: customer_data
//     });
//   } catch (e) {
//     return res.status(500).json({ code: 500, message: e.message });
//   }
// });

// // Export the Express app as a Firebase function
// exports.api = functions.https.onRequest(app);

