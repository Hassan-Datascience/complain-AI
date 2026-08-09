/**
 * Shared API Helper & Auth Manager for AI Smart Civic Services Frontend
 */
const API_BASE = window.location.origin.includes("127.0.0.1") || window.location.origin.includes("localhost")
  ? window.location.origin
  : "http://127.0.0.1:8000";

async function apiRequest(path, options = {}) {
  try {
    const token = localStorage.getItem("token");
    const headers = {
      "Content-Type": "application/json",
      ...(options.headers || {})
    };
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const res = await fetch(`${path.startsWith('/') ? path : '/' + path}`, {
      ...options,
      headers
    });

    if (res.status === 401) {
      // Clear token and redirect to appropriate login
      localStorage.removeItem("token");
      localStorage.removeItem("role");
      localStorage.removeItem("name");
      localStorage.removeItem("email");

      const isAdminPage = window.location.pathname.includes("admin-");
      window.location.href = isAdminPage ? "/ui/admin-login.html" : "/ui/citizen-login.html";
      throw new Error("Session expired or unauthenticated. Redirecting to login.");
    }

    if (!res.ok) {
      const errBody = await res.json().catch(() => ({}));
      let msg = errBody.detail || `Request failed with status ${res.status}`;
      if (Array.isArray(errBody.detail)) {
        msg = errBody.detail.map(e => `${e.loc?.join('.') || ''}: ${e.msg}`).join(', ');
      }
      throw new Error(msg);
    }
    return await res.json();
  } catch (err) {
    console.error("API Error:", err);
    throw err;
  }
}

// Global Auth Guard helper for page headers
function checkAuth(requiredRole = null) {
  const token = localStorage.getItem("token");
  const role = localStorage.getItem("role");

  if (!token) {
    if (requiredRole === "admin") {
      window.location.href = "/ui/admin-login.html";
    } else {
      window.location.href = "/ui/citizen-login.html";
    }
    return false;
  }

  if (requiredRole && role !== requiredRole) {
    if (requiredRole === "admin") {
      window.location.href = "/ui/admin-login.html";
    } else {
      window.location.href = "/ui/citizen-login.html";
    }
    return false;
  }

  return true;
}

// User Navigation Logout / Profile Header Injector
function setupAuthNav() {
  const token = localStorage.getItem("token");
  const name = localStorage.getItem("name") || "User";
  const role = localStorage.getItem("role") || "citizen";

  const userNavContainer = document.getElementById("user-nav-container");
  if (userNavContainer) {
    if (token) {
      userNavContainer.innerHTML = `
        <div class="flex items-center gap-3">
          <div class="flex items-center gap-1.5 text-xs text-on-surface bg-surface-variant/50 px-3 py-1.5 rounded-full border border-outline-variant/40">
            <span class="material-symbols-outlined text-sm text-primary">account_circle</span>
            <span class="font-semibold">${name}</span>
            <span class="text-[10px] text-primary uppercase font-mono px-1 bg-primary/10 rounded">${role}</span>
          </div>
          <button onclick="logout()" class="text-xs font-semibold px-3 py-1.5 rounded bg-rose-500/20 text-rose-300 hover:bg-rose-500/30 transition-colors flex items-center gap-1">
            <span class="material-symbols-outlined text-sm">logout</span>
            <span>Logout</span>
          </button>
        </div>
      `;
    } else {
      userNavContainer.innerHTML = `
        <a href="/ui/citizen-login.html" class="text-xs font-semibold px-3 py-1.5 rounded bg-surface-variant text-on-surface hover:bg-surface-container-highest transition-colors">
          Sign In
        </a>
      `;
    }
  }
}

function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("role");
  localStorage.removeItem("name");
  localStorage.removeItem("email");
  window.location.href = "/ui/citizen-login.html";
}

// Formatting utilities
function formatDate(isoStr) {
  if (!isoStr) return "N/A";
  try {
    const d = new Date(isoStr);
    return d.toLocaleDateString(undefined, {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit"
    });
  } catch (e) {
    return isoStr;
  }
}

function getStatusBadge(status) {
  const s = (status || "Open").toLowerCase();
  if (s === "resolved") {
    return `<span class="px-2.5 py-1 text-xs font-semibold rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">Resolved</span>`;
  } else if (s === "in progress") {
    return `<span class="px-2.5 py-1 text-xs font-semibold rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20">In Progress</span>`;
  } else if (s === "assigned") {
    return `<span class="px-2.5 py-1 text-xs font-semibold rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20">Assigned</span>`;
  } else {
    return `<span class="px-2.5 py-1 text-xs font-semibold rounded-full bg-slate-500/10 text-slate-300 border border-slate-500/20">Open</span>`;
  }
}

function getPriorityBadge(priority) {
  const p = (priority || "Medium").toLowerCase();
  if (p === "critical") {
    return `<span class="px-2.5 py-1 text-xs font-bold rounded-full bg-rose-500/20 text-rose-400 border border-rose-500/30">Critical</span>`;
  } else if (p === "high") {
    return `<span class="px-2.5 py-1 text-xs font-semibold rounded-full bg-orange-500/20 text-orange-400 border border-orange-500/30">High</span>`;
  } else if (p === "medium") {
    return `<span class="px-2.5 py-1 text-xs font-semibold rounded-full bg-yellow-500/20 text-yellow-400 border border-yellow-500/30">Medium</span>`;
  } else {
    return `<span class="px-2.5 py-1 text-xs font-semibold rounded-full bg-slate-500/20 text-slate-400 border border-slate-500/30">Low</span>`;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  setupAuthNav();
});
