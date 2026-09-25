export interface VehicleBrand {
  brand: string
  models: string[]
}

export const POPULAR_VEHICLE_BRANDS: VehicleBrand[] = [
  {
    brand: "Abarth",
    models: ["500", "595", "695", "124 Spider", "600e", "Punto Evo"],
  },
  {
    brand: "Alfa Romeo",
    models: ["Giulietta", "Giulia", "Stelvio", "Tonale", "MiTo", "147", "156", "159", "Brera", "Junior", "4C", "GT"],
  },
  {
    brand: "Audi",
    models: ["A1", "A3", "A4", "A5", "A6", "A7", "A8", "Q2", "Q3", "Q4 e-tron", "Q5", "Q7", "Q8", "TT", "R8", "e-tron GT"],
  },
  {
    brand: "BMW",
    models: ["Serie 1", "Serie 2", "Serie 3", "Serie 4", "Serie 5", "Serie 6", "Serie 7", "Serie 8", "X1", "X2", "X3", "X4", "X5", "X6", "X7", "Z4", "i3", "i4", "iX1", "iX3", "iX"],
  },
  {
    brand: "Citroën",
    models: ["C1", "C3", "C3 Aircross", "C4", "C4 Cactus", "C4 X", "C5", "C5 Aircross", "C5 X", "Berlingo", "Ami", "Xsara Picasso"],
  },
  {
    brand: "Cupra",
    models: ["Formentor", "Leon", "Born", "Ateca", "Terramar", "Tavascan"],
  },
  {
    brand: "Dacia",
    models: ["Sandero", "Sandero Stepway", "Duster", "Jogger", "Spring", "Logan", "Dokker", "Lodgy"],
  },
  {
    brand: "DS Automobiles",
    models: ["DS 3", "DS 3 Crossback", "DS 4", "DS 7 Crossback", "DS 9"],
  },
  {
    brand: "Fiat",
    models: ["Panda", "500", "500X", "500L", "500e", "600", "Tipo", "Punto", "Grande Punto", "Punto Evo", "Bravo", "Sedici", "Qubo", "Doblò", "Freemont"],
  },
  {
    brand: "Ford",
    models: ["Fiesta", "Focus", "Puma", "Kuga", "EcoSport", "Mondeo", "C-Max", "S-Max", "B-Max", "Galaxy", "Ranger", "Mustang", "Mustang Mach-E", "Tourneo Courier"],
  },
  {
    brand: "Honda",
    models: ["Civic", "Jazz", "HR-V", "CR-V", "ZR-V", "e:Ny1", "e"],
  },
  {
    brand: "Hyundai",
    models: ["i10", "i20", "i30", "Bayon", "Kona", "Tucson", "Santa Fe", "Ioniq", "Ioniq 5", "Ioniq 6"],
  },
  {
    brand: "Jaguar",
    models: ["XE", "XF", "F-Pace", "E-Pace", "I-Pace", "F-Type"],
  },
  {
    brand: "Jeep",
    models: ["Renegade", "Compass", "Avenger", "Wrangler", "Cherokee", "Grand Cherokee", "Gladiator"],
  },
  {
    brand: "Kia",
    models: ["Picanto", "Rio", "Ceed", "ProCeed", "XCeed", "Stonic", "Niro", "Sportage", "Sorento", "EV3", "EV6", "EV9"],
  },
  {
    brand: "Lancia",
    models: ["Ypsilon", "Delta", "Musa", "Thema", "Phedra"],
  },
  {
    brand: "Land Rover",
    models: ["Defender", "Discovery", "Discovery Sport", "Range Rover", "Range Rover Sport", "Range Rover Velar", "Range Rover Evoque", "Freelander"],
  },
  {
    brand: "Lexus",
    models: ["LBX", "UX", "NX", "RX", "CT", "IS", "ES", "RZ"],
  },
  {
    brand: "Maserati",
    models: ["Ghibli", "Levante", "Grecale", "Quattroporte", "GranTurismo"],
  },
  {
    brand: "Mazda",
    models: ["Mazda2", "Mazda3", "Mazda6", "CX-3", "CX-30", "CX-5", "CX-60", "CX-80", "MX-5", "MX-30"],
  },
  {
    brand: "Mercedes-Benz",
    models: ["Classe A", "Classe B", "Classe C", "Classe E", "Classe S", "CLA", "CLS", "GLA", "GLB", "GLC", "GLE", "GLS", "EQA", "EQB", "EQC", "EQE", "EQS", "Citan"],
  },
  {
    brand: "MG",
    models: ["MG4", "MG ZS", "MG HS", "MG3", "Cyberster"],
  },
  {
    brand: "Mini",
    models: ["Cooper", "Cooper S", "One", "Countryman", "Clubman", "Paceman", "Aceman", "Cabrio"],
  },
  {
    brand: "Mitsubishi",
    models: ["Space Star", "Colt", "ASX", "Eclipse Cross", "Outlander", "Pajero"],
  },
  {
    brand: "Nissan",
    models: ["Micra", "Juke", "Qashqai", "X-Trail", "Leaf", "Ariya", "Navara", "Note"],
  },
  {
    brand: "Opel",
    models: ["Corsa", "Astra", "Mokka", "Crossland", "Grandland", "Insignia", "Adam", "Meriva", "Zafira", "Karl", "Combo"],
  },
  {
    brand: "Peugeot",
    models: ["108", "208", "2008", "308", "3008", "408", "508", "5008", "Rifter", "Partner", "207", "206"],
  },
  {
    brand: "Porsche",
    models: ["911", "718 Boxster", "718 Cayman", "Cayenne", "Macan", "Panamera", "Taycan"],
  },
  {
    brand: "Renault",
    models: ["Clio", "Captur", "Mégane", "Arkana", "Austral", "Symbioz", "Rafale", "Kadjar", "Twingo", "Scénic", "Espace", "Kangoo", "Zoe", "R5 E-Tech"],
  },
  {
    brand: "Seat",
    models: ["Ibiza", "Leon", "Arona", "Ateca", "Tarraco", "Mii", "Altea", "Toledo"],
  },
  {
    brand: "Škoda",
    models: ["Fabia", "Scala", "Kamiq", "Karoq", "Kodiaq", "Octavia", "Superb", "Enyaq"],
  },
  {
    brand: "Smart",
    models: ["Fortwo", "Forfour", "#1", "#3"],
  },
  {
    brand: "Subaru",
    models: ["Impreza", "XV", "Crosstrek", "Forester", "Outback", "Solterra"],
  },
  {
    brand: "Suzuki",
    models: ["Swift", "Ignis", "Vitara", "S-Cross", "Jimny", "Baleno", "Swace", "Across"],
  },
  {
    brand: "Tesla",
    models: ["Model 3", "Model Y", "Model S", "Model X", "Cybertruck"],
  },
  {
    brand: "Toyota",
    models: ["Yaris", "Yaris Cross", "Corolla", "C-HR", "RAV4", "Aygo", "Aygo X", "Prius", "Land Cruiser", "Hilux", "bZ4X", "Auris"],
  },
  {
    brand: "Volkswagen",
    models: ["Polo", "Golf", "T-Roc", "T-Cross", "Taigo", "Tiguan", "Touareg", "Passat", "Touran", "Up!", "ID.3", "ID.4", "ID.5", "ID.7", "Arteon", "Scirocco", "Caddy"],
  },
  {
    brand: "Volvo",
    models: ["EX30", "EX90", "XC40", "XC60", "XC90", "V40", "V60", "V90", "C40", "S60"],
  },
]

export const POPULAR_FUEL_TYPES = [
  "Benzina",
  "Diesel",
  "Ibrida (Mild / Full)",
  "Plug-in Hybrid",
  "Elettrica (BEV)",
  "GPL",
  "Metano",
  "Altro",
] as const

/**
 * Tenta di estrarre marca e modello da una stringa libera preesistente (es. "BMW Serie 1 (F20)")
 */
export function guessBrandAndModel(fullName: string): { brand: string; model: string; extra: string } {
  if (!fullName) return { brand: "", model: "", extra: "" }

  const trimmed = fullName.trim()
  
  for (const b of POPULAR_VEHICLE_BRANDS) {
    if (trimmed.toLowerCase().startsWith(b.brand.toLowerCase())) {
      const rest = trimmed.slice(b.brand.length).trim()
      // Cerca tra i modelli di questa marca
      for (const m of b.models) {
        if (rest.toLowerCase().startsWith(m.toLowerCase())) {
          const extra = rest.slice(m.length).trim()
          return {
            brand: b.brand,
            model: m,
            extra: extra.replace(/^[\s\-(]+|[\s\-)﻿]+$/g, "").trim(), // rimuove parentesi o trattini residui
          }
        }
      }
      return { brand: b.brand, model: "", extra: rest }
    }
  }

  return { brand: "", model: "", extra: trimmed }
}
