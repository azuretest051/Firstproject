"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { budgetLabel } from "@/lib/format";
import { loadResult } from "@/lib/storage";
import type { RecommendPrefs, RecommendResponse } from "@/lib/types";
import { Icon } from "../Icon";
import { ResultCard } from "./ResultCard";
import { ResultsSidebar } from "./ResultsSidebar";

export function ResultsView() {
  const router = useRouter();
  const [prefs, setPrefs] = useState<RecommendPrefs | null>(null);
  const [result, setResult] = useState<RecommendResponse | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const loaded = loadResult();
    if (!loaded.prefs || !loaded.result) {
      router.replace("/");
      return;
    }
    setPrefs(loaded.prefs);
    setResult(loaded.result);
    setReady(true);
  }, [router]);

  if (!ready || !prefs || !result) {
    return (
      <div className="w-full max-w-[1200px] mx-auto px-gutter-md pt-space-xl pb-space-xl">
        <div className="rounded-xl bg-surface-container-low p-space-xl flex flex-col items-center justify-center gap-space-md">
          <div className="relative w-16 h-16 flex items-center justify-center">
            <div className="absolute inset-0 rounded-full border-2 border-primary-container/20 border-t-primary-container animate-spin" />
            <Icon name="local_fire_department" className="text-primary-container text-[24px]" />
          </div>
          <h4 className="text-headline-sm text-on-surface">Loading matches…</h4>
        </div>
      </div>
    );
  }

  const recommendations = (result.recommendations || [])
    .filter((r) => r && typeof r === "object")
    .slice(0, 5);
  const meta = result.meta || {
    candidates_considered: 0,
    match_count: 0,
    status: "ok",
  };
  const considered = meta.candidates_considered || 0;
  const matchCount = meta.match_count || recommendations.length;
  const status = meta.status || "ok";
  const conf = status === "ok" ? "High Confidence" : "Fallback Ranking";
  const empty = !recommendations.length || status === "no_matches";

  const stripBits = [
    budgetLabel(prefs.budget),
    prefs.cuisine,
    prefs.min_rating != null ? `${prefs.min_rating}+` : null,
    prefs.additional_preferences || null,
  ].filter(Boolean);

  return (
    <>
      <div className="sticky top-16 z-30 w-full bg-surface-container-lowest/95 backdrop-blur-md shadow-lg shadow-surface-container-lowest/80 py-space-sm">
        <div className="max-w-[1200px] mx-auto px-gutter-md flex flex-wrap items-center justify-between gap-space-sm">
          <div className="flex flex-wrap items-center gap-space-xs">
            <div className="flex items-center gap-1.5 px-space-sm py-1 rounded-full bg-surface-container-high text-primary text-label-md">
              <Icon name="pin_drop" className="text-[16px] text-primary-container" filled />
              <span>
                <strong className="text-on-surface">{prefs.location}</strong>
              </span>
            </div>
            <div className="hidden sm:flex items-center gap-1.5 px-space-sm py-1 rounded-full bg-surface-container text-on-surface-variant text-label-sm">
              {stripBits.join("  /  ")}
            </div>
            <Link
              href="/"
              className="flex items-center gap-1 px-space-sm py-1 rounded-lg bg-surface-container-low hover:bg-surface-container text-on-surface text-label-md transition-colors group"
            >
              <Icon
                name="tune"
                className="text-[15px] text-primary group-hover:rotate-12 transition-transform"
              />
              <span>Edit Preferences</span>
            </Link>
          </div>
          <div className="flex items-center gap-1.5 px-space-sm py-1 rounded-lg bg-surface-container-low text-on-surface text-label-md">
            <Icon name="sort" className="text-secondary text-[16px]" />
            <span className="text-on-surface-variant font-normal">Sort:</span>
            <span className="font-bold text-on-surface">AI Palate Match Score</span>
          </div>
        </div>
      </div>

      <div className="w-full max-w-[1200px] mx-auto px-gutter-md pt-space-lg pb-space-xl">
        <div className="flex flex-col lg:flex-row gap-space-lg items-start">
          <section
            aria-label="Curated Matches"
            className="w-full lg:w-[68%] flex flex-col gap-space-md"
          >
            <div className="relative overflow-hidden rounded-xl bg-surface-container-low p-space-md shadow-md animate-fade-up">
              <div className="absolute -right-8 -top-8 w-44 h-44 rounded-full bg-primary-container/10 blur-2xl pointer-events-none animate-glow-pulse" />
              <div className="flex items-start gap-space-sm relative z-10">
                <div className="w-10 h-10 rounded-lg bg-surface-container flex items-center justify-center shrink-0 shadow-sm">
                  <Icon
                    name="insights"
                    className="text-primary-container text-[24px]"
                    filled
                  />
                </div>
                <div className="flex flex-col gap-space-xs min-w-0">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="text-label-sm uppercase tracking-wider text-primary-container font-extrabold flex items-center gap-1">
                      <span className="w-2 h-2 rounded-full bg-primary-container animate-pulse" />
                      AI TasteMatch Synthesis
                    </span>
                    <span className="px-2 py-0.5 rounded-full bg-surface-container-high text-secondary text-label-sm font-bold">
                      {conf}
                    </span>
                  </div>
                  <p className="text-body-md text-on-surface leading-relaxed">
                    {result.summary?.trim() ||
                      `Ranked venues in ${prefs.location} for ${prefs.cuisine}.`}
                  </p>
                  <div className="flex items-center gap-3 mt-1 text-label-sm text-on-surface-variant">
                    <span className="flex items-center gap-1">
                      <Icon name="check_circle" className="text-[14px] text-secondary" />{" "}
                      {considered} evaluated
                    </span>
                    <span>•</span>
                    <span className="text-on-surface">
                      Top {recommendations.length} shown
                    </span>
                    <span>•</span>
                    <span>{matchCount} filter matches</span>
                  </div>
                </div>
              </div>
            </div>

            {empty ? (
              <div className="rounded-xl bg-surface-container-low p-space-xl text-center flex flex-col items-center justify-center gap-space-sm">
                <div className="w-14 h-14 rounded-full bg-surface-container flex items-center justify-center text-primary-container shadow-inner">
                  <Icon name="ramen_dining" className="text-[28px]" />
                </div>
                <h4 className="text-headline-md text-on-surface">
                  No High-Confidence Palate Matches in This Radius
                </h4>
                <p className="text-body-md text-on-surface-variant max-w-lg">
                  Try widening location, relaxing minimum rating, or changing budget.
                </p>
                <Link
                  href="/"
                  className="py-2 px-space-md rounded-lg bg-primary-container text-on-primary-container text-label-md font-bold"
                >
                  Edit Preferences
                </Link>
              </div>
            ) : (
              <div className="flex flex-col gap-space-md">
                {recommendations.map((item, index) => (
                  <ResultCard
                    key={`${item.restaurant_name}-${item.rank}-${index}`}
                    item={item}
                    index={index}
                  />
                ))}
              </div>
            )}

            <div className="p-space-md rounded-xl bg-surface-container-low flex flex-col sm:flex-row items-center justify-between gap-space-sm">
              <p className="text-body-sm text-on-surface-variant text-center sm:text-left">
                Showing{" "}
                <strong className="text-on-surface">{recommendations.length}</strong> of{" "}
                <strong className="text-on-surface">{matchCount}</strong> high-confidence
                matches.
              </p>
            </div>
          </section>

          <ResultsSidebar prefs={prefs} recommendations={recommendations} />
        </div>
      </div>
    </>
  );
}
