'use client';
import { useState, useRef, useEffect } from 'react';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import { Avatar, AvatarFallback, AvatarImage } from './ui/avatar';
import { Card, CardHeader, CardContent, CardFooter } from './ui/card';

type Message = {
  role: 'user' | 'assistant';
  content: string;
  components?: PCComponent[]; // Optional components data for rich responses
};

type PCComponent = {
  Id: number;
  Name: string;
  Price: number;
  Stock: number;
  ImageUrl: string;
  CategoryId: number;
};

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [components, setComponents] = useState<PCComponent[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Fetch components from OutSystems API on component mount
  useEffect(() => {
    const fetchComponents = async () => {
      try {
        const response = await fetch('http://localhost:8000/components');
        if (!response.ok) throw new Error('Failed to fetch components');
        const data = await response.json();
        setComponents(data);
      } catch (error) {
        console.error('Error fetching components:', error);
      }
    };

    fetchComponents();
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const generateResponse = (userInput: string): { response: string; relevantComponents?: PCComponent[] } => {
    const lowerInput = userInput.toLowerCase();
    let response = "I'm not sure how to help with that. Could you be more specific?";
    let relevantComponents: PCComponent[] = [];

    // Check for component categories
    if (lowerInput.includes('cpu') || lowerInput.includes('processor')) {
      relevantComponents = components.filter(c => c.CategoryId === 1);
      response = "Here are some available CPUs:";
    } else if (lowerInput.includes('gpu') || lowerInput.includes('graphics') || lowerInput.includes('video card')) {
      relevantComponents = components.filter(c => c.CategoryId === 2);
      response = "Here are some available GPUs:";
    } else if (lowerInput.includes('motherboard') || lowerInput.includes('mobo')) {
      relevantComponents = components.filter(c => c.CategoryId === 3);
      response = "Here are some available motherboards:";
    } else if (lowerInput.includes('ram') || lowerInput.includes('memory')) {
      relevantComponents = components.filter(c => c.CategoryId === 4);
      response = "Here are some available RAM kits:";
    } else if (lowerInput.includes('ssd') || lowerInput.includes('storage') || lowerInput.includes('hard drive')) {
      relevantComponents = components.filter(c => c.CategoryId === 5);
      response = "Here are some available storage options:";
    } else if (lowerInput.includes('case') || lowerInput.includes('casing')) {
      relevantComponents = components.filter(c => c.CategoryId === 6);
      response = "Here are some available PC cases:";
    } else if (lowerInput.includes('psu') || lowerInput.includes('power supply')) {
      relevantComponents = components.filter(c => c.CategoryId === 7);
      response = "Here are some available power supplies:";
    } else if (lowerInput.includes('cooler') || lowerInput.includes('aio')) {
      relevantComponents = components.filter(c => c.CategoryId === 8);
      response = "Here are some available cooling solutions:";
    } else if (lowerInput.includes('build') || lowerInput.includes('recommend')) {
      // For build recommendations, we'll pick components from each category
      response = "Here's a balanced PC build recommendation:";
      relevantComponents = [
        components.find(c => c.CategoryId === 1 && c.Price < 500) || components.find(c => c.CategoryId === 1)!,
        components.find(c => c.CategoryId === 2 && c.Price < 800) || components.find(c => c.CategoryId === 2)!,
        components.find(c => c.CategoryId === 3 && c.Price < 300) || components.find(c => c.CategoryId === 3)!,
        components.find(c => c.CategoryId === 4 && c.Price < 200) || components.find(c => c.CategoryId === 4)!,
        components.find(c => c.CategoryId === 5 && c.Price < 200) || components.find(c => c.CategoryId === 5)!,
        components.find(c => c.CategoryId === 6 && c.Price < 150) || components.find(c => c.CategoryId === 6)!,
        components.find(c => c.CategoryId === 7 && c.Price < 150) || components.find(c => c.CategoryId === 7)!,
      ];
    }

    return { response, relevantComponents };
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // First check if we can generate a response locally with components data
      const { response, relevantComponents } = generateResponse(input);
      
      // If we found relevant components, use them
      if (relevantComponents && relevantComponents.length > 0) {
        setMessages(prev => [...prev, { 
          role: 'assistant', 
          content: response,
          components: relevantComponents 
        }]);
      } else {
        // Fall back to the AI API if we don't have a local response
        const apiResponse = await fetch('http://localhost:8000/ai/api/generate', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            model: 'deepseek-r1',
            prompt: input,
            stream: false,
          }),
        });

        if (!apiResponse.ok) throw new Error('Network response was not ok');
        
        const data = await apiResponse.json();
        setMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
      }
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'Sorry, I encountered an error. Please try again.' 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(price);
  };

  return (
    <Card className="w-full max-w-3xl mx-auto h-[600px] flex flex-col">
      <CardHeader className="border-b">
        <h2 className="text-xl font-semibold">PC Builder Assistant</h2>
      </CardHeader>
      
      <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full text-gray-500">
            Ask me about PC builds, components, or recommendations
          </div>
        ) : (
          messages.map((message, index) => (
            <div 
              key={index} 
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`max-w-[80%] rounded-lg p-3 ${message.role === 'user' 
                ? 'bg-primary text-primary-foreground' 
                : 'bg-muted'}`}
              >
                <div className="flex items-center gap-2 mb-1">
                  <Avatar className="h-6 w-6">
                    <AvatarImage 
                      src={message.role === 'user' ? '' : '/ai-avatar.png'} 
                    />
                    <AvatarFallback>
                      {message.role === 'user' ? 'U' : 'AI'}
                    </AvatarFallback>
                  </Avatar>
                  <span className="text-sm font-medium">
                    {message.role === 'user' ? 'You' : 'Assistant'}
                  </span>
                </div>
                <p className="whitespace-pre-wrap mb-2">{message.content}</p>
                
                {/* Display components if available */}
                {message.components && message.components.length > 0 && (
                  <div className="mt-2 space-y-3">
                    {message.components.map(component => (
                      <div key={component.Id} className="flex gap-3 p-2 bg-white/10 rounded">
                        {component.ImageUrl && (
                          <img 
                            src={component.ImageUrl} 
                            alt={component.Name}
                            className="w-16 h-16 object-contain rounded"
                          />
                        )}
                        <div>
                          <h4 className="font-medium">{component.Name}</h4>
                          <p className="text-sm">{formatPrice(component.Price)}</p>
                          <p className="text-xs text-muted-foreground">
                            {component.Stock > 0 ? `${component.Stock} in stock` : 'Out of stock'}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </CardContent>

      <CardFooter className="border-t p-4">
        <form onSubmit={handleSubmit} className="flex w-full gap-2">
          <Textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your PC building question..."
            className="flex-1"
            disabled={isLoading}
          />
          <Button type="submit" disabled={isLoading || !input.trim()}>
            {isLoading ? 'Thinking...' : 'Send'}
          </Button>
        </form>
      </CardFooter>
    </Card>
  );
}