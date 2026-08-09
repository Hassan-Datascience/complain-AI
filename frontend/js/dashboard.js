/**
 * dashboard.js - Handles fetching live metrics and complaints for admin-dashboard.html
 */
document.addEventListener("DOMContentLoaded", () => {
  loadDashboardKPIs();
  loadRecentComplaints();
});

async function loadDashboardKPIs() {
  try {
    const summary = await apiRequest("/analytics/summary");

    // KPI Cards
    const totalEl = document.getElementById("kpi-total");
    const openEl = document.getElementById("kpi-open");
    const progressEl = document.getElementById("kpi-progress");
    const resolvedEl = document.getElementById("kpi-resolved");
    const criticalEl = document.getElementById("kpi-critical");

    if (totalEl) totalEl.textContent = summary.total_complaints || 0;
    
    const statusDist = summary.status_distribution || {};
    if (openEl) openEl.textContent = statusDist["Open"] || 0;
    if (progressEl) progressEl.textContent = (statusDist["In Progress"] || 0) + (statusDist["Assigned"] || 0);
    if (resolvedEl) resolvedEl.textContent = statusDist["Resolved"] || 0;

    const prioDist = summary.priority_distribution || {};
    if (criticalEl) criticalEl.textContent = prioDist["Critical"] || 0;

    // Render Category Breakdown
    const catContainer = document.getElementById("category-breakdown-list");
    if (catContainer && summary.category_distribution) {
      const cats = summary.category_distribution;
      const total = summary.total_complaints || 1;
      let html = "";

      const colors = ["bg-primary-container", "bg-tertiary-container", "bg-secondary", "bg-blue-400", "bg-purple-400"];
      let idx = 0;
      for (const [cat, count] of Object.entries(cats)) {
        const pct = Math.round((count / total) * 100);
        const color = colors[idx % colors.length];
        html += `
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <div class="w-3 h-3 rounded-full ${color}"></div>
              <span class="font-label-sm text-label-sm text-on-surface-variant">${cat}</span>
            </div>
            <span class="font-label-sm text-label-sm font-semibold text-on-surface">${count} (${pct}%)</span>
          </div>
        `;
        idx++;
      }
      catContainer.innerHTML = html || `<p class="text-xs text-on-surface-variant">No data available.</p>`;
    }
  } catch (err) {
    console.error("Failed to load dashboard KPIs:", err);
  }
}

async function loadRecentComplaints() {
  const tbody = document.getElementById("recent-complaints-tbody");
  if (!tbody) return;

  try {
    const complaints = await apiRequest("/complaints");
    const recent = complaints.slice(0, 5); // Take top 5 latest

    if (recent.length === 0) {
      tbody.innerHTML = `<tr><td colspan="5" class="p-4 text-center text-on-surface-variant">No complaints recorded yet.</td></tr>`;
      return;
    }

    let html = "";
    recent.forEach((c) => {
      const snippet = c.description.length > 50 ? c.description.substring(0, 50) + "..." : c.description;
      html += `
        <tr class="hover:bg-surface-variant/30 transition-colors group cursor-pointer" onclick="window.location.href='/ui/admin-complaint-detail.html?id=${c.complaint_id}'">
          <td class="p-4 font-label-sm text-label-sm font-mono text-primary">${c.complaint_id}</td>
          <td class="p-4 font-body-sm text-body-sm text-on-surface">${c.category || "Unclassified"}</td>
          <td class="p-4 font-body-sm text-body-sm text-on-surface-variant max-w-xs truncate">${snippet}</td>
          <td class="p-4">${getStatusBadge(c.status)}</td>
          <td class="p-4 text-right">
            <a href="/ui/admin-complaint-detail.html?id=${c.complaint_id}" class="text-on-surface-variant hover:text-primary transition-colors">
              <span class="material-symbols-outlined text-sm">visibility</span>
            </a>
          </td>
        </tr>
      `;
    });
    tbody.innerHTML = html;
  } catch (err) {
    console.error("Failed to load recent complaints:", err);
    tbody.innerHTML = `<tr><td colspan="5" class="p-4 text-center text-error">Failed to load recent complaints.</td></tr>`;
  }
}
