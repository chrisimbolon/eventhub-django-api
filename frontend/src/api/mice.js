// src/api/mice.js
// Matches the exact pattern of api/events.js
import api from "./client";

// ── MICE Projects ─────────────────────────────────────────────────────────────

export const fetchMICEProjects = (params) =>
  api.get("/mice/projects/", { params }).then((r) => r.data);

export const fetchMICEProject = (id) =>
  api.get(`/mice/projects/${id}/`).then((r) => r.data);

export const fetchMICEProjectDashboard = (id) =>
  api.get(`/mice/projects/${id}/dashboard/`).then((r) => r.data);

export const createMICEProject = (data) =>
  api.post("/mice/projects/", data).then((r) => r.data);

export const updateMICEProject = (id, data) =>
  api.patch(`/mice/projects/${id}/`, data).then((r) => r.data);

export const activateMICEProject = (id) =>
  api.post(`/mice/projects/${id}/activate/`).then((r) => r.data);

// ── Sub-Events ────────────────────────────────────────────────────────────────

export const fetchSubEvents = (projectId) =>
  api.get(`/mice/projects/${projectId}/sub-events/`).then((r) => r.data);

export const createSubEvent = (projectId, data) =>
  api.post(`/mice/projects/${projectId}/sub-events/`, data).then((r) => r.data);

export const updateSubEvent = (projectId, subEventId, data) =>
  api
    .patch(`/mice/projects/${projectId}/sub-events/${subEventId}/`, data)
    .then((r) => r.data);

export const deleteSubEvent = (projectId, subEventId) =>
  api.delete(`/mice/projects/${projectId}/sub-events/${subEventId}/`);

// ── Quotations ────────────────────────────────────────────────────────────────

export const fetchQuotations = (projectId) =>
  api.get("/mice/quotations/", { params: { project: projectId } }).then((r) => r.data);

export const fetchQuotation = (id) =>
  api.get(`/mice/quotations/${id}/`).then((r) => r.data);

export const createQuotation = (data) =>
  api.post("/mice/quotations/", data).then((r) => r.data);

export const updateQuotation = (id, data) =>
  api.patch(`/mice/quotations/${id}/`, data).then((r) => r.data);

export const recalculateQuotation = (id) =>
  api.post(`/mice/quotations/${id}/recalculate/`).then((r) => r.data);

export const sendQuotationToClient = (id) =>
  api.post(`/mice/quotations/${id}/send-to-client/`).then((r) => r.data);

export const createQuotationRevision = (id) =>
  api.post(`/mice/quotations/${id}/create-revision/`).then((r) => r.data);

export const markPaymentReceived = (id, term) =>
  api.post(`/mice/quotations/${id}/mark-payment-received/`, { term }).then((r) => r.data);

// ── Quotation Sections ────────────────────────────────────────────────────────

export const fetchSections = (quotationId) =>
  api.get(`/mice/quotations/${quotationId}/sections/`).then((r) => r.data);

export const createSection = (quotationId, data) =>
  api.post(`/mice/quotations/${quotationId}/sections/`, data).then((r) => r.data);

export const updateSection = (quotationId, sectionId, data) =>
  api
    .patch(`/mice/quotations/${quotationId}/sections/${sectionId}/`, data)
    .then((r) => r.data);

export const deleteSection = (quotationId, sectionId) =>
  api.delete(`/mice/quotations/${quotationId}/sections/${sectionId}/`);

export const bulkCreateStandardSections = (quotationId) =>
  api
    .post(`/mice/quotations/${quotationId}/sections/bulk-create-from-template/`)
    .then((r) => r.data);

// ── Line Items ────────────────────────────────────────────────────────────────

export const createLineItem = (quotationId, sectionId, data) =>
  api
    .post(`/mice/quotations/${quotationId}/sections/${sectionId}/items/`, data)
    .then((r) => r.data);

export const updateLineItem = (quotationId, sectionId, itemId, data) =>
  api
    .patch(
      `/mice/quotations/${quotationId}/sections/${sectionId}/items/${itemId}/`,
      data
    )
    .then((r) => r.data);

export const deleteLineItem = (quotationId, sectionId, itemId) =>
  api.delete(
    `/mice/quotations/${quotationId}/sections/${sectionId}/items/${itemId}/`
  );

export const bulkCreateLineItems = (quotationId, sectionId, items) =>
  api
    .post(
      `/mice/quotations/${quotationId}/sections/${sectionId}/items/bulk-create/`,
      { items }
    )
    .then((r) => r.data);

// ── Vendors ───────────────────────────────────────────────────────────────────

export const fetchVendors = (params) =>
  api.get("/mice/vendors/", { params }).then((r) => r.data);

export const createVendor = (data) =>
  api.post("/mice/vendors/", data).then((r) => r.data);

// ── Tasks ─────────────────────────────────────────────────────────────────────

export const fetchTasks = (projectId) =>
  api.get("/mice/tasks/", { params: { project: projectId } }).then((r) => r.data);

export const createTask = (data) =>
  api.post("/mice/tasks/", data).then((r) => r.data);

export const updateTask = (id, data) =>
  api.patch(`/mice/tasks/${id}/`, data).then((r) => r.data);

export const completeTask = (id) =>
  api.post(`/mice/tasks/${id}/complete/`).then((r) => r.data);

// ── Client Portal (public) ────────────────────────────────────────────────────

export const fetchClientPortal = (token) =>
  api.get(`/mice/quotation/portal/${token}/`).then((r) => r.data);

export const approveQuotationAsClient = (token) =>
  api.post(`/mice/quotation/portal/${token}/approve/`).then((r) => r.data);


// ── Project Assets ────────────────────────────────────────────────────────────

export const fetchAssetsByType = (projectId) =>
  api.get(`/mice/projects/${projectId}/assets/by-type/`).then((r) => r.data);

export const uploadAsset = (projectId, formData) =>
  api.post(`/mice/projects/${projectId}/assets/`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }).then((r) => r.data);

export const toggleAssetVisibility = (projectId, assetId) =>
  api.patch(`/mice/projects/${projectId}/assets/${assetId}/toggle-visibility/`)
    .then((r) => r.data);

export const deleteAsset = (projectId, assetId) =>
  api.delete(`/mice/projects/${projectId}/assets/${assetId}/`);
