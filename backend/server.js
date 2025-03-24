const express = require("express");
const cors = require("cors");
const axios = require("axios");

const app = express();
app.use(cors());
app.use(express.json());

const OLLAMA_URL = "http://localhost:11434/api/generate";
const OUTSYSTEMS_URL = "https://personal-0careuf6.outsystemscloud.com/ByteMeComponentService/rest/ComponentAPI/AllComponents";

app.post("/chat", async (req, res) => {
  const { message } = req.body;

  try {
    // Fetch available components from OutSystems
    const osResponse = await axios.get(OUTSYSTEMS_URL);
    const components = osResponse.data || [];

    // Convert components list into a format Ollama can use
    const componentList = components
      .map((c) => `${c.Name} - ${c.Specs}`)
      .join("\n");

    // Send query to Ollama
    const ollamaResponse = await axios.post(OLLAMA_URL, {
      model: "deepseek-r1:14b",
      prompt: `Available components:\n${componentList}\n\nRecommend PC parts based on: ${message} \n Do not deviate outside of the components given to you. \n Your component list should have the following components, in this order : CPU, Motherboard, GPU, RAM, SSD, CASING, PSU, COOLER \n Where there are no suitable parts, simply put no recommendations`,
      stream: false,
    });

    // Extract response and remove <think> tags
    let reply = ollamaResponse.data.response;
    reply = reply.replace(/<think>.*?<\/think>/gs, "").trim(); // Remove all <think>...</think> content

    res.json({ reply });
  } catch (error) {
    console.error("Error:", error.message);
    res.status(500).json({ error: "Error processing request" });
  }
});

app.listen(5000, () => console.log("Server running on port 5000"));
