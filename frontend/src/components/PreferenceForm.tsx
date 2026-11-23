"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { fetchLocations, postRecommend } from "@/lib/api";
import {
  CUISINE_OPTIONS,
  NEIGHBORHOOD_PILLS,
  VIBE_CHIPS,
} from "@/lib/format";
import { saveResult } from "@/lib/storage";
import type { Budget } from "@/lib/types";
import { Icon } from "./Icon";

const BUDGETS: { id: Budget; title: string; subtitle: string }[] = [
  { id: "low", title: "Low ₹", subtitle: "< ₹800" },
  { id: "medium", title: "Medium ₹₹", subtitle: "₹800–₹2,200" },
  { id: "high", title: "Fine Dining ₹₹₹", subtitle: "₹2,200+" },
];

export function PreferenceForm() {
  const router = useRouter();
  const [locations, setLocations] = useState<string[]>([]);
  const [location, setLocation] = useState("");
  const [budget, setBudget] = useState<Budget>("medium");
  const [cuisine, setCuisine] = useState("");
  const [minRating, setMinRating] = useState(4.0);
  const [vibe, setVibe] = useState("");
  const [status, setStatus] = useState<{ message: string; error: boolean } | null>(
    null,
  );
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    let cancelled = false;
    fetchLocations()
      .then((data) => {
        if (cancelled) return;
        const options: string[] = [];
        for (const city of data.cities || []) {
          if (city && !options.includes(city)) options.push(city);
        }
        for (const loc of data.locations || []) {
          if (loc && !options.includes(loc)) options.push(loc);
        }
        setLocations(options.length ? options : ["Bangalore"]);
      })
      .catch(() => {
        if (!cancelled) setLocations(["Bangalore"]);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const locationOptions = useMemo(() => {
    const set = new Set(locations);
    if (location) set.add(location);
    for (const pill of NEIGHBORHOOD_PILLS) set.add(pill);
    return Array.from(set);
  }, [locations, location]);

  function selectNeighborhood(value: string) {
    setLocation(value);
  }

  function clearAll() {
    setLocation("");
    setBudget("medium");
    setCuisine("");
    setMinRating(4.0);
    setVibe("");
    setStatus(null);
  }

  function appendVibe(chip: string) {
    setVibe((cur) => (cur.trim() ? `${cur.trim()}, ${chip}` : chip));
  }

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    if (!location.trim()) {
      setStatus({ message: "Please select a location.", error: true });
      return;
    }
    if (!cuisine.trim()) {
      setStatus({ message: "Please select a palate & cuisine.", error: true });
      return;
    }

    const prefs = {
      location: location.trim(),
      budget,
      cuisine: cuisine.trim(),
      min_rating: minRating,
      additional_preferences: vibe.trim() || null,
    };

    setSubmitting(true);
    setStatus({
      message: "Evaluating kitchens and calibrating palate scores…",
      error: false,
    });

    try {
      const result = await postRecommend(prefs);
      saveResult(prefs, result);
      router.push("/results");
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unknown error";
      setStatus({
        message: `Could not get recommendations: ${message}`,
        error: true,
      });
      setSubmitting(false);
    }
  }

  return (
    <section className="w-full bg-surface-container-low rounded-2xl p-6 sm:p-8 shadow-2xl relative animate-fade-up">
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-primary-container/60 to-transparent" />
      <form className="flex flex-col gap-space-lg" onSubmit={onSubmit}>
        <div className="flex flex-col gap-space-sm">
          <div className="flex items-center justify-between">
            <label
              className="text-label-lg text-on-surface flex items-center gap-2"
              htmlFor="tm-location"
            >
              <Icon name="explore" className="text-primary-container text-[20px]" />
              <span>
                Location <span className="text-primary-container">*</span>
              </span>
            </label>
            <span className="text-label-sm text-on-surface-variant/70">
              Required · Bangalore metro areas
            </span>
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-space-md items-center">
            <div className="lg:col-span-5 relative">
              <Icon
                name="location_on"
                className="absolute left-3.5 top-1/2 -translate-y-1/2 text-primary-container text-[20px] pointer-events-none"
              />
              <select
                id="tm-location"
                name="location"
                required
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                className="w-full appearance-none pl-11 pr-10 py-3 rounded-xl bg-surface-container text-on-surface text-body-md focus:outline-none focus:ring-1 focus:ring-primary-container transition-all cursor-pointer"
              >
                <option value="" disabled>
                  Select a location
                </option>
                {locationOptions.map((name) => (
                  <option key={name} value={name}>
                    {name}
                  </option>
                ))}
              </select>
              <Icon
                name="expand_more"
                className="absolute right-3.5 top-1/2 -translate-y-1/2 text-on-surface-variant text-[20px] pointer-events-none"
              />
            </div>
            <div className="lg:col-span-7 flex flex-wrap items-center gap-2">
              {NEIGHBORHOOD_PILLS.map((pill) => {
                const active = location === pill;
                return (
                  <button
                    key={pill}
                    type="button"
                    onClick={() => selectNeighborhood(pill)}
                    className={
                      active
                        ? "px-3.5 py-1.5 rounded-full text-label-md transition-all bg-primary-container/20 text-primary-container border border-primary-container/40"
                        : "px-3.5 py-1.5 rounded-full text-label-md transition-all bg-surface-container text-on-surface hover:bg-surface-container-high"
                    }
                  >
                    {pill}
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        <div className="w-full h-px bg-surface-container-highest/60" />

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-space-lg">
          <div className="lg:col-span-5 flex flex-col gap-space-sm">
            <label className="text-label-lg text-on-surface flex items-center gap-2">
              <Icon name="payments" className="text-secondary text-[20px]" />
              <span>Budget Envelope (Per Person)</span>
            </label>
            <div className="grid grid-cols-3 gap-1.5 p-1 rounded-xl bg-surface-container border border-surface-container-highest/50">
              {BUDGETS.map((item) => {
                const active = budget === item.id;
                return (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => setBudget(item.id)}
                    className={
                      active
                        ? "flex flex-col items-center py-2.5 px-2 rounded-lg bg-surface-container-high text-primary-container shadow-md border border-primary-container/30 transition-all text-center"
                        : "flex flex-col items-center py-2.5 px-2 rounded-lg bg-surface-container-low text-on-surface hover:text-white transition-all text-center"
                    }
                  >
                    <span className="text-label-md font-bold">{item.title}</span>
                    <span
                      className={
                        active
                          ? "text-[10px] text-primary"
                          : "text-[10px] text-on-surface-variant"
                      }
                    >
                      {item.subtitle}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>

          <div className="lg:col-span-7 flex flex-col gap-space-sm">
            <div className="flex items-center justify-between">
              <label
                className="text-label-lg text-on-surface flex items-center gap-2"
                htmlFor="tm-cuisine"
              >
                <Icon
                  name="restaurant_menu"
                  className="text-primary-container text-[20px]"
                />
                <span>
                  Palate &amp; Cuisine <span className="text-primary-container">*</span>
                </span>
              </label>
              <span className="text-label-sm text-on-surface-variant/70">Required</span>
            </div>
            <div className="relative">
              <Icon
                name="restaurant_menu"
                className="absolute left-3.5 top-1/2 -translate-y-1/2 text-primary-container text-[20px] pointer-events-none"
              />
              <select
                id="tm-cuisine"
                name="cuisine"
                required
                value={cuisine}
                onChange={(e) => setCuisine(e.target.value)}
                className="w-full appearance-none pl-11 pr-10 py-3 rounded-xl bg-surface-container text-on-surface text-body-md focus:outline-none focus:ring-1 focus:ring-primary-container transition-all cursor-pointer"
              >
                <option value="" disabled>
                  Select a cuisine
                </option>
                {CUISINE_OPTIONS.map((name) => (
                  <option key={name} value={name}>
                    {name}
                  </option>
                ))}
              </select>
              <Icon
                name="expand_more"
                className="absolute right-3.5 top-1/2 -translate-y-1/2 text-on-surface-variant text-[20px] pointer-events-none"
              />
            </div>
          </div>
        </div>

        <div className="w-full h-px bg-surface-container-highest/60" />

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-space-lg items-start">
          <div className="lg:col-span-4 flex flex-col gap-space-md p-4 rounded-xl bg-surface-container">
            <div className="flex items-center justify-between">
              <label className="text-label-lg text-on-surface flex items-center gap-2">
                <Icon name="stars" className="text-secondary text-[20px]" />
                <span>Minimum Foodie Rating</span>
              </label>
              <span className="px-2.5 py-0.5 rounded-md bg-surface-container-highest text-secondary text-headline-sm font-bold flex items-center gap-1">
                {minRating.toFixed(1)}{" "}
                <Icon name="star" className="text-[16px]" />
              </span>
            </div>
            <div className="flex flex-col gap-2">
              <input
                className="w-full h-2 rounded-lg bg-surface-container-highest accent-primary-container cursor-pointer"
                max={5}
                min={0}
                step={0.1}
                type="range"
                value={minRating}
                onChange={(e) => setMinRating(parseFloat(e.target.value) || 0)}
              />
              <div className="flex justify-between text-label-sm text-on-surface-variant">
                <span>Any (0.0)</span>
                <span className="text-secondary font-bold">4.0 ★ Gastronomic Cut</span>
                <span>Flawless (5.0)</span>
              </div>
            </div>
            <p className="text-body-sm text-on-surface-variant/80">
              Filters community ratings against verified frequent epicurean check-ins.
            </p>
          </div>

          <div className="lg:col-span-8 flex flex-col gap-space-xs">
            <div className="flex items-center justify-between">
              <label className="text-label-lg text-on-surface flex items-center gap-2">
                <Icon name="psychology" className="text-primary-container text-[20px]" />
                <span>Natural Language Vibe &amp; Sensory Atmosphere</span>
              </label>
              <span className="text-label-sm text-primary flex items-center gap-1">
                <span className="inline-block w-1.5 h-1.5 rounded-full bg-primary-container" />
                Sensory Vector Matching
              </span>
            </div>
            <textarea
              className="w-full p-3.5 rounded-xl bg-surface-container text-on-surface text-body-md placeholder:text-on-surface-variant/40 focus:outline-none focus:ring-1 focus:ring-primary-container resize-none transition-all leading-relaxed"
              placeholder="e.g., Rooftop seating with artisanal craft cocktails and wood-fired sourdough pizzas, quiet enough for conversation"
              rows={3}
              value={vibe}
              onChange={(e) => setVibe(e.target.value)}
            />
            <div className="flex flex-wrap items-center gap-2 mt-1">
              <span className="text-label-sm text-on-surface-variant">
                Suggested Prompts:
              </span>
              {VIBE_CHIPS.map((chip) => (
                <button
                  key={chip}
                  type="button"
                  onClick={() => appendVibe(chip)}
                  className="px-2.5 py-1 rounded-md bg-surface-container hover:bg-surface-container-high text-label-sm text-on-surface-variant hover:text-primary-container transition-colors"
                >
                  + {chip}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row items-center justify-between gap-space-md pt-2">
          <div className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-surface-container border border-surface-container-highest">
            <Icon name="verified" className="text-secondary text-[18px]" />
            <span className="text-label-md text-on-surface">
              <span className="font-bold text-secondary">AI-ranked venues</span> match
              these parameters
            </span>
          </div>
          <div className="flex items-center gap-space-md w-full sm:w-auto justify-end">
            <button
              className="text-label-md text-on-surface-variant hover:text-on-surface transition-colors px-3 py-2"
              type="button"
              onClick={clearAll}
            >
              Clear all filters
            </button>
            <button
              className="flex-1 sm:flex-none flex items-center justify-center gap-2 px-8 py-3.5 rounded-xl bg-primary-container text-on-primary text-label-lg font-bold shadow-[0_4px_24px_rgba(255,107,74,0.35)] hover:shadow-[0_4px_32px_rgba(255,107,74,0.5)] hover:bg-[#ff8a65] transition-all transform active:scale-95 disabled:opacity-70"
              type="submit"
              disabled={submitting}
            >
              <span>
                {submitting ? "Matching…" : "Find Restaurants (AI Match)"}
              </span>
              <Icon name="arrow_forward" className="text-[20px]" />
            </button>
          </div>
        </div>

        {status ? (
          <p
            className={`text-body-sm mt-2 ${
              status.error ? "text-error" : "text-primary-container"
            }`}
          >
            {status.message}
          </p>
        ) : null}
      </form>
    </section>
  );
}
