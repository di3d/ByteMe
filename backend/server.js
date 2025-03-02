const express = require('express')
const axios = require('axios')
require('dotenv').config();

const app = express()
const port = 3000

app.get('/', (req, res) => {
  res.send('Hello World!')
})

// Middleware to parse JSON bodies
app.use(express.json());

// Endpoint to call DeepSeek's API
app.post('/call-deepseek', async (req, res) => {
    try {
        // Replace with DeepSeek's API endpoint
        const apiUrl = 'https://api.deepseek.com';

        // Get the API key from the .env file
        const apiKey = process.env.DEEPSEEK_API_KEY;

        if (!apiKey) {
            throw new Error('API key is missing. Please check your .env file.');
        }

        // Data to send to DeepSeek's API (if required)
        const requestData = req.body; // Assuming the client sends data in the request body

        // Make the API call
        const response = await axios.post(apiUrl, requestData, {
            headers: {
                'Authorization': `Bearer ${apiKey}`,
                'Content-Type': 'application/json',
            },
        });

        // Send the response back to the client
        res.status(200).json(response.data);
    } catch (error) {
        console.error('Error calling DeepSeek API:', error.message);
        res.status(500).json({ error: 'Failed to call DeepSeek API' });
    }
});

// Start the server
app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});