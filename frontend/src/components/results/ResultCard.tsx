import {
  PLACEHOLDER_IMAGES,
  cuisineTags,
  formatCost,
  tasteScore,
} from "@/lib/format";
import type { RecommendationItem } from "@/lib/types";
import { Icon } from "../Icon";

type Props = {
  item: RecommendationItem;
  index: number;
};

export function ResultCard({ item, index }: Props) {
  const rank = item.rank ?? index + 1;
  const score = tasteScore(rank);
  const tags = cuisineTags(item.cuisine);
  const cost = formatCost(item);
  const img = PLACEHOLDER_IMAGES[index % PLACEHOLDER_IMAGES.length];
  const isTop = Number(rank) === 1;

  return (
    <article
      className="relative rounded-xl bg-surface-container-low p-space-md shadow-md transition-all duration-300 hover:shadow-lg group animate-fade-up"
      style={{
        animationDelay: `${0.06 * index}s`,
        boxShadow: isTop
          ? "0 4px 24px -2px rgba(255, 107, 74, 0.12), 0 0 1px 1px rgba(255, 107, 74, 0.35)"
          : undefined,
      }}
    >
      <div className="flex items-center justify-between gap-2 mb-space-sm">
        <div className="flex items-center gap-2">
          <span
            className={
              isTop
                ? "px-2.5 py-1 rounded-md bg-primary-container text-on-primary-container text-label-sm uppercase font-extrabold tracking-wider flex items-center gap-1 shadow-sm"
                : "px-2.5 py-1 rounded-md bg-surface-container-high text-primary text-label-sm uppercase font-bold tracking-wider flex items-center gap-1"
            }
          >
            <Icon
              name={isTop ? "local_fire_department" : "insights"}
              className="text-[14px]"
            />
            #{rank} Match · {score}% Taste Score
          </span>
          {item.rating != null ? (
            <span className="px-2 py-0.5 rounded-md bg-surface-container-high text-secondary text-label-sm flex items-center gap-1 font-semibold">
              <Icon name="star" className="text-[13px]" filled />
              {item.rating}
            </span>
          ) : null}
        </div>
        {item.location ? (
          <div className="flex items-center gap-1 text-on-surface-variant text-label-sm">
            <Icon name="near_me" className="text-[16px] text-primary-container" />
            <span>{item.location}</span>
          </div>
        ) : null}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-space-md">
        <div className="md:col-span-5 relative rounded-lg overflow-hidden h-52 md:h-full min-h-[200px] bg-surface-container">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            alt={item.restaurant_name}
            className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
            src={img}
          />
          <div className="absolute inset-0 bg-gradient-to-t from-surface-container-lowest/90 via-transparent to-black/20" />
          {cost ? (
            <div className="absolute bottom-2 left-2 flex items-center gap-1.5 px-2 py-1 rounded bg-surface-container-lowest/80 backdrop-blur-md text-label-sm text-on-surface">
              <span className="w-2 h-2 rounded-full bg-secondary-container" />
              <span>{cost}</span>
            </div>
          ) : null}
        </div>

        <div className="md:col-span-7 flex flex-col justify-between gap-space-sm">
          <div>
            <h3 className="text-headline-md text-on-surface leading-tight tracking-tight">
              {item.restaurant_name || "Unknown restaurant"}
            </h3>
            <p className="text-body-sm text-on-surface-variant mt-0.5">
              {item.cuisine || "Recommended dining"}
            </p>
            <div className="flex flex-wrap items-center gap-1.5 mt-space-xs">
              {tags.length ? (
                tags.map((tag, i) => (
                  <span
                    key={tag}
                    className={`px-2 py-0.5 rounded bg-surface-container text-label-sm ${
                      i === 0
                        ? "text-primary font-semibold"
                        : "text-on-surface-variant"
                    }`}
                  >
                    {tag}
                  </span>
                ))
              ) : (
                <span className="px-2 py-0.5 rounded bg-surface-container text-on-surface-variant text-label-sm">
                  Curated pick
                </span>
              )}
            </div>
            <div className="mt-space-sm p-space-sm rounded-lg bg-surface-container flex items-start gap-2.5 relative overflow-hidden">
              <div className="w-1 absolute left-0 top-0 bottom-0 bg-primary-container" />
              <div className="pl-1 flex flex-col gap-0.5">
                <span className="text-label-sm font-bold text-primary-container uppercase tracking-wider flex items-center gap-1">
                  <Icon name="auto_awesome" className="text-[13px]" filled />
                  Why TasteMatch Picked This
                </span>
                <p className="text-body-sm text-on-surface leading-snug">
                  {item.explanation || "No explanation provided."}
                </p>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-space-sm pt-space-xs">
            <button
              className="flex-1 py-2 px-space-md rounded-lg bg-primary-container hover:bg-tertiary-container text-on-primary-container text-label-lg font-bold transition-all shadow-md flex items-center justify-center gap-1.5 cursor-pointer"
              type="button"
            >
              <Icon name="table_restaurant" className="text-[18px]" />
              <span>Book Table</span>
            </button>
            <button
              className="py-2 px-space-md rounded-lg bg-surface-container hover:bg-surface-container-high text-on-surface text-label-lg font-semibold transition-colors flex items-center gap-1 cursor-pointer"
              type="button"
            >
              <span>View details</span>
              <Icon name="arrow_outward" className="text-[16px]" />
            </button>
          </div>
        </div>
      </div>
    </article>
  );
}
