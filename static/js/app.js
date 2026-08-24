const qs = (selector) => document.querySelector(selector);
const message = (text, type = "success") => { const box = qs("#message"); if (box) { box.textContent = text; box.className = `message ${type}`; } };
const api = async (url, options = {}) => { const res = await fetch(url, options); const data = await res.json().catch(() => ({})); if (!res.ok) throw data; return data; };
const formatDate = (value) => new Date(value).toLocaleString();

async function loadDashboard() {
  const table = qs("#ticketsTable");
  if (!table) return;
  const params = new URLSearchParams();
  ["search", "status", "priority", "category"].forEach((id) => { const value = qs(`#${id}`).value.trim(); if (value) params.set(id, value); });
  try {
    const data = await api(`/api/tickets?${params}`);
    qs("#total").textContent = data.summary.total;
    qs("#open").textContent = data.summary.open;
    qs("#inProgress").textContent = data.summary.in_progress;
    qs("#resolved").textContent = data.summary.resolved;
    qs("#highCritical").textContent = data.summary.high_critical;
    table.innerHTML = data.tickets.map((t) => `<tr><td><a href="/tickets/${t._id}">${t._id}</a></td><td>${t.name}<br><small>${t.email}</small></td><td>${t.category}</td><td>${t.priority}</td><td>${t.status}</td><td>${formatDate(t.created_at)}</td></tr>`).join("") || `<tr><td colspan="6">No tickets found.</td></tr>`;
  } catch (err) { message(err.message || err.error || "Could not load tickets.", "error"); }
}

async function loadTicketDetail() {
  const form = qs("#updateForm");
  if (!form) return;
  try {
    const { ticket } = await api(`/api/tickets/${form.dataset.ticketId}`);
    qs("#ticketTitle").textContent = `${ticket._id} — ${ticket.name}`;
    qs("#ticketDetails").innerHTML = Object.entries({Employee: ticket.name, Email: ticket.email, Category: ticket.category, Priority: ticket.priority, Status: ticket.status, Description: ticket.description, Resolution: ticket.resolution || "Not added", Created: formatDate(ticket.created_at), Updated: formatDate(ticket.updated_at)}).map(([k,v]) => `<dt>${k}</dt><dd>${v}</dd>`).join("");
    form.status.value = ticket.status; form.priority.value = ticket.priority; form.resolution.value = ticket.resolution || "";
  } catch (err) { message(err.error || "Ticket could not be loaded.", "error"); }
}

qs("#ticketForm")?.addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = Object.fromEntries(new FormData(event.target).entries());
  try { const data = await api("/api/tickets", {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(payload)}); message(`Created ${data.ticket._id}. Redirecting...`); setTimeout(() => location.href = `/tickets/${data.ticket._id}`, 800); }
  catch (err) { message(err.error ? `${err.error}: ${JSON.stringify(err.details || err.message)}` : "Ticket creation failed.", "error"); }
});

qs("#updateForm")?.addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.target;
  const payload = Object.fromEntries(new FormData(form).entries());
  try { await api(`/api/tickets/${form.dataset.ticketId}`, {method:"PUT", headers:{"Content-Type":"application/json"}, body:JSON.stringify(payload)}); message("Ticket updated successfully."); loadTicketDetail(); }
  catch (err) { message(err.error ? `${err.error}: ${JSON.stringify(err.details || err.message)}` : "Ticket update failed.", "error"); }
});

["search", "status", "priority", "category"].forEach((id) => qs(`#${id}`)?.addEventListener("input", loadDashboard));
loadDashboard();
loadTicketDetail();
