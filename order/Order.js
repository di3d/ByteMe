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

// Reference to the Orders node in Firebase Realtime Database
const ref = admin.database().ref('Orders');

app.get('/order/:order_id', async (req, res) => {
    try {
        const order_id = req.params.order_id;
        const snapshot = await ref.child(order_id).once('value');
        const order = snapshot.val();

        // Set the content type to application/json
        res.setHeader('Content-Type', 'application/json');

        if (order) {
            return res.status(200).json({
                code: 200,
                message: 'Order retrieved successfully',
                data: order
            });
        } else {
            return res.status(404).json({
                code: 404,
                message: 'Order not found'
            });
        }
    } catch (e) {
        return res.status(500).json({ code: 500, message: e.message });
    }
});


app.post('/order', async (req, res) => {
    try {
        const data = req.body;

        // Validate required fields
        if (!data.customer_id || !data.parts_list) {
            return res.status(400).json({ code: 400, message: 'Missing required field: customer_id or parts_list' });
        }

        // Ensure customer_id is 36 characters long
        if (typeof data.customer_id !== 'string' || data.customer_id.length !== 36) {
            return res.status(400).json({ code: 400, message: 'Invalid customer_id format' });
        }

        // Generate a unique order_id
        const order_id = uuidv4();

        // Generate a timestamp for the order date
        const order_date = new Date().toISOString();

        // Create order data
        const order_data = {
            customer_id: data.customer_id,
            parts_list: data.parts_list,
            order_date: order_date
        };

        // Store in Firebase
        await ref.child(order_id).set(order_data);

        return res.status(201).json({
            code: 201,
            message: 'Order created successfully',
            data: order_data
        });

    } catch (e) {
        return res.status(500).json({ code: 500, message: e.message });
    }
});

app.put('/order/:order_id', async (req, res) => {
    try {
        const order_id = req.params.order_id;
        const data = req.body;

        // Validate required fields
        if (!data.customer_id || !data.parts_list) {
            return res.status(400).json({ code: 400, message: 'Missing required field: customer_id or parts_list' });
        }

        // Ensure customer_id is 36 characters long
        if (typeof data.customer_id !== 'string' || data.customer_id.length !== 36) {
            return res.status(400).json({ code: 400, message: 'Invalid customer_id format' });
        }

        // Generate a timestamp for the order date
        const order_date = new Date().toISOString();

        // Create updated order data
        const order_data = {
            customer_id: data.customer_id,
            parts_list: data.parts_list,
            order_date: order_date
        };

        // Update in Firebase
        await ref.child(order_id).update(order_data);

        return res.status(200).json({
            code: 200,
            message: 'Order updated successfully',
            data: order_data
        });

    } catch (e) {
        return res.status(500).json({ code: 500, message: e.message });
    }
});

app.delete('/order/:order_id', async (req, res) => {
    try {
        const order_id = req.params.order_id;

        // Delete from Firebase
        await ref.child(order_id).remove();

        return res.status(200).json({
            code: 200,
            message: 'Order deleted successfully'
        });

    } catch (e) {
        return res.status(500).json({ code: 500, message: e.message });
    }
});

app.listen(5007, () => {
    console.log('Server is running on port 5007');
});
