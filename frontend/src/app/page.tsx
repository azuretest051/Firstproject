import { PreferenceForm } from "@/components/PreferenceForm";
import { TrendingCurations } from "@/components/TrendingCurations";

export default function HomePage() {
  return (
    <div className="relative w-full overflow-hidden">
      <div className="absolute -top-24 left-1/2 -translate-x-1/2 w-[1000px] h-[480px] bg-gradient-to-b from-primary-container/20 via-secondary-container/10 to-transparent blur-[120px] pointer-events-none -z-10 animate-glow-pulse" />
      <div className="absolute top-[320px] right-10 w-96 h-96 bg-primary-container/10 blur-[140px] pointer-events-none -z-10" />

      <div className="max-w-[1200px] mx-auto px-4 sm:px-margin-lg py-space-xl flex flex-col gap-space-xl">
        <section className="flex flex-col items-center text-center gap-space-md pt-4 animate-fade-up">
          <div className="flex flex-wrap items-center justify-center gap-space-sm">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-surface-container border border-surface-container-highest shadow-sm">
              <span className="inline-block w-2 h-2 rounded-full bg-primary-container animate-ping" />
              <span className="text-label-sm uppercase tracking-wider text-primary">
                AI-Powered Gastronomy & Sensory Palate Matching
              </span>
            </div>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-surface-container-low text-secondary text-label-sm border border-secondary/20 shadow-inner">
              <span className="material-symbols-outlined text-[15px] text-secondary">
                bolt
              </span>
              <span>1,420+ flavor graphs mapped across Bangalore today</span>
            </div>
          </div>

          <h1 className="text-3xl sm:text-headline-xl text-on-surface max-w-4xl tracking-tight leading-[1.12] font-extrabold">
            Personalized restaurant picks, <br />
            <span className="text-primary-container relative inline-block">
              explained by AI.
              <svg
                className="absolute -bottom-2 left-0 w-full h-2 text-primary-container/40"
                preserveAspectRatio="none"
                viewBox="0 0 100 8"
              >
                <path
                  d="M0,5 Q50,0 100,5"
                  fill="none"
                  stroke="currentColor"
                  strokeLinecap="round"
                  strokeWidth="3"
                />
              </svg>
            </span>
          </h1>

          <p className="text-body-lg text-on-surface-variant max-w-2xl text-balance">
            Discover Bangalore&apos;s finest dining calibrated to your exact taste,
            budget, and culinary vibe in seconds.
          </p>
        </section>

        <PreferenceForm />
        <TrendingCurations />
      </div>
    </div>
  );
}
