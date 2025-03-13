"use client";
import { useState } from "react";

export default function Build() {
  const [budget, setBudget] = useState(0);

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    console.log(event.target.value);
    setBudget(event.target.value);
  };

  return (
    <div>
      <div className="bg-blue-600 p-3 m-3 rounded-xl">
        <h1>Find Parts for your PC!</h1>
        <div className="flex">
          <div className="p-3 ">
            <h1>Find parts by PC</h1>
            <input type="text"></input>
          </div>

          <div className="p-3">
            <h2>Find specific parts</h2>
            <input type="text"></input>
          </div>
        </div>
      </div>

      <div className="bg-pink-700 flex p-3 m-3 justify-between rounded-xl">
        <div className="my-auto">New to PC building? Get some help here!</div>
        <button className="bg-green-700 p-3 rounded-xl">Help me!</button>
      </div>

      <div className="bg-pink-700 p-3 m-3 justify-between rounded-xl">
        <div className="text-xl font-bold">Requirements</div>
        <form>
          <div>
            <label htmlFor="budget_slider" className="block">
              Budget ${budget}
            </label>
            <input
              className="block"
              id="budget_slider"
              min="0"
              max="10000"
              value={budget}
              onChange={handleChange}
              type="range"
            ></input>
          </div>
          <div>
            <label>

            </label>
            <input type="radio">
            </input>
          </div>
          <div>
            <label htmlFor="ai_prompt" className="block">
              Prompt
            </label>
            <input id="ai_prompt" type="text" required className=""></input>
          </div>
        </form>
      </div>
    </div>
  );
}
