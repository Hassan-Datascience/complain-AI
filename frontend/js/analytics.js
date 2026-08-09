/**
 * analytics.js - Handles fetching resolution stats and trends for admin-analytics.html
 */
document.addEventListener("DOMContentLoaded", () => {
  loadAnalyticsStats();
  loadAnalyticsTrends();
});

async function loadAnalyticsStats() {
  const container = document.getElementById("stats-grid-container");
  const narrativeContainer = document.getElementById("stats-interpretation-text");

  try {
    const stats = await apiRequest("/analytics/stats");

    if (stats.total_resolved === 0) {
      if (container) {
        container.innerHTML = `
          <div class="col-span-full p-8 text-center bg-surface-container rounded-xl border border-outline-variant">
            <span class="material-symbols-outlined text-4xl text-amber-400 mb-2">info</span>
            <p class="font-body-md text-on-surface font-semibold">Not Enough Resolved Complaints Yet</p>
            <p class="font-body-sm text-on-surface-variant mt-1">${stats.interpretation || "No resolved complaints available yet to compute statistics."}</p>
          </div>
        `;
      }
      return;
    }

    // Populate Stat Fields
    if (narrativeContainer) {
      narrativeContainer.textContent = stats.interpretation;
    }

    const setVal = (id, val) => {
      const el = document.getElementById(id);
      if (el) el.textContent = val;
    };

    setVal("stat-mean", `${stats.mean_hours}h`);
    setVal("stat-median", `${stats.median_hours}h`);
    setVal("stat-mode", `${stats.mode_hours}h`);
    setVal("stat-range", `${stats.min_hours}h - ${stats.max_hours}h`);
    setVal("stat-variance", stats.variance_hours);
    setVal("stat-std-dev", `${stats.std_dev_hours}h`);
    setVal("stat-iqr", `${stats.iqr_hours}h (Q1: ${stats.q1_hours}h, Q3: ${stats.q3_hours}h)`);
    setVal("stat-outliers-count", `${stats.outliers_count} delayed`);

  } catch (err) {
    console.error("Failed to load resolution stats:", err);
    if (container) {
      container.innerHTML = `<div class="col-span-full p-6 text-center text-error">Failed to load analytics statistics.</div>`;
    }
  }
}

async function loadAnalyticsTrends() {
  const container = document.getElementById("trends-data-list");
  if (!container) return;

  try {
    const trendsData = await apiRequest("/analytics/trends");
    const trends = trendsData.daily_trends || [];

    if (trends.length === 0) {
      container.innerHTML = `<p class="text-xs text-on-surface-variant p-4">No daily submission data available yet.</p>`;
      return;
    }

    let html = "";
    trends.forEach((t) => {
      html += `
        <div class="flex items-center justify-between p-3 bg-surface-container rounded-lg border border-outline-variant/40">
          <span class="font-label-sm text-on-surface-variant font-mono">${t.date}</span>
          <span class="font-label-md font-bold text-primary">${t.count} complaints</span>
        </div>
      `;
    });
    container.innerHTML = html;
  } catch (err) {
    console.error("Failed to load analytics trends:", err);
  }
}
