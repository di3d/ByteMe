export default function Build() {
    return (
        <div>
            <div>

                <h1>ByteMe</h1>
            </div>
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

            <div>
                <input type="text" placeholder="the ai input goes here!"></input>
            </div>

            <div className="budget">
                <label htmlFor="budget_slider">What's your budget?</label>
                <input id="budget_slider" type="range">

                </input>
            </div>

        </div>
    )
}