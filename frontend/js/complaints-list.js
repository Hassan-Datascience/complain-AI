/**
 * complaints-list.js - Handles filtering and table population for admin-complaints.html
 */
document.addEventListener("DOMContentLoaded", () => {
  const categoryFilter = document.getElementById("filter-category");
  const priorityFilter = document.getElementById("filter-priority");
  const statusFilter = document.getElementById("filter-status");
  const departmentFilter = document.getElementById("filter-department");
  const searchInput = document.getElementById("filter-search");

  // Load complaints initially
  fetchAndRenderComplaints();

  // Attach filter change listeners
  [categoryFilter, priorityFilter, statusFilter, departmentFilter].forEach((el) => {
    if (el) el.addEventListener("change", fetchAndRenderComplaints);
  });

  if (searchInput) {
    let timeout = null;
    searchInput.addEventListener("input", () => {
      clearTimeout(timeout);
      timeout = setTimeout(fetchAndRenderComplaints, 300);
    });
  }
});

async function fetchAndRenderComplaints() {
  const tbody = document.getElementById("complaints-tbody");
  const countDisplay = document.getElementById("complaints-count");
  if (!tbody) return;

  tbody.innerHTML = `<tr><td colspan="6" class="p-8 text-center text-on-surface-variant"><span class="material-symbols-outlined animate-spin text-2xl">progress_activity</span><p class="mt-2 text-xs">Loading complaints...</p></td></tr>`;

  try {
    const category = document.getElementById("filter-category")?.value || "";
    const priority = document.getElementById("filter-priority")?.value || "";
    const status = document.getElementById("filter-status")?.value || "";
    const department = document.getElementById("filter-department")?.value || "";
    const searchQuery = document.getElementById("filter-search")?.value.trim().toLowerCase() || "";

    // Build URL with backend parameters
    const params = new URLSearchParams();
    if (category) params.append("category", category);
    if (priority) params.append("priority", priority);
    if (status) params.append("status", status);
    if (department) params.append("department", department);

    const queryString = params.toString() ? `?${params.toString()}` : "";
    let data = await apiRequest(`/complaints${queryString}`);

    // Client-side text search filter if searchQuery provided
    if (searchQuery) {
      data = data.filter(c =>
        c.complaint_id.toLowerCase().includes(searchQuery) ||
        (c.description && c.description.toLowerCase().includes(searchQuery)) ||
        (c.location && c.location.toLowerCase().includes(searchQuery))
      );
    }

    if (countDisplay) countDisplay.textContent = `${data.length} Complaints`;

    if (data.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" class="p-8 text-center text-on-surface-variant">No matching complaints found.</td></tr>`;
      return;
    }

    let html = "";
    data.forEach((c) => {
      const dateStr = formatDate(c.date || c.created_at);
      const snippet = c.description.length > 60 ? c.description.substring(0, 60) + "..." : c.description;

      html += `
        <tr class="hover:bg-surface-variant/30 transition-colors group cursor-pointer" onclick="window.location.href='/ui/admin-complaint-detail.html?id=${c.complaint_id}'">
          <td class="p-4 font-label-sm text-label-sm font-mono text-primary font-bold">${c.complaint_id}</td>
          <td class="p-4 font-body-sm text-body-sm text-on-surface">${c.category || "Unclassified"}</td>
          <td class="p-4 font-body-sm text-body-sm text-on-surface-variant max-w-sm">${snippet}</td>
          <td class="p-4">${getPriorityBadge(c.priority)}</td>
          <td class="p-4">${getStatusBadge(c.status)}</td>
          <td class="p-4 font-body-sm text-body-sm text-on-surface-variant">${c.assigned_department || "Unassigned"}</td>
          <td class="p-4 text-right">
            <a href="/ui/admin-complaint-detail.html?id=${c.complaint_id}" class="btn-secondary px-3 py-1 text-xs">
              View
            </a>
          </td>
        </tr>
      `;
    });
    tbody.innerHTML = html;
  } catch (err) {
    console.error("Failed to fetch complaints list:", err);
    tbody.innerHTML = `<tr><td colspan="6" class="p-8 text-center text-error">Failed to load complaints. Please verify server connection.</td></tr>`;
  }
}
