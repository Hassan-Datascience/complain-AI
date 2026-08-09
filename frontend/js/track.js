/**
 * track.js
 * Citizen Complaints Dashboard (fetches logged-in citizen's complaints via GET /complaints/my)
 */

document.addEventListener("DOMContentLoaded", async () => {
  if (!checkAuth()) return;
  await loadMyComplaints();
});

async function loadMyComplaints() {
  const container = document.getElementById("my-complaints-list");
  if (!container) return;

  try {
    const complaints = await apiRequest("/complaints/my");

    if (!complaints || complaints.length === 0) {
      container.innerHTML = `
        <div class="surface-card rounded-xl p-10 text-center flex flex-col items-center gap-3">
          <span class="material-symbols-outlined text-4xl text-on-surface-variant">assignment_late</span>
          <h3 class="font-bold text-lg text-on-surface">No Complaints Submitted Yet</h3>
          <p class="text-xs text-on-surface-variant max-w-sm">You haven't reported any civic issues under this account. Click below to submit your first report.</p>
          <a href="/ui/index.html" class="btn-primary px-6 py-2.5 rounded text-xs font-semibold mt-2 inline-flex items-center gap-2">
            <span>Report an Issue</span>
            <span class="material-symbols-outlined text-sm">arrow_forward</span>
          </a>
        </div>
      `;
      return;
    }

    container.innerHTML = complaints.map(c => `
      <div class="surface-card rounded-xl p-6 flex flex-col gap-4">
        <div class="flex justify-between items-start border-b border-outline-variant/40 pb-3">
          <div>
            <span class="text-[10px] text-on-surface-variant uppercase font-mono font-semibold">COMPLAINT ID</span>
            <h3 class="text-lg font-bold text-primary font-mono">${c.complaint_id}</h3>
          </div>
          <div class="flex items-center gap-2">
            ${getStatusBadge(c.status)}
            ${getPriorityBadge(c.priority)}
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
          <div>
            <p class="text-on-surface-variant">Category</p>
            <p class="font-semibold text-on-surface">${c.category || 'Other'}</p>
          </div>
          <div>
            <p class="text-on-surface-variant">Assigned Department</p>
            <p class="font-semibold text-on-surface">${c.assigned_department || 'Unassigned'}</p>
          </div>
          <div>
            <p class="text-on-surface-variant">Submitted Date</p>
            <p class="text-on-surface">${formatDate(c.date)}</p>
          </div>
        </div>

        <div>
          <p class="text-xs text-on-surface-variant font-semibold mb-1">Location</p>
          <p class="text-xs text-on-surface">${c.location || 'N/A'}</p>
        </div>

        <div>
          <p class="text-xs text-on-surface-variant font-semibold mb-1">Description</p>
          <p class="text-xs text-on-surface-variant bg-surface-variant/30 p-3 rounded border border-outline-variant/30">${c.description}</p>
        </div>

        ${c.ai_summary ? `
          <div class="bg-primary/5 border border-primary/20 p-3 rounded">
            <p class="text-[11px] text-primary font-bold mb-1 flex items-center gap-1">
              <span class="material-symbols-outlined text-xs">auto_awesome</span> AI Actionable Summary
            </p>
            <p class="text-xs text-on-surface italic">${c.ai_summary}</p>
          </div>
        ` : ''}
      </div>
    `).join("");

  } catch (err) {
    container.innerHTML = `
      <div class="surface-card rounded-xl p-6 text-center text-rose-400 text-sm">
        Failed to load your complaints: ${err.message}
      </div>
    `;
  }
}
