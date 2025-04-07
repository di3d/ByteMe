const express = require("express");
const cors = require("cors");
const axios = require("axios");
const { json } = require("body-parser");

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
      model: "llama3.2",
      prompt: `Available components: ${componentList} 
      Recommend PC parts based on: ${message}
      Do not deviate outside of the components given to you. 
      Your component list should have the following components, in this order : CPU, Motherboard, GPU, RAM, SSD, CASING, PSU, COOLER 
      Where there are no suitable parts, simply put no recommendations`,
      stream: false,
      format: {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "PC Component Recommendation",
        "description": "A schema for recommended PC components with IDs",
        "type": "object",
        "properties": {
          "CPU": {
            "type": "object",
            "properties": {
              "Name": {
                "type": "string",
                "description": "CPU model name",
                "examples": ["Intel Core i9-13900K", "AMD Ryzen 9 7950X"]
              },
              "ComponentId": {
                "type": "integer",
                "description": "Unique identifier for the component",
                "examples": [101, 102]
              }
            },
            "required": ["Name", "ComponentId"]
          },
          "Motherboard": {
            "type": "object",
            "properties": {
              "Name": {
                "type": "string",
                "description": "Motherboard model name",
                "examples": ["ASUS ROG Maximus Z790 Hero", "MSI MAG B550 TOMAHAWK"]
              },
              "ComponentId": {
                "type": "integer",
                "description": "Unique identifier for the component",
                "examples": [201, 202]
              }
            },
            "required": ["Name", "ComponentId"]
          },
          "GPU": {
            "type": "object",
            "properties": {
              "Name": {
                "type": "string",
                "description": "GPU model name",
                "examples": ["NVIDIA RTX 4090", "AMD Radeon RX 7900 XTX"]
              },
              "ComponentId": {
                "type": "integer",
                "description": "Unique identifier for the component",
                "examples": [301, 302]
              }
            },
            "required": ["Name", "ComponentId"]
          },
          "RAM": {
            "type": "object",
            "properties": {
              "Name": {
                "type": "string",
                "description": "RAM kit name",
                "examples": ["32GB DDR5-6000", "64GB DDR4-3600"]
              },
              "ComponentId": {
                "type": "integer",
                "description": "Unique identifier for the component",
                "examples": [401, 402]
              }
            },
            "required": ["Name", "ComponentId"]
          },
          "SSD": {
            "type": "object",
            "properties": {
              "Name": {
                "type": "string",
                "description": "SSD model name",
                "examples": ["Samsung 990 Pro 2TB", "WD Black SN850X 1TB"]
              },
              "ComponentId": {
                "type": "integer",
                "description": "Unique identifier for the component",
                "examples": [501, 502]
              }
            },
            "required": ["Name", "ComponentId"]
          },
          "CASING": {
            "type": "object",
            "properties": {
              "Name": {
                "type": "string",
                "description": "Case model name",
                "examples": ["Lian Li PC-O11 Dynamic", "Fractal Design Torrent"]
              },
              "ComponentId": {
                "type": "integer",
                "description": "Unique identifier for the component",
                "examples": [601, 602]
              }
            },
            "required": ["Name", "ComponentId"]
          },
          "PSU": {
            "type": "object",
            "properties": {
              "Name": {
                "type": "string",
                "description": "Power supply model name",
                "examples": ["Corsair RM1000x", "Seasonic PRIME TX-1000"]
              },
              "ComponentId": {
                "type": "integer",
                "description": "Unique identifier for the component",
                "examples": [701, 702]
              }
            },
            "required": ["Name", "ComponentId"]
          },
          "COOLER": {
            "type": "object",
            "properties": {
              "Name": {
                "type": "string",
                "description": "Cooler model name",
                "examples": ["Noctua NH-D15", "Corsair iCUE H150i ELITE LCD"]
              },
              "ComponentId": {
                "type": "integer",
                "description": "Unique identifier for the component",
                "examples": [801, 802]
              }
            },
            "required": ["Name", "ComponentId"]
          }
        },
        "required": ["CPU", "Motherboard", "GPU", "RAM", "SSD", "CASING", "PSU", "COOLER"],
        "additionalProperties": false
      }
      
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
