"use client";

import { useState } from "react";
import { Breadcrumb, BreadcrumbItem, BreadcrumbLink, BreadcrumbList, BreadcrumbPage, BreadcrumbSeparator } from "@/components/ui/breadcrumb";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { Separator } from "@/components/ui/separator";
import { Rocket, Info, Search } from "lucide-react";

export default function Build() {
  const [budget, setBudget] = useState(1500); // Default budget

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Breadcrumb Navigation */}
      <BreadcrumbList>
        <BreadcrumbItem>
          <BreadcrumbLink href="/">Home</BreadcrumbLink>
        </BreadcrumbItem>
        <BreadcrumbSeparator />
        <BreadcrumbItem>
          <BreadcrumbPage>Build Your PC</BreadcrumbPage>
        </BreadcrumbItem>
      </BreadcrumbList>

      <Separator className="my-4" />

      {/* 🔥 Hero Section */}
      <Card className="bg-gradient-to-r from-blue-600 to-blue-400 text-white shadow-lg">
        <CardHeader className="flex flex-col sm:flex-row items-center gap-4">
          <Rocket className="w-12 h-12" />
          <div>
            <CardTitle>Find the Perfect Parts for Your PC!</CardTitle>
            <CardDescription className="text-white/80">
              Get AI-powered recommendations tailored to your budget and needs.
            </CardDescription>
          </div>
        </CardHeader>
        <CardContent className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <h2 className="font-medium text-lg">Find parts by PC</h2>
            <div className="relative">
              <Input type="text" placeholder="Enter your PC model..." />
              <Search className="absolute right-3 top-2.5 text-gray-400" />
            </div>
          </div>
          <div>
            <h2 className="font-medium text-lg">Find specific parts</h2>
            <div className="relative">
              <Input type="text" placeholder="Enter part name..." />
              <Search className="absolute right-3 top-2.5 text-gray-400" />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 🛠️ New to PC Building? */}
      <Card className="bg-gradient-to-r from-pink-700 to-pink-500 text-white shadow-lg">
        <CardContent className="flex flex-col sm:flex-row justify-between items-center p-6">
          <div className="flex items-center gap-3">
            <Info className="w-10 h-10" />
            <span className="text-lg font-medium">
              New to PC building? Let us guide you step by step!
            </span>
          </div>
          <Button className="bg-green-600 hover:bg-green-500 mt-4 sm:mt-0">Get Help</Button>
        </CardContent>
      </Card>

      {/* 📋 Requirements Section */}
      <Card className="bg-gradient-to-r from-purple-700 to-purple-500 text-white shadow-lg">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <span>Requirements</span>
          </CardTitle>
          <CardDescription className="text-white/80">
            Customize your build with specific preferences.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form className="space-y-6">
            {/* 🎚️ Budget Slider */}
            <div>
              <label htmlFor="budget_slider" className="block text-lg font-medium">
                Budget: <span className="text-yellow-300">${budget}</span>
              </label>
              <Slider
                id="budget_slider"
                min={0}
                max={10000}
                step={50}
                defaultValue={[budget]}
                onValueChange={(value) => setBudget(value[0])}
              />
            </div>

            {/* 🔍 AI Prompt */}
            <div>
              <label htmlFor="ai_prompt" className="block text-lg font-medium">
                Describe Your Needs
              </label>
              <Input id="ai_prompt" type="text" placeholder="Ex: I need a gaming PC under $2000" required />
            </div>

            {/* 🚀 Submit Button */}
            <Button type="submit" className="w-full bg-green-600 hover:bg-green-500">
              Find My PC Parts
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
