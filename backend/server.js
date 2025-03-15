const express = require("express");
const cors = require("cors");
const axios = require("axios");

const app = express();
app.use(cors());
app.use(express.json());

const OLLAMA_URL = "http://localhost:11434/api/generate";

app.post("/chat", async (req, res) => {
  const { message } = req.body;

  try {
    const response = await axios.post(OLLAMA_URL, {
      model: "deepseek-r1:14b",
      prompt: `Recommend PC parts based on: ${message}`,
      stream: false,
    });

    res.json({ reply: response.data.response });
  } catch (error) {
    res.status(500).json({ error: "Error communicating with Ollama" });
  }
});

app.listen(5000, () => console.log("Server running on port 5000"));
