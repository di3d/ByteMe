const express = require('express');
const cors = require('cors');
const admin = require('firebase-admin');
const { v4: uuidv4 } = require('uuid');
const app = express();

app.use(cors());
app.use(express.json());

// Fetch the service account key JSON file contents
const serviceAccount = require('./../privateKey.json');

// Initialize the app with a service account, granting admin privileges
admin.initializeApp({
    credential: admin.credential.cert(serviceAccount),
    databaseURL: 'https://esdteam3g7-73a7b-default-rtdb.asia-southeast1.firebasedatabase.app/'
});

// Reference to the Deliveries node in Firebase Realtime Database
const ref = admin.database().ref('Deliveries');

// Get Delivery [GET] /delivery/{deliveryID}
app.get('/delivery/:delivery_id', async (req, res) => {
    try {
        const delivery_id = req.params.delivery_id;
        const snapshot = await ref.child(delivery_id).once('value');
        const delivery = snapshot.val();

        // Set the content type to application/json
        res.setHeader('Content-Type', 'application/json');

        if (delivery) {
            return res.status(200).json({
                code: 200,
                message: 'Delivery retrieved successfully',
                data: delivery
            });
        } else {
            return res.status(404).json({
                code: 404,
                message: 'Delivery not found'
            });
        }
    } catch (e) {
        return res.status(500).json({ code: 500, message: e.message });
    }
});

// Create Delivery Task [POST] /delivery
app.post('/delivery', async (req, res) => {
    try {
        const data = req.body;

        // Validate required fields
        if (!data.customerAddress || !data.customerEmail) {
            return res.status(400).json({ 
                code: 400, 
                message: 'Missing required fields: customerAddress or customerEmail' 
            });
        }

        // Generate a unique delivery_id
        const delivery_id = uuidv4();

        // Generate a timestamp for the delivery creation
        const timestamp = new Date().toISOString();

        // Create delivery data with the schema from the diagram
        const delivery_data = {
            deliveryID: delivery_id,
            timestamp: timestamp,
            customerAddress: data.customerAddress,
            customerEmail: data.customerEmail
        };

        // Store in Realtime Database
        await ref.child(delivery_id).set(delivery_data);

        return res.status(201).json({
            code: 201,
            message: 'Delivery task created successfully',
            data: delivery_data
        });

    } catch (e) {
        return res.status(500).json({ code: 500, message: e.message });
    }
});

// Update delivery information
app.put('/delivery/:delivery_id', async (req, res) => {
    try {
        const delivery_id = req.params.delivery_id;
        const data = req.body;

        // Validate required fields
        if (!data.customerAddress && !data.customerEmail) {
            return res.status(400).json({ 
                code: 400, 
                message: 'No fields to update provided' 
            });
        }

        // Check if delivery exists
        const snapshot = await ref.child(delivery_id).once('value');
        if (!snapshot.exists()) {
            return res.status(404).json({
                code: 404,
                message: 'Delivery not found'
            });
        }

        // Create updated delivery data
        const update_data = {};
        if (data.customerAddress) update_data.customerAddress = data.customerAddress;
        if (data.customerEmail) update_data.customerEmail = data.customerEmail;
        
        // Update timestamp
        update_data.timestamp = new Date().toISOString();

        // Update in Realtime Database
        await ref.child(delivery_id).update(update_data);

        // Get the updated data
        const updatedSnapshot = await ref.child(delivery_id).once('value');

        return res.status(200).json({
            code: 200,
            message: 'Delivery updated successfully',
            data: updatedSnapshot.val()
        });

    } catch (e) {
        return res.status(500).json({ code: 500, message: e.message });
    }
});

// Delete delivery
app.delete('/delivery/:delivery_id', async (req, res) => {
    try {
        const delivery_id = req.params.delivery_id;

        // Check if delivery exists
        const snapshot = await ref.child(delivery_id).once('value');
        if (!snapshot.exists()) {
            return res.status(404).json({
                code: 404,
                message: 'Delivery not found'
            });
        }

        // Delete from Realtime Database
        await ref.child(delivery_id).remove();

        return res.status(200).json({
            code: 200,
            message: 'Delivery deleted successfully'
        });

    } catch (e) {
        return res.status(500).json({ code: 500, message: e.message });
    }
});

app.listen(5008, () => {
    console.log('Delivery service is running on port 5008');
});
