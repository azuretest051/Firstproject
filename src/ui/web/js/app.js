/**
 * TasteMatch AI — wire Stitch HTML screens to the FastAPI /recommend engine.
 */
(function () {
  const API_BASE = "";
  const STORAGE_KEY = "tastematch_last_result";
  const PREFS_KEY = "tastematch_last_prefs";

  const PLACEHOLDER_IMAGES = [
    "https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=800&q=80",
    "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=800&q=80",
    "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=800&q=80",
    "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&q=80",
    "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=800&q=80",
  ];

  const state = {
    location: "",
    budget: "medium",
    cuisine: "",
    min_rating: 4.0,
    additional_preferences: "",
  };

  const PILL_ACTIVE =
    "px-3.5 py-1.5 rounded-full font-label-md text-label-md transition-all bg-primary-container/20 text-primary-container border border-primary-container/40";
  const PILL_IDLE =
    "px-3.5 py-1.5 rounded-full font-label-md text-label-md transition-all bg-surface-container text-on-surface hover:bg-surface-container-high";

  function esc(value) {
    return String(value ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function tasteScore(rank) {
    const r = Number(rank) || 1;
    return Math.max(72, 99 - (r - 1) * 4);
  }

  function formatCost(item) {
    const cost = item.estimated_cost ?? item.cost_for_two;
    if (cost == null || cost === "") return "";
    if (typeof cost === "number") return `₹${Math.round(cost)} for two`;
    const text = String(cost).trim().toLowerCase();
    if (text === "low") return "₹ Low";
    if (text === "medium") return "₹₹ Medium";
    if (text === "high") return "₹₹₹ High";
    return String(cost);
  }

  function budgetLabel(budget) {
    const map = { low: "₹ Low", medium: "₹₹ Medium", high: "₹₹₹ High" };
    return map[String(budget || "").toLowerCase()] || String(budget || "");
  }

  function cuisineTags(cuisine, limit = 3) {
    if (!cuisine) return [];
    return String(cuisine)
      .replace(/\|/g, ",")
      .split(",")
      .map((p) => p.trim())
      .filter(Boolean)
      .slice(0, limit);
  }

  async function postRecommend(prefs) {
    const res = await fetch(`${API_BASE}/recommend`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(prefs),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      const detail = data.detail || data.error || res.statusText;
      throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
    }
    return data;
  }

  function saveResult(prefs, result) {
    sessionStorage.setItem(PREFS_KEY, JSON.stringify(prefs));
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(result));
  }

  function loadResult() {
    try {
      const prefs = JSON.parse(sessionStorage.getItem(PREFS_KEY) || "null");
      const result = JSON.parse(sessionStorage.getItem(STORAGE_KEY) || "null");
      return { prefs, result };
    } catch {
      return { prefs: null, result: null };
    }
  }

  function syncNeighborhoodPills(selected) {
    document.querySelectorAll("#neighborhood-pills button").forEach((btn) => {
      const value = (btn.dataset.location || btn.textContent || "").trim();
      btn.className = value === selected ? PILL_ACTIVE : PILL_IDLE;
    });
  }

  async function populateLocationSelect(selectEl) {
    if (!selectEl) return;
    try {
      const res = await fetch(`${API_BASE}/meta/locations`);
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.detail || res.statusText);

      const options = [];
      for (const city of data.cities || []) {
        if (city && !options.includes(city)) options.push(city);
      }
      for (const loc of data.locations || []) {
        if (loc && !options.includes(loc)) options.push(loc);
      }

      const placeholder = document.createElement("option");
      placeholder.value = "";
      placeholder.disabled = true;
      placeholder.selected = true;
      placeholder.textContent = "Select a location";

      selectEl.innerHTML = "";
      selectEl.appendChild(placeholder);
      for (const name of options) {
        const opt = document.createElement("option");
        opt.value = name;
        opt.textContent = name;
        selectEl.appendChild(opt);
      }
    } catch (err) {
      console.warn("Could not load locations:", err);
      if (!selectEl.options.length) {
        selectEl.innerHTML =
          '<option value="" disabled selected>Select a location</option><option value="Bangalore">Bangalore</option>';
      }
    }
  }

  function showFormStatus(statusEl, message, isError) {
    if (!statusEl) return;
    statusEl.classList.remove("hidden");
    statusEl.classList.toggle("text-error", Boolean(isError));
    statusEl.classList.toggle("text-primary-container", !isError);
    statusEl.textContent = message;
  }

  /* ─── Home page ─── */
  function initHome() {
    const form = document.getElementById("tm-prefs-form");
    if (!form) return;

    const locationSelect = document.getElementById("tm-location");
    const cuisineSelect = document.getElementById("tm-cuisine");
    const vibeInput = document.getElementById("tm-vibe");
    const ratingInput = document.getElementById("tm-rating");
    const ratingVal = document.getElementById("rating-val");
    const statusEl = document.getElementById("tm-form-status");
    const submitBtn = document.getElementById("tm-submit");

    populateLocationSelect(locationSelect);

    if (locationSelect) {
      locationSelect.addEventListener("change", () => {
        state.location = locationSelect.value.trim();
        syncNeighborhoodPills(state.location);
      });
    }

    if (cuisineSelect) {
      cuisineSelect.addEventListener("change", () => {
        state.cuisine = cuisineSelect.value.trim();
      });
    }

    // Neighborhood pills → set location dropdown
    document.querySelectorAll("#neighborhood-pills button").forEach((btn) => {
      btn.addEventListener("click", () => {
        const value = (btn.dataset.location || btn.textContent || "").trim();
        if (!value || !locationSelect) return;

        const hasOption = Array.from(locationSelect.options).some(
          (opt) => opt.value === value
        );
        if (!hasOption) {
          const opt = document.createElement("option");
          opt.value = value;
          opt.textContent = value;
          locationSelect.appendChild(opt);
        }
        locationSelect.value = value;
        state.location = value;
        syncNeighborhoodPills(value);
      });
    });

    // Budget buttons
    document.querySelectorAll(".budget-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        const label = (btn.textContent || "").toLowerCase();
        if (label.includes("low")) state.budget = "low";
        else if (label.includes("fine") || label.includes("high")) state.budget = "high";
        else state.budget = "medium";

        document.querySelectorAll(".budget-btn").forEach((b) => {
          b.className =
            "budget-btn flex flex-col items-center py-2.5 px-2 rounded-lg bg-surface-container-low text-on-surface hover:text-white transition-all text-center";
        });
        btn.className =
          "budget-btn flex flex-col items-center py-2.5 px-2 rounded-lg bg-surface-container-high text-primary-container shadow-md border border-primary-container/30 transition-all text-center";
      });
    });

    // Suggested vibe chips
    document.querySelectorAll("[data-vibe]").forEach((btn) => {
      btn.addEventListener("click", () => {
        if (!vibeInput) return;
        const chip = btn.getAttribute("data-vibe");
        const cur = vibeInput.value.trim();
        vibeInput.value = cur ? `${cur}, ${chip}` : chip;
      });
    });

    if (ratingInput) {
      ratingInput.addEventListener("input", () => {
        state.min_rating = parseFloat(ratingInput.value) || 0;
        if (ratingVal) {
          ratingVal.innerHTML = `${state.min_rating.toFixed(1)} <span class="material-symbols-outlined text-[16px]">star</span>`;
        }
      });
    }

    form.addEventListener("submit", async (event) => {
      event.preventDefault();

      const location = (locationSelect?.value || "").trim();
      const cuisine = (cuisineSelect?.value || "").trim();

      if (!location) {
        showFormStatus(statusEl, "Please select a location.", true);
        locationSelect?.focus();
        return;
      }
      if (!cuisine) {
        showFormStatus(statusEl, "Please select a palate & cuisine.", true);
        cuisineSelect?.focus();
        return;
      }

      state.location = location;
      state.cuisine = cuisine;
      if (ratingInput) {
        state.min_rating = parseFloat(ratingInput.value) || state.min_rating;
      }

      const prefs = {
        location,
        budget: state.budget,
        cuisine,
        min_rating: state.min_rating,
        additional_preferences: (vibeInput?.value || "").trim() || null,
      };

      showFormStatus(
        statusEl,
        "Evaluating kitchens and calibrating palate scores…",
        false
      );
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.classList.add("opacity-70");
      }

      try {
        const result = await postRecommend(prefs);
        saveResult(prefs, result);
        window.location.href = "/results.html";
      } catch (err) {
        showFormStatus(
          statusEl,
          `Could not get recommendations: ${err.message}`,
          true
        );
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.classList.remove("opacity-70");
        }
      }
    });

    // Nav: AI TasteMatch stays home; results link if available
    document.querySelectorAll('[data-path="ai-tastematch"]').forEach((a) => {
      a.setAttribute("href", "/");
    });
    document.querySelectorAll('[data-path="discover"]').forEach((a) => {
      a.setAttribute("href", "/");
    });
  }

  /* ─── Results page ─── */
  function cardHtml(item, index) {
    const rank = item.rank ?? index + 1;
    const score = tasteScore(rank);
    const name = esc(item.restaurant_name || "Unknown restaurant");
    const explanation = esc(item.explanation || "No explanation provided.");
    const cuisine = item.cuisine || "";
    const rating = item.rating != null ? esc(item.rating) : "";
    const location = esc(item.location || "");
    const cost = esc(formatCost(item));
    const tags = cuisineTags(cuisine);
    const img = PLACEHOLDER_IMAGES[index % PLACEHOLDER_IMAGES.length];
    const isTop = Number(rank) === 1;
    const matchIcon = isTop ? "local_fire_department" : "insights";
    const matchCls = isTop
      ? "px-2.5 py-1 rounded-md bg-primary-container text-on-primary-container font-label-sm text-label-sm uppercase font-extrabold tracking-wider flex items-center gap-1 shadow-sm"
      : "px-2.5 py-1 rounded-md bg-surface-container-high text-primary font-label-sm text-label-sm uppercase font-bold tracking-wider flex items-center gap-1";
    const cardGlow = isTop
      ? 'style="box-shadow: 0 4px 24px -2px rgba(255, 107, 74, 0.12), 0 0 1px 1px rgba(255, 107, 74, 0.35);"'
      : "";
    const tagHtml =
      tags
        .map(
          (t, i) =>
            `<span class="px-2 py-0.5 rounded bg-surface-container ${
              i === 0 ? "text-primary font-semibold" : "text-on-surface-variant"
            } font-label-sm text-label-sm">${esc(t)}</span>`
        )
        .join("") ||
      `<span class="px-2 py-0.5 rounded bg-surface-container text-on-surface-variant font-label-sm text-label-sm">Curated pick</span>`;

    return `
<article class="relative rounded-xl bg-surface-container-low p-space-md shadow-md transition-all duration-300 hover:shadow-lg group" ${cardGlow}>
  <div class="flex items-center justify-between gap-2 mb-space-sm">
    <div class="flex items-center gap-2">
      <span class="${matchCls}">
        <span class="material-symbols-outlined text-[14px]">${matchIcon}</span>
        #${esc(rank)} Match · ${score}% Taste Score
      </span>
      ${
        rating
          ? `<span class="px-2 py-0.5 rounded-md bg-surface-container-high text-secondary font-label-sm text-label-sm flex items-center gap-1 font-semibold">
              <span class="material-symbols-outlined text-[13px]" style="font-variation-settings: 'FILL' 1;">star</span>
              ${rating}
            </span>`
          : ""
      }
    </div>
    ${
      location
        ? `<div class="flex items-center gap-1 text-on-surface-variant font-label-sm text-label-sm">
            <span class="material-symbols-outlined text-[16px] text-primary-container">near_me</span>
            <span>${location}</span>
          </div>`
        : ""
    }
  </div>
  <div class="grid grid-cols-1 md:grid-cols-12 gap-space-md">
    <div class="md:col-span-5 relative rounded-lg overflow-hidden h-52 md:h-full min-h-[200px] bg-surface-container">
      <img alt="${name}" class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105" src="${img}"/>
      <div class="absolute inset-0 bg-gradient-to-t from-surface-container-lowest/90 via-transparent to-black/20"></div>
      ${
        cost
          ? `<div class="absolute bottom-2 left-2 flex items-center gap-1.5 px-2 py-1 rounded bg-surface-container-lowest/80 backdrop-blur-md font-label-sm text-label-sm text-on-surface">
              <span class="w-2 h-2 rounded-full bg-secondary-container"></span>
              <span>${cost}</span>
            </div>`
          : ""
      }
    </div>
    <div class="md:col-span-7 flex flex-col justify-between gap-space-sm">
      <div>
        <div class="flex items-start justify-between gap-2">
          <div>
            <h3 class="font-headline-md text-headline-md text-on-surface leading-tight tracking-tight">${name}</h3>
            <p class="font-body-sm text-body-sm text-on-surface-variant mt-0.5">${esc(cuisine) || "Recommended dining"}</p>
          </div>
        </div>
        <div class="flex flex-wrap items-center gap-1.5 mt-space-xs">${tagHtml}</div>
        <div class="mt-space-sm p-space-sm rounded-lg bg-surface-container flex items-start gap-2.5 relative overflow-hidden">
          <div class="w-1 absolute left-0 top-0 bottom-0 bg-primary-container"></div>
          <div class="pl-1 flex flex-col gap-0.5">
            <span class="font-label-sm text-label-sm font-bold text-primary-container uppercase tracking-wider flex items-center gap-1">
              <span class="material-symbols-outlined text-[13px]" style="font-variation-settings: 'FILL' 1;">auto_awesome</span>
              Why TasteMatch Picked This
            </span>
            <p class="font-body-sm text-body-sm text-on-surface leading-snug">${explanation}</p>
          </div>
        </div>
      </div>
      <div class="flex items-center gap-space-sm pt-space-xs">
        <button class="flex-1 py-2 px-space-md rounded-lg bg-primary-container hover:bg-tertiary-container text-on-primary-container font-label-lg text-label-lg font-bold transition-all shadow-md flex items-center justify-center gap-1.5 cursor-pointer" type="button">
          <span class="material-symbols-outlined text-[18px]">table_restaurant</span>
          <span>Book Table</span>
        </button>
        <button class="py-2 px-space-md rounded-lg bg-surface-container hover:bg-surface-container-high text-on-surface font-label-lg text-label-lg font-semibold transition-colors flex items-center gap-1 cursor-pointer" type="button">
          <span>View details</span>
          <span class="material-symbols-outlined text-[16px]">arrow_outward</span>
        </button>
      </div>
    </div>
  </div>
</article>`;
  }

  function renderResults(prefs, result) {
    const feed = document.getElementById("tm-results-feed");
    if (!feed) return;

    const allRecommendations = (result.recommendations || []).filter(
      (r) => r && typeof r === "object"
    );
    // Stitch desktop results shows a short curated batch (top 4–5).
    const recommendations = allRecommendations.slice(0, 5);
    const meta = result.meta || {};
    const summary = (result.summary || "").trim();
    const considered = meta.candidates_considered || 0;
    const matchCount = meta.match_count || recommendations.length;
    const status = meta.status || "ok";
    const conf = status === "ok" ? "High Confidence" : "Fallback Ranking";

    // Preference strip
    const stripLoc = document.getElementById("tm-strip-location");
    const stripMeta = document.getElementById("tm-strip-meta");
    if (stripLoc) {
      stripLoc.innerHTML = `<strong class="text-on-surface">${esc(
        prefs.location || ""
      )}</strong>`;
    }
    if (stripMeta) {
      const bits = [
        budgetLabel(prefs.budget),
        prefs.cuisine,
        prefs.min_rating != null ? `${prefs.min_rating}+` : null,
        prefs.additional_preferences || null,
      ].filter(Boolean);
      stripMeta.textContent = bits.join("  /  ");
    }

    // Synthesis
    const synthBody = document.getElementById("tm-synth-body");
    const synthMeta = document.getElementById("tm-synth-meta");
    const synthBadge = document.getElementById("tm-synth-badge");
    if (synthBadge) synthBadge.textContent = conf;
    if (synthBody) {
      synthBody.innerHTML = summary
        ? esc(summary)
        : `Ranked venues in <strong>${esc(
            prefs.location || "your area"
          )}</strong> for <strong>${esc(
            prefs.cuisine || "your cuisine"
          )}</strong>.`;
    }
    if (synthMeta) {
      synthMeta.innerHTML = `
        <span class="flex items-center gap-1"><span class="material-symbols-outlined text-[14px] text-secondary">check_circle</span> ${considered} evaluated</span>
        <span>•</span>
        <span class="text-on-surface">Top ${recommendations.length} shown</span>
        <span>•</span>
        <span>${matchCount} filter matches</span>`;
    }

    // Empty state
    const emptyEl = document.getElementById("tm-empty-state");
    const loadingEl = document.getElementById("tm-loading-state");
    if (loadingEl) loadingEl.classList.add("hidden");

    if (!recommendations.length || status === "no_matches") {
      feed.innerHTML = "";
      if (emptyEl) {
        emptyEl.classList.remove("hidden");
        emptyEl.classList.add("flex");
      }
      return;
    }
    if (emptyEl) {
      emptyEl.classList.add("hidden");
      emptyEl.classList.remove("flex");
    }

    feed.innerHTML = recommendations.map((item, i) => cardHtml(item, i)).join("");

    const moreEl = document.getElementById("tm-more-count");
    if (moreEl) {
      moreEl.innerHTML = `Showing <strong class="text-on-surface">${recommendations.length}</strong> of <strong class="text-on-surface">${matchCount}</strong> high-confidence matches.`;
    }

    // Sidebar metrics (approximate from prefs)
    const setBar = (id, pct) => {
      const el = document.getElementById(id);
      if (el) el.style.width = `${pct}%`;
      const label = document.getElementById(`${id}-val`);
      if (label) label.textContent = `${pct}%`;
    };
    setBar("tm-metric-flavor", prefs.cuisine ? 96 : 80);
    setBar(
      "tm-metric-budget",
      { low: 88, medium: 94, high: 90 }[String(prefs.budget || "medium").toLowerCase()] ||
        90
    );
    setBar("tm-metric-atmosphere", prefs.additional_preferences ? 91 : 84);
    setBar("tm-metric-distance", 88);

    // Map pins
    const pins = document.getElementById("tm-map-pins");
    if (pins) {
      const positions = [
        ["35%", "45%"],
        ["50%", "25%"],
        ["65%", "70%"],
        ["20%", "60%"],
      ];
      pins.innerHTML = recommendations
        .slice(0, 4)
        .map((item, i) => {
          const [top, left] = positions[i] || ["40%", "50%"];
          const cls =
            i === 0
              ? "w-7 h-7 rounded-full bg-primary-container text-on-primary-container"
              : "w-6 h-6 rounded-full bg-surface-container-highest text-primary";
          return `<div class="absolute -translate-x-1/2 -translate-y-1/2 cursor-pointer" style="top:${top};left:${left}">
            <div class="${cls} font-label-sm text-label-sm font-extrabold flex items-center justify-center shadow-lg">${
            i + 1
          }</div>
          </div>`;
        })
        .join("");
    }

    const mapTitle = document.getElementById("tm-map-title");
    if (mapTitle) mapTitle.textContent = `${prefs.location || "Metro"} Heatmap`;
  }

  function initResults() {
    const { prefs, result } = loadResult();
    if (!prefs || !result) {
      window.location.href = "/";
      return;
    }
    renderResults(prefs, result);

    document.querySelectorAll("[data-edit-prefs]").forEach((btn) => {
      btn.addEventListener("click", () => {
        window.location.href = "/";
      });
    });
    document.querySelectorAll('[data-path="ai-tastematch"]').forEach((a) => {
      a.setAttribute("href", "/results.html");
    });
    document.querySelectorAll('[data-path="discover"]').forEach((a) => {
      a.setAttribute("href", "/");
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    if (document.body.dataset.page === "home") initHome();
    if (document.body.dataset.page === "results") initResults();
  });
})();
