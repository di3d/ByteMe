import { Button } from "@/components/ui/button"
import Link from "next/link"



export default function Page() {
  return (
    <div>
      <div className="w-full bg-gradient-to-r from-blue-800 via-purple-800 to-pink-800 py-20 px-6 text-center text-white">
        <h1 className="text-5xl font-extrabold">Welcome to ByteMe!</h1>
        <p className="text-lg mt-4">Your community-powered PC builder with real user recommendations</p>
        <div className="mt-8 flex justify-center gap-4">
          <Button className="bg-white text-blue-500 hover:bg-gray-800 px-6 py-3 rounded-lg text-lg"><Link href="/build"> Start Building</Link></Button>
          <Button className="bg-transparent border-2 border-white text-white hover:bg-white hover:text-blue-500 px-6 py-3 rounded-lg text-lg"><Link href="/browse"> Browse Builds</Link></Button>
        </div>
      </div>

      <section className="py-16 bg-gray-900 text-center">
        <h2 className="text-4xl font-semibold text-white">How It Works</h2>
        <p className="text-lg text-gray-400 mt-4 mb-8">Get recommendations from real PC builders who've been where you are.</p>
        
        <div className="flex justify-center gap-8">
          <div className="flex flex-col items-center">
            <div className="bg-blue-500 text-white p-4 rounded-full w-24 h-24 flex items-center justify-center">
              <span className="text-3xl">1</span>
            </div>
            <h3 className="text-2xl mt-4 font-semibold text-white">Share Your Needs</h3>
            <p className="text-gray-400 mt-2">Tell us about your budget, use case, and preferences.</p>
          </div>
          
          <div className="flex flex-col items-center">
            <div className="bg-purple-500 text-white p-4 rounded-full w-24 h-24 flex items-center justify-center">
              <span className="text-3xl">2</span>
            </div>
            <h3 className="text-2xl mt-4 font-semibold text-white">Get Community Recommendations</h3>
            <p className="text-gray-400 mt-2">See builds and part lists from users with similar needs.</p>
          </div>
          
          <div className="flex flex-col items-center">
            <div className="bg-pink-500 text-white p-4 rounded-full w-24 h-24 flex items-center justify-center">
              <span className="text-3xl">3</span>
            </div>
            <h3 className="text-2xl mt-4 font-semibold text-white">Build & Share</h3>
            <p className="text-gray-400 mt-2">Create your perfect build and help others by sharing your experience.</p>
          </div>
        </div>
      </section>

      <section className="py-16 bg-gray-800 text-center">
        <h2 className="text-4xl font-semibold text-white">Why Choose ByteMe?</h2>
        <p className="text-lg text-gray-400 mt-4 mb-8">Real recommendations from real builders who've faced the same challenges.</p>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
          <div className="p-8 bg-gray-700 rounded-xl shadow-md">
            <h3 className="text-2xl font-semibold text-blue-500">Community Wisdom</h3>
            <p className="mt-4 text-gray-300">Access thousands of verified builds from our active community of PC enthusiasts.</p>
          </div>
          
          <div className="p-8 bg-gray-700 rounded-xl shadow-md">
            <h3 className="text-2xl font-semibold text-purple-500">Proven Performance</h3>
            <p className="mt-4 text-gray-300">See builds that have been tested and reviewed by real users for real-world performance.</p>
          </div>
          
          <div className="p-8 bg-gray-700 rounded-xl shadow-md">
            <h3 className="text-2xl font-semibold text-pink-500">Budget-Friendly Options</h3>
            <p className="mt-4 text-gray-300">Find builds at every price point with honest feedback about value and performance.</p>
          </div>
        </div>
      </section>

      <section className="py-16 bg-gray-900">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-semibold text-white">Join Our Growing Community</h2>
          <p className="text-lg text-gray-400 mt-4">
            Over 50,000 PC builders share their knowledge and builds to help others.
            Be part of something bigger - where every recommendation comes from experience.
          </p>
          <div className="mt-8 flex justify-center gap-4">
            <Button  className="bg-blue-500 text-white hover:bg-blue-600 px-6 py-3 rounded-lg text-lg" >
              <Link href="/build"> See Popular Builds</Link>
            </Button>
            <Button className="bg-transparent border-2 border-white text-white hover:bg-white hover:text-blue-500 px-6 py-3 rounded-lg text-lg">
              Join Discussions
            </Button>
          </div>
        </div>
      </section>

      <section className="py-20 bg-gradient-to-r from-blue-800 to-pink-800 text-center text-white">
        <h2 className="text-3xl font-semibold">Ready to Build With Community Support?</h2>
        <p className="text-lg mt-4">Join thousands of PC builders who help each other create the perfect machines.</p>
        <div className="mt-8">
          <Button className="bg-white text-blue-500 hover:bg-gray-800 px-6 py-3 rounded-lg text-lg">Start Your Build</Button>
        </div>
      </section>
    </div>
  )
}