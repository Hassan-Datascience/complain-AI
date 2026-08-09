/**
 * submit.js - Handles logic for index.html (Submit Complaint)
 */
document.addEventListener("DOMContentLoaded", () => {
  const submitBtn = document.getElementById("submit-btn");
  const descriptionInput = document.getElementById("description");
  const locationInput = document.getElementById("location");

  const formView = document.getElementById("form-view");
  const successView = document.getElementById("success-view");

  const errorBoxId = "inline-error-msg";

  function showError(msg) {
    let errorBox = document.getElementById(errorBoxId);
    if (!errorBox) {
      errorBox = document.createElement("div");
      errorBox.id = errorBoxId;
      errorBox.className = "p-4 mb-4 text-sm rounded-lg bg-rose-500/10 text-rose-400 border border-rose-500/20";
      descriptionInput.parentNode.insertBefore(errorBox, descriptionInput);
    }
    errorBox.textContent = msg;
    errorBox.classList.remove("hidden");
  }

  function clearError() {
    const errorBox = document.getElementById(errorBoxId);
    if (errorBox) errorBox.classList.add("hidden");
  }

  if (submitBtn) {
    submitBtn.addEventListener("click", async (e) => {
      e.preventDefault();
      clearError();

      const description = descriptionInput.value.trim();
      const location = locationInput ? locationInput.value.trim() : "";

      if (description.length < 10) {
        showError("Description must be at least 10 characters long.");
        return;
      }

      const originalBtnHTML = submitBtn.innerHTML;
      submitBtn.innerHTML = `<span class="material-symbols-outlined animate-spin text-[18px]">progress_activity</span><span>Analyzing & Submitting...</span>`;
      submitBtn.disabled = true;

      try {
        const payload = {
          description,
          location: location || "Not specified",
        };

        const response = await apiRequest("/complaints", {
          method: "POST",
          body: JSON.stringify(payload),
        });

        // Populate success view
        document.getElementById("res-complaint-id").textContent = `#${response.complaint_id}`;
        document.getElementById("res-category").textContent = response.category;
        document.getElementById("res-assigned-dept").textContent = response.assigned_department || "Pending";
        
        const priorityContainer = document.getElementById("res-priority-badge");
        if (priorityContainer) {
          priorityContainer.innerHTML = getPriorityBadge(response.priority);
        }

        const summaryEl = document.getElementById("res-ai-summary");
        if (summaryEl) {
          summaryEl.textContent = response.ai_summary || description;
        }

        const trackLink = document.getElementById("res-track-link");
        if (trackLink) {
          trackLink.href = `/ui/track.html?id=${response.complaint_id}`;
        }

        formView.classList.add("hidden");
        successView.classList.remove("hidden");

        // Clear input fields
        descriptionInput.value = "";
        if (locationInput) locationInput.value = "";
      } catch (err) {
        showError(err.message || "Failed to submit report. Please check server connection.");
      } finally {
        submitBtn.innerHTML = originalBtnHTML;
        submitBtn.disabled = false;
      }
    });
  }
});

function resetForm() {
  const formView = document.getElementById("form-view");
  const successView = document.getElementById("success-view");
  if (formView && successView) {
    successView.classList.add("hidden");
    formView.classList.remove("hidden");
  }
}
