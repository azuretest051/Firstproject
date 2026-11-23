import type { RecommendPrefs, RecommendationItem } from "@/lib/types";
import { Icon } from "../Icon";

type Props = {
  prefs: RecommendPrefs;
  recommendations: RecommendationItem[];
};

export function ResultsSidebar({ prefs, recommendations }: Props) {
  const flavor = prefs.cuisine ? 96 : 80;
  const budget =
    ({ low: 88, medium: 94, high: 90 } as Record<string, number>)[
      String(prefs.budget || "medium").toLowerCase()
    ] || 90;
  const atmosphere = prefs.additional_preferences ? 91 : 84;
  const distance = 88;

  const positions = [
    ["35%", "45%"],
    ["50%", "25%"],
    ["65%", "70%"],
    ["20%", "60%"],
  ];

  const metrics = [
    {
      label: "Flavor Alignment (Spices & Tandoor)",
      value: flavor,
      bar: "from-secondary-container to-primary-container",
      valueClass: "text-primary-container",
    },
    {
      label: `Budget Fit (${prefs.budget})`,
      value: budget,
      bar: "from-secondary to-secondary-container",
      valueClass: "text-secondary",
    },
    {
      label: "Atmosphere Match",
      value: atmosphere,
      bar: "bg-primary/70",
      valueClass: "text-on-surface-variant",
      plain: true,
    },
    {
      label: "Distance Proximity (<3.5 km)",
      value: distance,
      bar: "bg-primary/50",
      valueClass: "text-on-surface-variant",
      plain: true,
    },
  ];

  return (
    <aside
      aria-label="Geographic & Algorithmic Insights"
      className="w-full lg:w-[32%] flex flex-col gap-space-md"
    >
      <div className="rounded-xl bg-surface-container-low overflow-hidden shadow-lg">
        <div className="p-space-sm bg-surface-container flex items-center justify-between">
          <div className="flex items-center gap-1.5">
            <Icon name="map" className="text-primary-container text-[18px]" />
            <span className="text-label-lg text-on-surface font-bold">
              {prefs.location || "Metro"} Heatmap
            </span>
          </div>
          <span className="px-2 py-0.5 rounded-full bg-surface-container-highest text-secondary text-label-sm font-semibold">
            Live Density
          </span>
        </div>
        <div className="relative w-full h-56 bg-surface-container-lowest">
          <div
            className="w-full h-full bg-cover bg-center"
            style={{
              backgroundImage:
                "url('https://lh3.googleusercontent.com/aida-public/AB6AXuCe4cxFVYLgjMlHKXwzqJwi3tUO34ypU4gIjwOL2M5Otxmgjq87KE9yW-OffRa41fl6WD8eATq2aO6DI1nmY6ugdohe8RhvSSxRChH5c8M3dT5zRoOeeDO4lRGIY-DPqyk7WnUwthQ_8pNOUtJrElSVwLvkxpxuswUClBoJIlnPG-qkFAdvzKU9W9i4nC76reLtqs8zveGMiObdwzrqiQVNb8QEXJbO-ei9ozQwfl8')",
            }}
          />
          {recommendations.slice(0, 4).map((item, i) => {
            const [top, left] = positions[i] || ["40%", "50%"];
            return (
              <div
                key={`${item.restaurant_name}-${i}`}
                className="absolute -translate-x-1/2 -translate-y-1/2 cursor-pointer"
                style={{ top, left }}
              >
                <div
                  className={
                    i === 0
                      ? "w-7 h-7 rounded-full bg-primary-container text-on-primary-container text-label-sm font-extrabold flex items-center justify-center shadow-lg"
                      : "w-6 h-6 rounded-full bg-surface-container-highest text-primary text-label-sm font-extrabold flex items-center justify-center shadow-lg"
                  }
                >
                  {i + 1}
                </div>
              </div>
            );
          })}
          <div className="absolute bottom-2 right-2 px-2 py-1 rounded bg-surface-container-lowest/90 backdrop-blur-sm text-on-surface-variant text-label-sm flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-primary-container" />
            <span>Geo-Ranked Hubs</span>
          </div>
        </div>
        <div className="p-space-sm bg-surface-container-low flex items-center justify-between">
          <span className="text-body-sm text-on-surface-variant">
            Cluster: curated matches
          </span>
          <span className="text-label-sm text-primary font-semibold flex items-center gap-0.5">
            Expand Full Map
            <Icon name="open_in_new" className="text-[14px]" />
          </span>
        </div>
      </div>

      <div className="p-space-md rounded-xl bg-surface-container-low shadow-md flex flex-col gap-space-sm">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5">
            <Icon name="radar" className="text-secondary text-[20px]" />
            <h4 className="text-headline-sm text-on-surface">AI Palate Breakdown</h4>
          </div>
          <span className="text-label-sm text-on-surface-variant font-mono">
            v4.2 METRIC
          </span>
        </div>
        <p className="text-body-sm text-on-surface-variant">
          Aggregated neural affinity weight for your active search profile:
        </p>
        <div className="flex flex-col gap-2.5 pt-1">
          {metrics.map((metric) => (
            <div key={metric.label} className="flex flex-col gap-1">
              <div className="flex justify-between text-label-sm">
                <span className="text-on-surface font-semibold">{metric.label}</span>
                <span className={`${metric.valueClass} font-bold font-mono`}>
                  {metric.value}%
                </span>
              </div>
              <div className="h-2 w-full bg-surface-container rounded-full overflow-hidden">
                <div
                  className={
                    metric.plain
                      ? `h-full ${metric.bar} rounded-full`
                      : `h-full bg-gradient-to-r ${metric.bar} rounded-full`
                  }
                  style={{ width: `${metric.value}%` }}
                />
              </div>
            </div>
          ))}
        </div>
        <div className="mt-2 p-space-sm rounded-lg bg-surface-container flex items-center gap-space-sm">
          <svg
            className="w-12 h-12 text-primary shrink-0"
            fill="none"
            viewBox="0 0 100 100"
            xmlns="http://www.w3.org/2000/svg"
          >
            <circle
              cx="50"
              cy="50"
              r="45"
              stroke="currentColor"
              strokeOpacity="0.2"
              strokeWidth="2"
            />
            <circle
              cx="50"
              cy="50"
              r="30"
              stroke="currentColor"
              strokeOpacity="0.3"
              strokeWidth="2"
            />
            <circle
              cx="50"
              cy="50"
              r="15"
              stroke="currentColor"
              strokeOpacity="0.4"
              strokeWidth="2"
            />
            <polygon
              fill="rgba(255, 107, 74, 0.35)"
              points="50,12 85,42 78,82 22,80 18,38"
              stroke="#ff6b4a"
              strokeWidth="2"
            />
          </svg>
          <div className="flex flex-col">
            <span className="text-label-sm text-on-surface font-bold">
              Multi-Parametric Score
            </span>
            <span className="text-body-sm text-on-surface-variant">
              Cross-matched against Bangalore diner histories.
            </span>
          </div>
        </div>
      </div>

      <div className="p-space-sm rounded-lg bg-surface-container-low/60 flex items-start gap-2">
        <Icon name="help" className="text-[16px] text-primary-container mt-0.5" />
        <p className="text-body-sm text-on-surface-variant">
          Scores dynamically adjust as diners review live evening wait times and
          kitchen consistency on weekdays.
        </p>
      </div>
    </aside>
  );
}
