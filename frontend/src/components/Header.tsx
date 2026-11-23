"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Icon } from "./Icon";

const NAV = [
  { href: "/", label: "Discover", path: "discover" },
  { href: "/", label: "AI TasteMatch", path: "ai-tastematch", pulse: true },
  { href: "/", label: "Food Map", path: "food-map" },
  { href: "/", label: "Saved Picks", path: "saved-picks", badge: "4" },
] as const;

export function Header() {
  const pathname = usePathname();
  const onResults = pathname?.startsWith("/results");

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-surface-container-lowest/90 backdrop-blur-xl border-b border-surface-container-highest shadow-[0_1px_8px_rgba(0,0,0,0.4)]">
      <div className="h-16 max-w-7xl mx-auto px-margin-lg flex items-center justify-between gap-space-md">
        <div className="flex items-center gap-space-lg">
          <Link
            href="/"
            className="flex items-center gap-space-sm group focus:outline-none"
          >
            <div className="w-9 h-9 rounded-lg bg-surface-container flex items-center justify-center border border-outline-variant group-hover:border-primary-container transition-colors">
              <Icon name="local_fire_department" className="text-primary-container text-[22px]" />
            </div>
            <div className="flex flex-col">
              <span className="text-headline-sm text-on-surface tracking-tight leading-none group-hover:text-primary transition-colors">
                TasteMatch
                <span className="text-primary-container ml-0.5">AI</span>
              </span>
              <span className="text-label-sm text-on-surface-variant uppercase tracking-wider scale-90 -ml-1 mt-0.5">
                Curated Metro
              </span>
            </div>
          </Link>
          <div className="hidden xl:flex items-center gap-space-xs px-space-sm py-1 rounded-full bg-surface-container-low border border-surface-container-highest hover:border-outline-variant transition-colors cursor-pointer">
            <Icon name="location_on" className="text-primary-container text-[16px]" />
            <span className="text-label-md text-on-surface">Bangalore, KA</span>
            <Icon name="expand_more" className="text-on-surface-variant text-[14px]" />
          </div>
        </div>

        <nav className="hidden lg:flex items-center gap-space-xs p-1 rounded-xl bg-surface-container-lowest border border-surface-container-highest">
          {NAV.map((item) => {
            const active =
              (item.path === "discover" && !onResults) ||
              (item.path === "ai-tastematch" && onResults);
            const href =
              item.path === "ai-tastematch" && onResults ? "/results" : item.href;
            return (
              <Link
                key={item.path}
                href={href}
                aria-current={active ? "page" : undefined}
                className={
                  active
                    ? "px-space-md py-1.5 transition-all bg-surface-container-high text-primary-container text-label-lg font-bold rounded-lg shadow-[0_0_12px_rgba(255,107,74,0.15)] flex items-center gap-1.5"
                    : "px-space-md py-1.5 rounded-lg text-label-lg text-on-surface-variant hover:text-on-surface hover:bg-surface-container transition-all flex items-center gap-1.5"
                }
              >
                <span>{item.label}</span>
                {"pulse" in item && item.pulse ? (
                  <span className="w-1.5 h-1.5 rounded-full bg-primary-container animate-pulse" />
                ) : null}
                {"badge" in item && item.badge ? (
                  <span className="px-1.5 py-0.5 rounded-full bg-surface-container-highest text-[10px] font-bold text-on-surface-variant">
                    {item.badge}
                  </span>
                ) : null}
              </Link>
            );
          })}
        </nav>

        <div className="flex items-center gap-space-md">
          <div className="hidden md:flex items-center relative w-56 lg:w-64">
            <Icon
              name="search"
              className="text-on-surface-variant text-[18px] absolute left-3 pointer-events-none"
            />
            <input
              className="w-full pl-9 pr-10 py-1.5 rounded-lg bg-surface-container-low border border-surface-container-highest text-on-surface text-body-sm placeholder:text-on-surface-variant/60 focus:outline-none focus:border-primary-container transition-all"
              placeholder="Cuisines, micro-regions..."
              type="text"
              readOnly
            />
            <span className="absolute right-2 px-1.5 py-0.5 rounded bg-surface-container-highest text-[10px] font-mono text-on-surface-variant border border-surface-bright">
              ⌘K
            </span>
          </div>
          <div className="flex items-center gap-space-xs">
            <button
              aria-label="Notifications"
              className="w-9 h-9 rounded-lg bg-surface-container-low border border-surface-container-highest flex items-center justify-center text-on-surface-variant hover:text-on-surface hover:border-outline-variant hover:bg-surface-container transition-all relative"
              type="button"
            >
              <Icon name="notifications" className="text-[20px]" />
              <span className="absolute top-2 right-2 w-2 h-2 rounded-full bg-primary-container border-2 border-surface-container-lowest" />
            </button>
            <div className="w-9 h-9 rounded-full bg-primary-container flex items-center justify-center cursor-pointer ring-2 ring-primary-container/20 hover:ring-primary-container/50 transition-all ml-1">
              <Icon name="person" className="text-on-primary-container text-[20px]" />
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
