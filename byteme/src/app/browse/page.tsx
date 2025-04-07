import BuildCard from "@/components/BuildCard";

const info = [
    { label: "CPU", value: "Intel Core i7" },
    { label: "RAM", value: "16GB DDR5" },
    { label: "Storage", value: "1TB SSD" },
    { label: "GPU", value: "NVIDIA RTX 4070" },
    { label: "OS", value: "Windows 11 Pro" },
    { label: "Form Factor", value: "ATX Mid Tower" },
    { label: "Power Supply", value: "750W Gold" },
  ];

export default function Browse() {
  return (
    <div className="container mx-auto px-4 py-8  min-h-screen">
      <header>
        <div className="w-full bg-gradient-to-r from-blue-800 via-purple-800 to-pink-800 py-12 px-6 rounded-xl mb-8">
          <h1 className="text-4xl font-extrabold mb-4">Browse Systems</h1>
          <p className="text-lg">
          Discover user-submitted setups and ideas
          </p>
        </div>
      </header>
      <body>
        <BuildCard title="Bob's PC" infoRows={info} totalPrice={333}></BuildCard>
      </body>
    </div>
  );
}
