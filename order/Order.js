const express = require('express');
const cors = require('cors');
const admin = require('firebase-admin');
const { v4: uuidv4 } = require('uuid');
const app = express();
const amqp = require('amqplib');


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

// RabbitMQ Config (Match with `amqp_setup.py`)
const RABBITMQ_URL = process.env.RABBITMQ_URL || "amqp://localhost";
const EXCHANGE_NAME = "order_topic";
const ORDER_QUEUE = "Order";
const RESPONSE_QUEUE = "order.response";

async function consumeOrders() {
    try {
        // Connect to RabbitMQ
        const connection = await amqp.connect(RABBITMQ_URL);
        const channel = await connection.createChannel();

        // Ensure the queue exists 
        await channel.assertExchange(EXCHANGE_NAME, "topic", { durable: true });
        await channel.assertQueue(ORDER_QUEUE, { durable: true });
        await channel.bindQueue(ORDER_QUEUE, EXCHANGE_NAME, "order.create");

        console.log(`Listening for messages on queue: ${ORDER_QUEUE}`);

        channel.consume(ORDER_QUEUE, async (msg) => {
            if (msg !== null) {
                try {
                    const orderData = JSON.parse(msg.content.toString());
                    console.log(`Received order: ${JSON.stringify(orderData)}`);
    
                    // Generate a unique order ID
                    const order_id = uuidv4();
                    orderData.order_id = order_id;
                    orderData.order_date = new Date().toISOString();
                    orderData.status = "Pending";
    
                    // Store in Firebase
                    await ref.child(order_id).set(orderData);
                    console.log(`Order ${order_id} stored in Firebase.`);
    
                    // Send asynchronous reply (Order Confirmation)
                    const confirmationMessage = JSON.stringify({
                        order_id: order_id,
                        status: "Confirmed",
                        message: "Order successfully stored in Firebase."
                    });
    
                    channel.publish(EXCHANGE_NAME, "order.response", Buffer.from(confirmationMessage), { persistent: true });
                    console.log(`Sent order confirmation: ${confirmationMessage}`);
    
                    // Acknowledge the message
                    channel.ack(msg);

                } catch (error) {
                    console.error("❌ Error processing order:", error);
                    
                    // ✅ Reject and remove message if an error occurs (prevents infinite retries)
                    channel.nack(msg, false, false);
                }

            }
        },
        { noAck: false } // ✅ Ensures messages aren't automatically requeued
        );
    } catch (error) {
        console.error("Error in consuming orders:", error);
        
    }
}

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

const PORT = process.env.PORT || 5007;
app.listen(PORT, async () => {
    console.log(`Order Microservice running on port ${PORT}...`);
    await consumeOrders(); // Start listening for messages
});
