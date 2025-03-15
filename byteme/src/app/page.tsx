import { AppSidebar } from "@/components/app-sidebar"
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar"

export default function Page() {
  return (
<div>
<div className="w-full bg-gradient-to-r from-blue-800 via-purple-800 to-pink-800 py-20 px-6 text-center text-white">
  <h1 className="text-5xl font-extrabold">Welcome to ByteMe</h1>
  <p className="text-lg mt-4">Your AI-powered PC builder for the ultimate custom builds</p>
  <div className="mt-8 flex justify-center gap-4">
    <Button className="bg-white text-blue-500 hover:bg-gray-800 px-6 py-3 rounded-lg text-lg">Start Building</Button>
    <Button className="bg-transparent border-2 border-white text-white hover:bg-white hover:text-blue-500 px-6 py-3 rounded-lg text-lg">Learn More</Button>
  </div>
</div>

<section className="py-16 bg-gray-900 text-center">
  <h2 className="text-4xl font-semibold text-white">How It Works</h2>
  <p className="text-lg text-gray-400 mt-4 mb-8">Our AI helps you choose the best PC components based on your needs and preferences.</p>
  
  <div className="flex justify-center gap-8">
    <div className="flex flex-col items-center">
      <div className="bg-blue-500 text-white p-4 rounded-full w-24 h-24 flex items-center justify-center">
        <span className="text-3xl">1</span>
      </div>
      <h3 className="text-2xl mt-4 font-semibold text-white">Tell Us Your Needs</h3>
      <p className="text-gray-400 mt-2">Describe your needs, whether it’s gaming, streaming, or productivity.</p>
    </div>
    
    <div className="flex flex-col items-center">
      <div className="bg-purple-500 text-white p-4 rounded-full w-24 h-24 flex items-center justify-center">
        <span className="text-3xl">2</span>
      </div>
      <h3 className="text-2xl mt-4 font-semibold text-white">AI-Powered Recommendations</h3>
      <p className="text-gray-400 mt-2">Our AI will analyze your input and suggest the best parts for your needs.</p>
    </div>
    
    <div className="flex flex-col items-center">
      <div className="bg-pink-500 text-white p-4 rounded-full w-24 h-24 flex items-center justify-center">
        <span className="text-3xl">3</span>
      </div>
      <h3 className="text-2xl mt-4 font-semibold text-white">Finalize Your Build</h3>
      <p className="text-gray-400 mt-2">Choose your final build and get recommendations for where to buy the parts.</p>
    </div>
  </div>
</section>

<section className="py-16 bg-gray-800 text-center">
  <h2 className="text-4xl font-semibold text-white">Why Choose ByteMe?</h2>
  <p className="text-lg text-gray-400 mt-4 mb-8">Our AI provides personalized recommendations to help you build your perfect PC.</p>
  
  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
    <div className="p-8 bg-gray-700 rounded-xl shadow-md">
      <h3 className="text-2xl font-semibold text-blue-500">AI-Driven Precision</h3>
      <p className="mt-4 text-gray-300">Get the best PC parts based on real-time data and your specific requirements.</p>
    </div>
    
    <div className="p-8 bg-gray-700 rounded-xl shadow-md">
      <h3 className="text-2xl font-semibold text-purple-500">Optimized for Performance</h3>
      <p className="mt-4 text-gray-300">Build a machine that fits your exact needs, whether it's gaming, editing, or streaming.</p>
    </div>
    
    <div className="p-8 bg-gray-700 rounded-xl shadow-md">
      <h3 className="text-2xl font-semibold text-pink-500">Affordable Options</h3>
      <p className="mt-4 text-gray-300">Find builds that match your budget without compromising on quality.</p>
    </div>
  </div>
</section>

<section className="py-20 bg-gradient-to-r from-blue-800 to-pink-800 text-center text-white">
  <h2 className="text-3xl font-semibold">Ready to Build Your Dream PC?</h2>
  <p className="text-lg mt-4">Start now with ByteMe’s AI-powered PC builder to create the perfect machine for your needs.</p>
  <div className="mt-8">
    <Button className="bg-white text-blue-500 hover:bg-gray-800 px-6 py-3 rounded-lg text-lg">Get Started</Button>
  </div>
</section>



</div>
  )
}
