/**
 * complaint-detail.js - Handles viewing single complaint detail and updating status / department
 */
let currentComplaintId = null;

document.addEventListener("DOMContentLoaded", () => {
  const urlParams = new URLSearchParams(window.location.search);
  currentComplaintId = urlParams.get("id");

  if (!currentComplaintId) {
    showErrorState("No Complaint ID provided in URL.");
    return;
  }

  loadComplaintDetail(currentComplaintId);

  // Setup Action Handlers
  const saveStatusBtn = document.getElementById("btn-save-status");
  if (saveStatusBtn) {
    saveStatusBtn.addEventListener("click", updateStatus);
  }

  const saveDeptBtn = document.getElementById("btn-save-dept");
  if (saveDeptBtn) {
    saveDeptBtn.addEventListener("click", updateDepartment);
  }
});

async function loadComplaintDetail(id) {
  try {
    const data = await apiRequest(`/complaints/${id}`);

    // Populate Fields
    document.getElementById("detail-complaint-id").textContent = data.complaint_id;
    document.getElementById("detail-category").textContent = data.category || "Unclassified";
    document.getElementById("detail-description").textContent = data.description || "";
    document.getElementById("detail-location").textContent = data.location || "N/A";
    document.getElementById("detail-date").textContent = formatDate(data.date || data.created_at);
    document.getElementById("detail-ai-summary").textContent = data.ai_summary || "No summary generated.";

    // Badges & Departments
    const statusContainer = document.getElementById("detail-status-badge");
    if (statusContainer) statusContainer.innerHTML = getStatusBadge(data.status);

    const prioContainer = document.getElementById("detail-priority-badge");
    if (prioContainer) prioContainer.innerHTML = getPriorityBadge(data.priority);

    const deptEl = document.getElementById("detail-department");
    if (deptEl) deptEl.textContent = data.assigned_department || "Unassigned";

    // Set dropdown selections
    const statusSelect = document.getElementById("select-status");
    if (statusSelect) statusSelect.value = data.status || "Open";

    const deptSelect = document.getElementById("select-department");
    if (deptSelect && data.assigned_department) {
      deptSelect.value = data.assigned_department;
    }
  } catch (err) {
    console.error("Failed to load complaint detail:", err);
    showErrorState(`Complaint ID "${id}" could not be found.`);
  }
}

async function updateStatus() {
  const select = document.getElementById("select-status");
  const btn = document.getElementById("btn-save-status");
  const msgEl = document.getElementById("status-update-msg");

  if (!select || !currentComplaintId) return;

  const newStatus = select.value;
  const origText = btn.innerHTML;
  btn.innerHTML = `<span class="material-symbols-outlined animate-spin text-sm">progress_activity</span> Updating...`;
  btn.disabled = true;

  try {
    await apiRequest(`/complaints/${currentComplaintId}/status`, {
      method: "PATCH",
      body: JSON.stringify({ status: newStatus }),
    });

    if (msgEl) {
      msgEl.textContent = "Status updated successfully!";
      msgEl.className = "text-xs text-emerald-400 font-semibold mt-1";
      setTimeout(() => (msgEl.textContent = ""), 3000);
    }
    // Refresh page data to confirm
    await loadComplaintDetail(currentComplaintId);
  } catch (err) {
    if (msgEl) {
      msgEl.textContent = err.message || "Failed to update status.";
      msgEl.className = "text-xs text-rose-400 font-semibold mt-1";
    }
  } finally {
    btn.innerHTML = origText;
    btn.disabled = false;
  }
}

async function updateDepartment() {
  const select = document.getElementById("select-department");
  const btn = document.getElementById("btn-save-dept");
  const msgEl = document.getElementById("dept-update-msg");

  if (!select || !currentComplaintId) return;

  const newDept = select.value;
  const origText = btn.innerHTML;
  btn.innerHTML = `<span class="material-symbols-outlined animate-spin text-sm">progress_activity</span> Assigning...`;
  btn.disabled = true;

  try {
    await apiRequest(`/complaints/${currentComplaintId}/assign`, {
      method: "PATCH",
      body: JSON.stringify({ assigned_department: newDept }),
    });

    if (msgEl) {
      msgEl.textContent = "Department assigned successfully!";
      msgEl.className = "text-xs text-emerald-400 font-semibold mt-1";
      setTimeout(() => (msgEl.textContent = ""), 3000);
    }
    // Refresh page data to confirm
    await loadComplaintDetail(currentComplaintId);
  } catch (err) {
    if (msgEl) {
      msgEl.textContent = err.message || "Failed to reassign department.";
      msgEl.className = "text-xs text-rose-400 font-semibold mt-1";
    }
  } finally {
    btn.innerHTML = origText;
    btn.disabled = false;
  }
}

function showErrorState(msg) {
  const mainContainer = document.getElementById("detail-main-canvas");
  if (mainContainer) {
    mainContainer.innerHTML = `
      <div class="p-12 text-center bg-surface-container rounded-xl border border-outline-variant max-w-md mx-auto my-12">
        <span class="material-symbols-outlined text-5xl text-rose-400 mb-4">error</span>
        <h3 class="text-xl font-bold text-on-surface mb-2">Error Loading Complaint</h3>
        <p class="text-sm text-on-surface-variant mb-6">${msg}</p>
        <a href="/ui/admin-complaints.html" class="btn-primary px-6 py-2 text-sm font-semibold">
          Back to All Complaints
        </a>
      </div>
    `;
  }
}
