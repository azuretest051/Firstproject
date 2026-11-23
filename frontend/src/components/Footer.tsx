import Link from "next/link";
import { Icon } from "./Icon";

export function Footer() {
  return (
    <footer className="w-full bg-surface-container-lowest border-t border-surface-container-highest mt-auto">
      <div className="max-w-7xl mx-auto px-margin-lg py-space-xl">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-space-xl pb-space-xl border-b border-surface-container-highest">
          <div className="md:col-span-1 flex flex-col gap-space-sm">
            <div className="flex items-center gap-space-sm">
              <div className="w-7 h-7 rounded bg-surface-container flex items-center justify-center border border-outline-variant">
                <Icon name="local_fire_department" className="text-primary-container text-[18px]" />
              </div>
              <span className="text-headline-sm text-on-surface tracking-tight">
                TasteMatch<span className="text-primary-container">AI</span>
              </span>
            </div>
            <p className="text-body-sm text-on-surface-variant">
              Searing palate intelligence for urban diners across Bengaluru&apos;s
              dynamic micro-neighborhoods.
            </p>
            <div className="flex items-center gap-2 mt-2">
              <span className="w-2 h-2 rounded-full bg-secondary" />
              <span className="text-label-sm text-on-surface-variant">
                Bangalore Live Grid Active
              </span>
            </div>
          </div>

          <div className="flex flex-col gap-space-xs">
            <span className="text-label-lg text-on-surface mb-space-xs">Curations</span>
            {["Indiranagar Wood-Fired", "Koramangala Coastal", "Lavelle Chef's Tables", "Malleshwaram Heritage"].map(
              (label) => (
                <Link
                  key={label}
                  href="/"
                  className="text-body-sm text-on-surface-variant hover:text-primary transition-colors"
                >
                  {label}
                </Link>
              ),
            )}
          </div>

          <div className="flex flex-col gap-space-xs">
            <span className="text-label-lg text-on-surface mb-space-xs">Intelligence</span>
            {["Taste Affinity Engine", "Heat Index Radar", "Midnight Supper Map", "Shared Palates"].map(
              (label) => (
                <Link
                  key={label}
                  href="/"
                  className="text-body-sm text-on-surface-variant hover:text-primary transition-colors"
                >
                  {label}
                </Link>
              ),
            )}
          </div>

          <div className="flex flex-col gap-space-xs">
            <span className="text-label-lg text-on-surface mb-space-xs">
              Legal &amp; Standards
            </span>
            {[
              "Privacy Policy",
              "Terms of Service",
              "Curation Standards",
              "Chef & Restaurateur Ingestion",
            ].map((label) => (
              <span
                key={label}
                className="text-body-sm text-on-surface-variant"
              >
                {label}
              </span>
            ))}
          </div>
        </div>

        <div className="pt-space-md flex flex-col md:flex-row items-center justify-between gap-space-md">
          <p className="text-body-sm text-on-surface-variant/80 text-center md:text-left">
            <span className="font-bold text-on-surface">Algorithmic Notice:</span>{" "}
            TasteMatch culinary affinity indicators reflect neural mapping of
            flavor palates across verified Bangalore dining rooms.
          </p>
          <p className="text-label-sm text-on-surface-variant shrink-0">
            © 2026 TasteMatch AI Inc. Bengaluru.
          </p>
        </div>
      </div>
    </footer>
  );
}
