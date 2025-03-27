import { useState } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { recommendationsCollection } from "@/lib/firebase";  // Import firebase collection
import { addDoc } from "firebase/firestore";  // Import Firestore function for adding documents

export default function Chat() {
  const [messages, setMessages] = useState<{ role: string; text: string }[]>([]);
  const [input, setInput] = useState("");

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { role: "user", text: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    try {
      const response = await axios.post("http://localhost:5000/chat", { message: input });

      // Clean the response by removing <think> tags
      const cleanedResponse = response.data.reply.replace(/<think.*?>.*?<\/think>/g, "").trim();

      // Add bot message to chat
      const botMessage = { role: "bot", text: cleanedResponse };
      setMessages((prev) => [...prev, botMessage]);

      // Save the recommendation to Firebase (you may extract parts from cleanedResponse)
      const recommendationData = {
        userMessage: input,
        recommendedParts: cleanedResponse,  // Modify this to store the relevant parts data
        timestamp: new Date()
      };

      // Save to Firestore
      await addDoc(recommendationsCollection, recommendationData);

    } catch (error) {
      console.error("Error:", error);
    }
  };

  return (
    <div className="flex flex-col h-full w-full p-4 bg-gray-900 text-white">
      <div className="flex-1 overflow-y-auto p-2">
        {messages.map((msg, index) => (
          <div key={index} className={`p-2 my-1 ${msg.role === "user" ? "text-right" : "text-left"}`}>
            <span className={`inline-block p-2 rounded-lg ${msg.role === "user" ? "bg-blue-600" : "bg-gray-700"}`}>
              {msg.text}
            </span>
          </div>
        ))}
      </div>

      <div className="flex gap-2">
        <Input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about PC parts..."
          className="flex-1"
        />
        <Button onClick={sendMessage}>Send</Button>
      </div>
    </div>
  );
}
