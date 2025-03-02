import OpenAI from "openai";
import dotenv from "dotenv";


const openai = new OpenAI({
        baseURL: 'https://api.deepseek.com',
        apiKey: 'sk-bdd178e0f2634274a0c1fe94e2e3d90e',
});

async function main() {
  const completion = await openai.chat.completions.create({
    messages: [{ role: "system", content: "You are a helpful assistant." }],
    model: "deepseek-chat",
  });

  console.log(completion.choices[0].message.content);
}

main();