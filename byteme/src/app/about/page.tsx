// app/about/page.tsx
import { Card, CardHeader, CardContent } from "@/components/ui/card"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Linkedin, Github } from "lucide-react"

const teamMembers = [
  {
    name: "Qian Chen",
    role: "AI Architect",
    bio: "Designed the Ollama integration and prompt engineering system. Specializes in optimizing AI responses for hardware recommendations.",
    avatar: "/team/qian.jpg",
    linkedin: "#",
    github: "#"
  },
  {
    name: "Yan Hui",
    role: "Backend Engineer",
    bio: "Built the Kong API gateway and microservices architecture. Ensures seamless communication between all system components.",
    avatar: "/team/yan.jpg",
    linkedin: "#",
    github: "#"
  },
  {
    name: "Chun Yik",
    role: "Frontend Lead",
    bio: "Created the interactive PC builder interface with React and Tailwind. Focuses on delivering an intuitive user experience.",
    avatar: "/team/chunyik.jpg",
    linkedin: "#",
    github: "#"
  },
  {
    name: "Jonathan",
    role: "Systems Integrator",
    bio: "Orchestrated the Docker deployment and cloud infrastructure. Makes sure everything runs smoothly in production.",
    avatar: "/team/jonathan.jpg",
    linkedin: "#",
    github: "#"
  },
  {
    name: "Benjamin",
    role: "Product Manager",
    bio: "Coordinates feature development and user testing. Bridges the gap between technical and business requirements.",
    avatar: "/team/benjamin.jpg",
    linkedin: "#",
    github: "#"
  }
]

export default function AboutPage() {
  return (
    <div className="container mx-auto px-4 py-12">
      <section className="text-center mb-16">
        <h1 className="text-4xl font-bold tracking-tight mb-4 bg-gradient-to-r from-primary to-blue-600 bg-clip-text text-transparent">
          The ByteMe Team
        </h1>
        <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
          We're revolutionizing PC building with AI-powered recommendations and real-time inventory.
        </p>
      </section>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {teamMembers.map((member) => (
          <Card key={member.name} className="hover:shadow-lg transition-all duration-300">
            <CardHeader className="items-center">
              <Avatar className="w-24 h-24 mb-4">
                <AvatarImage src={member.avatar} />
                <AvatarFallback className="text-2xl">
                  {member.name.split(' ').map(n => n[0]).join('')}
                </AvatarFallback>
              </Avatar>
              <div className="text-center">
                <h3 className="text-xl font-semibold">{member.name}</h3>
                <p className="text-primary">{member.role}</p>
              </div>
            </CardHeader>
            <CardContent className="text-center">
              <p className="text-muted-foreground mb-4">{member.bio}</p>
              <div className="flex justify-center space-x-4">
                <a 
                  href={member.linkedin} 
                  className="text-blue-600 hover:text-blue-800 transition-colors"
                  aria-label={`${member.name}'s LinkedIn`}
                >
                  <Linkedin className="w-5 h-5" />
                </a>
                <a 
                  href={member.github} 
                  className="text-gray-700 hover:text-black transition-colors"
                  aria-label={`${member.name}'s GitHub`}
                >
                  <Github className="w-5 h-5" />
                </a>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <section className="mt-16 text-center">
        <h2 className="text-2xl font-semibold mb-6">Our Mission</h2>
        <div className="max-w-4xl mx-auto bg-gradient-to-br from-secondary/20 to-primary/10 p-8 rounded-xl">
          <p className="text-lg">
            At ByteMe, we combine cutting-edge AI with comprehensive hardware knowledge to simplify PC building. 
            Our system cross-references real-time inventory with performance benchmarks to recommend 
            the perfect components for every need and budget.
          </p>
        </div>
      </section>
    </div>
  )
}