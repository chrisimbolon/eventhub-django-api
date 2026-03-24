// src/hooks/useMICE.js
// Matches the exact pattern of hooks/useEvents.js
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  activateMICEProject,
  bulkCreateStandardSections,
  completeTask,
  createLineItem,
  createMICEProject,
  createQuotation,
  createQuotationRevision,
  createSection,
  createSubEvent,
  createTask,
  createVendor,
  deleteAsset,
  deleteLineItem,
  deleteSection,
  deleteSubEvent,
  fetchAssetsByType,
  fetchMICEProject,
  fetchMICEProjectDashboard,
  fetchMICEProjects,
  fetchQuotation,
  fetchQuotations,
  fetchTasks,
  fetchVendors,
  markPaymentReceived,
  recalculateQuotation,
  sendQuotationToClient,
  toggleAssetVisibility,
  updateLineItem,
  updateMICEProject,
  updateQuotation,
  updateSection,
  updateSubEvent,
  updateTask,
  uploadAsset,
} from "../api/mice";

// ── MICE Projects ─────────────────────────────────────────────────────────────

export const useMICEProjects = (params) =>
  useQuery({
    queryKey: ["mice-projects", params],
    queryFn: () => fetchMICEProjects(params),
    select: (data) => {
      if (Array.isArray(data)) return data;
      return data?.results || [];
    },
    placeholderData: (prev) => prev,
  });

export const useMICEProject = (id) =>
  useQuery({
    queryKey: ["mice-project", id],
    queryFn: () => fetchMICEProject(id),
    enabled: !!id,
  });

export const useMICEProjectDashboard = (id) =>
  useQuery({
    queryKey: ["mice-project-dashboard", id],
    queryFn: () => fetchMICEProjectDashboard(id),
    enabled: !!id,
    refetchInterval: 30000, // Refresh every 30s for live updates
  });

export const useCreateMICEProject = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: createMICEProject,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["mice-projects"] });
    },
  });
};

export const useUpdateMICEProject = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }) => updateMICEProject(id, data),
    onSuccess: (_, variables) => {
      qc.invalidateQueries({ queryKey: ["mice-project", variables.id] });
      qc.invalidateQueries({ queryKey: ["mice-projects"] });
    },
  });
};

export const useActivateMICEProject = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: activateMICEProject,
    onSuccess: (_, id) => {
      qc.invalidateQueries({ queryKey: ["mice-project", id] });
      qc.invalidateQueries({ queryKey: ["mice-projects"] });
    },
  });
};

// ── Sub-Events ────────────────────────────────────────────────────────────────

export const useCreateSubEvent = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ projectId, data }) => createSubEvent(projectId, data),
    onSuccess: (_, variables) => {
      qc.invalidateQueries({ queryKey: ["mice-project", variables.projectId] });
    },
  });
};

export const useUpdateSubEvent = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ projectId, subEventId, data }) =>
      updateSubEvent(projectId, subEventId, data),
    onSuccess: (_, variables) => {
      qc.invalidateQueries({ queryKey: ["mice-project", variables.projectId] });
    },
  });
};

export const useDeleteSubEvent = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ projectId, subEventId }) =>
      deleteSubEvent(projectId, subEventId),
    onSuccess: (_, variables) => {
      qc.invalidateQueries({ queryKey: ["mice-project", variables.projectId] });
    },
  });
};

// ── Quotations ────────────────────────────────────────────────────────────────

export const useQuotations = (projectId) =>
  useQuery({
    queryKey: ["mice-quotations", projectId],
    queryFn: () => fetchQuotations(projectId),
    enabled: !!projectId,
    select: (data) => {
      if (Array.isArray(data)) return data;
      return data?.results || [];
    },
  });

export const useQuotation = (id) =>
  useQuery({
    queryKey: ["mice-quotation", id],
    queryFn: () => fetchQuotation(id),
    enabled: !!id,
  });

export const useCreateQuotation = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: createQuotation,
    onSuccess: (data) => {
      qc.invalidateQueries({
        queryKey: ["mice-quotations", data.mice_project],
      });
    },
  });
};

export const useUpdateQuotation = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }) => updateQuotation(id, data),
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: ["mice-quotation", data.id] });
    },
  });
};

export const useRecalculateQuotation = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: recalculateQuotation,
    onSuccess: (data) => {
      qc.setQueryData(["mice-quotation", data.id], data);
    },
  });
};

export const useSendQuotationToClient = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: sendQuotationToClient,
    onSuccess: (_, id) => {
      qc.invalidateQueries({ queryKey: ["mice-quotation", id] });
    },
  });
};

export const useCreateQuotationRevision = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: createQuotationRevision,
    onSuccess: (data) => {
      qc.invalidateQueries({
        queryKey: ["mice-quotations", data.mice_project],
      });
    },
  });
};

export const useMarkPaymentReceived = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, term }) => markPaymentReceived(id, term),
    onSuccess: (_, variables) => {
      qc.invalidateQueries({ queryKey: ["mice-quotation", variables.id] });
    },
  });
};

// ── Sections ──────────────────────────────────────────────────────────────────

export const useCreateSection = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ quotationId, data }) => createSection(quotationId, data),
    onSuccess: (_, variables) => {
      qc.invalidateQueries({
        queryKey: ["mice-quotation", variables.quotationId],
      });
    },
  });
};

export const useUpdateSection = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ quotationId, sectionId, data }) =>
      updateSection(quotationId, sectionId, data),
    onSuccess: (_, variables) => {
      qc.invalidateQueries({
        queryKey: ["mice-quotation", variables.quotationId],
      });
    },
  });
};

export const useDeleteSection = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ quotationId, sectionId }) =>
      deleteSection(quotationId, sectionId),
    onSuccess: (_, variables) => {
      qc.invalidateQueries({
        queryKey: ["mice-quotation", variables.quotationId],
      });
    },
  });
};

export const useBulkCreateStandardSections = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: bulkCreateStandardSections,
    onSuccess: (_, quotationId) => {
      qc.invalidateQueries({ queryKey: ["mice-quotation", quotationId] });
    },
  });
};

// ── Line Items ────────────────────────────────────────────────────────────────

export const useCreateLineItem = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ quotationId, sectionId, data }) =>
      createLineItem(quotationId, sectionId, data),
    onSuccess: (_, variables) => {
      qc.invalidateQueries({
        queryKey: ["mice-quotation", variables.quotationId],
      });
    },
  });
};

export const useUpdateLineItem = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ quotationId, sectionId, itemId, data }) =>
      updateLineItem(quotationId, sectionId, itemId, data),
    onSuccess: (_, variables) => {
      qc.invalidateQueries({
        queryKey: ["mice-quotation", variables.quotationId],
      });
    },
  });
};

export const useDeleteLineItem = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ quotationId, sectionId, itemId }) =>
      deleteLineItem(quotationId, sectionId, itemId),
    onSuccess: (_, variables) => {
      qc.invalidateQueries({
        queryKey: ["mice-quotation", variables.quotationId],
      });
    },
  });
};

// ── Vendors ───────────────────────────────────────────────────────────────────

export const useVendors = (params) =>
  useQuery({
    queryKey: ["mice-vendors", params],
    queryFn: () => fetchVendors(params),
    select: (data) => {
      if (Array.isArray(data)) return data;
      return data?.results || [];
    },
    placeholderData: (prev) => prev,
  });

export const useCreateVendor = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: createVendor,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["mice-vendors"] });
    },
  });
};

// ── Tasks ─────────────────────────────────────────────────────────────────────

export const useTasks = (projectId) =>
  useQuery({
    queryKey: ["mice-tasks", projectId],
    queryFn: () => fetchTasks(projectId),
    enabled: !!projectId,
    select: (data) => {
      if (Array.isArray(data)) return data;
      return data?.results || [];
    },
  });

export const useCreateTask = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: createTask,
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: ["mice-tasks", data.mice_project] });
    },
  });
};

export const useUpdateTask = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }) => updateTask(id, data),
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: ["mice-tasks", data.mice_project] });
    },
  });
};

export const useCompleteTask = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: completeTask,
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: ["mice-tasks", data.mice_project] });
    },
  });
};

// ── Assets ────────────────────────────────────────────────────────────────────

export const useAssetsByType = (projectId) =>
  useQuery({
    queryKey: ['mice-assets', projectId],
    queryFn:  () => fetchAssetsByType(projectId),
    enabled:  !!projectId,
  });

export const useUploadAsset = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ projectId, formData }) => uploadAsset(projectId, formData),
    onSuccess: (_, variables) => {
      qc.invalidateQueries({ queryKey: ['mice-assets', variables.projectId] });
      qc.invalidateQueries({ queryKey: ['mice-project', variables.projectId] });
    },
  });
};

export const useToggleAssetVisibility = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ projectId, assetId }) => toggleAssetVisibility(projectId, assetId),
    onSuccess: (_, variables) => {
      qc.invalidateQueries({ queryKey: ['mice-assets', variables.projectId] });
    },
  });
};

export const useDeleteAsset = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ projectId, assetId }) => deleteAsset(projectId, assetId),
    onSuccess: (_, variables) => {
      qc.invalidateQueries({ queryKey: ['mice-assets', variables.projectId] });
    },
  });
};
