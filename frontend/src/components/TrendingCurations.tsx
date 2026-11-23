import { Icon } from "./Icon";

const CARDS = [
  {
    title: "The Charcoal Atelier",
    subtitle: "Wood-Fired Progressive Grill & Ferment Bar",
    affinity: "97% Taste Affinity",
    rating: "4.9",
    place: "Indiranagar, 100ft Rd",
    cost: "₹2,800 for two",
    why: "Matched for your affinity toward smoky sourdough notes and charred umami reduction with intimate counter vibes.",
    tags: ["Smoked Butter Crudo", "Artisanal Brioche", "Smoky Mezcal Sour"],
    image:
      "https://lh3.googleusercontent.com/aida-public/AB6AXuDFdX9Uk8X3WdSeo4HMPplhW4PNEBPBlcK6O6Mxfl-Pt6fsVaPR0-ff26hNwDKm1avKb1V_PabkCgUiezhkBCjxUwceVujnEuMKrW2hgZqN33ljXADhB9CSokNeoOBCdQ50ClS-crDBLCMn8_3NESm13LuL-Maf6lC5ohAJO0ExYHWse9KpipWa1j0ooRE0KkZSN7yqY6nM6gmuA_Pi6rFNoeM9pOFak-kJA6ZvPdU",
    featured: true,
  },
  {
    title: "The Permit Room",
    subtitle: "Modern South Indian & Botanical Mixology",
    affinity: "95% Taste Affinity",
    rating: "4.7",
    place: "Koramangala, 5th Block",
    cost: "₹1,900 for two",
    why: "Fits your high spicy-tangy balance preference and outdoor breeze criteria; top marks for ghee roasts & spiced gin.",
    tags: ["Pandi Fry", "Gunpowder Prawns", "Curry Leaf Gin"],
    image:
      "https://lh3.googleusercontent.com/aida-public/AB6AXuC65oG4x5Tr3attArzZBlSPn7MIwJA-CWmJjue96q4lQcL1cQSFABtVwK-vSNgCUw4QDXH2iorISyqvKJsfdiuCMt6-QBkzy85b9ujnT-xBE58q8GEOz_j3Ie5UCkz4oXY_e4FfvXqVfPecbwkaMBAWv0Lo0xVo3SboVe5LrwCfd971vzAmOvcmghYgdj8OuS9oYF-XFrAEUxNtUJTN3OGu3uRao5020R3O_BTGf_Q",
    accent: "secondary" as const,
  },
  {
    title: "Meghana Reserve",
    subtitle: "Slow-Cooked Dum & Hyderabadi Heritage",
    affinity: "92% Taste Affinity",
    rating: "4.8",
    place: "Lavelle Road, Central",
    cost: "₹1,600 for two",
    why: "High heat-tolerance alignment: heavy star anise, mace infusions, and hand-ground green chilli profiles rated #1 by your cohort.",
    tags: ["Special Dum Biryani", "Mutton Ghee Chukka", "Mirchi Ka Salan"],
    image:
      "https://lh3.googleusercontent.com/aida-public/AB6AXuDqyU6sbfgm1Rnix4RKn0ySGnhXq-TLs3Xbt7oEX-ZsJigI4UyZV4tx1T8lbgZw0mbzoOb-jF7bA2E-jFDmrDeyvGl6vfYe_3UEc9u2NGDP-ewJMbOuQ1KtNyOeidzXlEQtqMysn51lCxegRBrSIT3ApMliVwpuQtsDNv69n-IVCX4JdqkOxmJzfhHCWypDl1x-uSktiNqeHekVZwowzcTWWqYJ1_a9pwbzx5odaIU",
  },
];

export function TrendingCurations() {
  return (
    <section className="flex flex-col gap-space-lg pt-4 pb-12">
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-space-xs">
        <div>
          <div className="flex items-center gap-2">
            <Icon name="local_fire_department" className="text-primary-container text-[20px]" />
            <span className="text-label-sm text-primary uppercase tracking-widest">
              Sensory Radar
            </span>
          </div>
          <h2 className="text-headline-lg text-on-surface tracking-tight mt-1">
            Trending Curations In Bangalore
          </h2>
        </div>
        <span className="text-label-md text-primary-container flex items-center gap-1">
          Explore 140+ real-time neighborhood tables
          <Icon name="east" className="text-[16px]" />
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-space-lg">
        {CARDS.map((card, index) => (
          <article
            key={card.title}
            className={`flex flex-col rounded-2xl bg-surface-container overflow-hidden transition-all duration-300 hover:-translate-y-1.5 ring-1 group animate-fade-up ${
              card.featured
                ? "shadow-[0_4px_24px_-2px_rgba(255,107,74,0.15)] ring-primary-container/30"
                : "shadow-xl hover:shadow-[0_4px_24px_-2px_rgba(255,185,95,0.15)] ring-surface-container-highest"
            }`}
            style={{ animationDelay: `${0.08 * (index + 1)}s` }}
          >
            <div className="relative w-full h-52 overflow-hidden bg-surface-container-high">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                alt={card.title}
                src={card.image}
              />
              <div className="absolute inset-0 bg-gradient-to-t from-surface-container via-surface-container/20 to-transparent" />
              <div
                className={`absolute top-3 left-3 flex items-center gap-1.5 px-3 py-1 rounded-full bg-surface-container-lowest/80 backdrop-blur-md text-label-md font-bold border ${
                  card.accent === "secondary"
                    ? "text-secondary border-secondary/30"
                    : "text-primary border-primary-container/30"
                }`}
              >
                <Icon
                  name="local_fire_department"
                  className={`${
                    card.accent === "secondary" ? "text-secondary" : "text-primary-container"
                  } text-[16px]`}
                />
                <span>{card.affinity}</span>
              </div>
              <div className="absolute top-3 right-3 px-2.5 py-1 rounded-md bg-surface-container-lowest/80 backdrop-blur-md text-secondary text-label-sm font-bold flex items-center gap-1">
                <Icon name="star" className="text-[14px]" /> {card.rating}
              </div>
              <div className="absolute bottom-3 left-3 right-3 flex items-center justify-between text-on-surface-variant text-label-sm">
                <span className="flex items-center gap-1 text-on-surface font-semibold">
                  <Icon name="location_on" className="text-primary-container text-[14px]" />
                  {card.place}
                </span>
                <span className="text-secondary font-bold">{card.cost}</span>
              </div>
            </div>
            <div className="p-space-md flex flex-col gap-space-sm flex-1">
              <div>
                <h3 className="text-headline-sm text-on-surface font-bold group-hover:text-primary transition-colors">
                  {card.title}
                </h3>
                <p className="text-body-sm text-on-surface-variant mt-0.5">
                  {card.subtitle}
                </p>
              </div>
              <div
                className={`p-3 rounded-lg bg-surface-container-low border-l-2 flex flex-col gap-1 ${
                  card.accent === "secondary"
                    ? "border-secondary"
                    : "border-primary-container"
                }`}
              >
                <span
                  className={`text-[11px] uppercase tracking-wider font-bold flex items-center gap-1 ${
                    card.accent === "secondary" ? "text-secondary" : "text-primary"
                  }`}
                >
                  <Icon name="auto_awesome" className="text-[13px]" /> Why TasteMatch
                  Picked This
                </span>
                <p className="text-body-sm text-on-surface-variant">{card.why}</p>
              </div>
              <div className="flex flex-wrap gap-1.5 pt-1 mt-auto">
                {card.tags.map((tag) => (
                  <span
                    key={tag}
                    className="px-2 py-0.5 rounded bg-surface-container-high text-label-sm text-on-surface"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
