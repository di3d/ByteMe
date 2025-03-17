/**
 * Sample PC build data for testing the checkout flow
 * This provides structured data to be used in the checkout process
 */

export interface PCComponent {
  id: string;
  name: string;
  price: number; // Price in cents
  category: string;
  description?: string;
  image?: string;
}

export interface PCBuild {
  id: string;
  name: string;
  description: string;
  orderId: string;
  items: PCComponent[];
  timestamp: number;
}

// Sample PC builds with individual part pricing
export const samplePCBuilds: PCBuild[] = [
  {
    id: 'gaming-pc',
    name: 'Ultimate Gaming PC',
    description: 'High-performance gaming PC with RTX 3070 GPU',
    orderId: `ORD-GAMING-${Date.now()}`,
    items: [
      { 
        id: 'cpu-001', 
        name: 'AMD Ryzen 7 5800X CPU', 
        price: 29900, 
        category: 'CPU',
        description: '8-core, 16-thread processor for high-performance gaming'
      },
      { 
        id: 'gpu-001', 
        name: 'NVIDIA RTX 3070 GPU', 
        price: 79900, 
        category: 'GPU',
        description: '8GB GDDR6 graphics card for maximum gaming performance'
      },
      { 
        id: 'mb-001', 
        name: 'ASUS ROG Strix B550-F Gaming Motherboard', 
        price: 24900, 
        category: 'Motherboard',
        description: 'ATX motherboard with PCIe 4.0 support and robust power delivery'
      },
      { 
        id: 'ram-001', 
        name: 'Corsair Vengeance RGB 32GB (2x16GB) DDR4-3600', 
        price: 19900, 
        category: 'RAM',
        description: 'High-performance memory with RGB lighting'
      },
      { 
        id: 'storage-001', 
        name: 'Samsung 970 EVO Plus 1TB NVMe SSD', 
        price: 14900, 
        category: 'Storage',
        description: 'Ultra-fast NVMe SSD for rapid boot and load times'
      },
      { 
        id: 'psu-001', 
        name: 'Corsair RM750x 750W Power Supply', 
        price: 12900, 
        category: 'Power Supply',
        description: 'Gold-rated fully modular power supply'
      },
      { 
        id: 'case-001', 
        name: 'Fractal Design Meshify C Case', 
        price: 9900, 
        category: 'Case',
        description: 'Mid-tower case with excellent airflow'
      },
      { 
        id: 'cooling-001', 
        name: 'NZXT Kraken X63 280mm AIO CPU Cooler', 
        price: 7900, 
        category: 'Cooling',
        description: 'Liquid cooling solution for optimal CPU temperatures'
      }
    ],
    timestamp: Date.now()
  },
  {
    id: 'budget-pc',
    name: 'Budget Friendly Gaming PC',
    description: 'Great performance at an affordable price',
    orderId: `ORD-BUDGET-${Date.now()}`,
    items: [
      { 
        id: 'cpu-002', 
        name: 'AMD Ryzen 5 5600X CPU', 
        price: 19900, 
        category: 'CPU',
        description: '6-core, 12-thread processor with excellent gaming performance'
      },
      { 
        id: 'gpu-002', 
        name: 'NVIDIA RTX 3060 GPU', 
        price: 39900, 
        category: 'GPU',
        description: '12GB GDDR6 graphics card for 1080p gaming'
      },
      { 
        id: 'mb-002', 
        name: 'MSI B550M PRO-VDH WiFi Motherboard', 
        price: 10900, 
        category: 'Motherboard',
        description: 'Micro-ATX motherboard with built-in WiFi'
      },
      { 
        id: 'ram-002', 
        name: 'Crucial Ballistix 16GB (2x8GB) DDR4-3200', 
        price: 8900, 
        category: 'RAM',
        description: 'Reliable memory kit with good performance'
      },
      { 
        id: 'storage-002', 
        name: 'WD Blue SN550 500GB NVMe SSD', 
        price: 6900, 
        category: 'Storage',
        description: 'Affordable NVMe SSD for fast system performance'
      },
      { 
        id: 'psu-002', 
        name: 'EVGA 600W 80+ Bronze Power Supply', 
        price: 5900, 
        category: 'Power Supply',
        description: 'Reliable power supply for mid-range builds'
      },
      { 
        id: 'case-002', 
        name: 'Phanteks P300 ATX Mid Tower Case', 
        price: 4900, 
        category: 'Case',
        description: 'Affordable case with good cable management'
      },
      { 
        id: 'cooling-002', 
        name: 'Cooler Master Hyper 212 RGB CPU Cooler', 
        price: 2900, 
        category: 'Cooling',
        description: 'Air cooler with RGB lighting'
      }
    ],
    timestamp: Date.now()
  },
  {
    id: 'pro-workstation',
    name: 'Professional Workstation',
    description: 'High-end workstation for content creators and professionals',
    orderId: `ORD-PRO-${Date.now()}`,
    items: [
      { 
        id: 'cpu-003', 
        name: 'AMD Ryzen 9 5950X CPU', 
        price: 79900, 
        category: 'CPU',
        description: '16-core, 32-thread processor for professional workloads'
      },
      { 
        id: 'gpu-003', 
        name: 'NVIDIA RTX 3090 GPU', 
        price: 199900, 
        category: 'GPU',
        description: '24GB GDDR6X for 3D rendering and professional work'
      },
      { 
        id: 'mb-003', 
        name: 'ASUS ROG X570 Crosshair VIII Hero Motherboard', 
        price: 49900, 
        category: 'Motherboard',
        description: 'High-end ATX motherboard with premium features'
      },
      { 
        id: 'ram-003', 
        name: 'G.Skill Trident Z RGB 64GB (4x16GB) DDR4-3600', 
        price: 59900, 
        category: 'RAM',
        description: 'High-capacity memory kit for content creation'
      },
      { 
        id: 'storage-003', 
        name: 'Samsung 980 PRO 2TB NVMe SSD', 
        price: 39900, 
        category: 'Storage',
        description: 'Ultra-fast PCIe 4.0 SSD for professional workloads'
      },
      { 
        id: 'psu-003', 
        name: 'Corsair AX1000 Titanium Power Supply', 
        price: 29900, 
        category: 'Power Supply',
        description: 'Titanium-rated 1000W power supply for high-end systems'
      },
      { 
        id: 'case-003', 
        name: 'Lian Li O11 Dynamic XL Case', 
        price: 19900, 
        category: 'Case',
        description: 'Premium case with excellent cooling options'
      },
      { 
        id: 'cooling-003', 
        name: 'Corsair iCUE H150i Elite Capellix 360mm AIO', 
        price: 19900, 
        category: 'Cooling',
        description: 'High-end 360mm liquid cooling solution'
      }
    ],
    timestamp: Date.now()
  },
  {
    id: 'streaming-pc',
    name: 'Streaming PC',
    description: 'Optimized for gaming and streaming simultaneously',
    orderId: `ORD-STREAM-${Date.now()}`,
    items: [
      { 
        id: 'cpu-004', 
        name: 'AMD Ryzen 9 5900X CPU', 
        price: 54900, 
        category: 'CPU',
        description: '12-core, 24-thread processor for streaming and gaming'
      },
      { 
        id: 'gpu-004', 
        name: 'NVIDIA RTX 3080 GPU', 
        price: 99900, 
        category: 'GPU',
        description: '10GB GDDR6X for high-fps gaming while streaming'
      },
      { 
        id: 'mb-004', 
        name: 'MSI MPG X570 Gaming Edge WiFi Motherboard', 
        price: 29900, 
        category: 'Motherboard',
        description: 'Feature-rich motherboard with excellent connectivity'
      },
      { 
        id: 'ram-004', 
        name: 'G.Skill Ripjaws V 32GB (2x16GB) DDR4-3600', 
        price: 19900, 
        category: 'RAM',
        description: 'High-capacity memory for streaming workloads'
      },
      { 
        id: 'storage-004', 
        name: 'Western Digital Black SN850 1TB NVMe SSD', 
        price: 18900, 
        category: 'Storage',
        description: 'High-performance Gen4 SSD for quick load times'
      },
      { 
        id: 'storage-add-004', 
        name: 'Seagate Barracuda 4TB HDD', 
        price: 9900, 
        category: 'Storage',
        description: 'Additional storage for recordings and media files'
      },
      { 
        id: 'psu-004', 
        name: 'EVGA SuperNOVA 850W G5 Power Supply', 
        price: 15900, 
        category: 'Power Supply',
        description: 'Gold-rated power supply with ample wattage for upgrades'
      },
      { 
        id: 'case-004', 
        name: 'Corsair 4000D Airflow Case', 
        price: 9900, 
        category: 'Case',
        description: 'Mid-tower case with excellent airflow design'
      },
      { 
        id: 'cooling-004', 
        name: 'be quiet! Dark Rock Pro 4 CPU Cooler', 
        price: 8900, 
        category: 'Cooling',
        description: 'Silent and effective air cooling solution'
      },
      { 
        id: 'capture-004', 
        name: 'Elgato HD60 S+ Capture Card', 
        price: 19900, 
        category: 'Accessories',
        description: 'For console streaming and multi-PC setups'
      }
    ],
    timestamp: Date.now()
  }
];

// Helper function to calculate the total amount of a PC build
export function calculateBuildTotal(build: PCBuild): number {
  return build.items.reduce((total, item) => total + item.price, 0);
}

// Helper function to get a build by ID
export function getBuildById(id: string): PCBuild | undefined {
  return samplePCBuilds.find(build => build.id === id);
}
