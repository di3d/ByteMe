const express = require('express')
const axios = require('axios')
require('dotenv').config();

const app = express();
const port = 3001;

// Middleware to parse JSON bodies
app.use(express.json());

// Endpoint to interact with DeepSeek
app.post('/generate', async (req, res) => {
  try {
    // Extract the prompt from the request body
    const { prompt } = req.body;

    if (!prompt) {
      return res.status(400).json({ error: 'Prompt is required' });
    }

    // Send a request to the local DeepSeek model
    const response = await axios.post('http://localhost:11434/api/generate', {
      model: 'deepseek-r1:14b',
      prompt: prompt,
    }, {
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Return the response from DeepSeek to the client
    res.json(response.data);
  } catch (error) {
    console.error('Error calling DeepSeek:', error.message);
    res.status(500).json({ error: 'Failed to generate response' });
  }
});

// Start the server
app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});