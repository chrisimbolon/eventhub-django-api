// src/pages/MICEProjectDetailPage.jsx
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";
import {
  useActivateMICEProject,
  useCreateQuotation,
  useCreateSubEvent,
  useMICEProject,
} from "@/hooks/useMICE";
import {
  ArrowLeft,
  Building2,
  Calendar,
  CheckCircle2,
  ChevronRight,
  Clock,
  FileText, FolderOpen, Mail,
  Phone,
  Plus,
  Rocket,
  User,
  Zap
} from "lucide-react";
import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

const IDR = (val) =>
  new Intl.NumberFormat("id-ID", {
    style: "currency", currency: "IDR",
    maximumFractionDigits: 0,
  }).format(val ?? 0);

const STATUS_CONFIG = {
  draft:     { label: "Draft",      className: "bg-slate-100 text-slate-600" },
  quoted:    { label: "Terkirim",   className: "bg-blue-50 text-blue-700" },
  approved:  { label: "Disetujui", className: "bg-emerald-50 text-emerald-700" },
  active:    { label: "Aktif",      className: "bg-green-50 text-green-700" },
  completed: { label: "Selesai",    className: "bg-slate-50 text-slate-500" },
  cancelled: { label: "Batal",      className: "bg-red-50 text-red-600" },
};

function InfoRow({ icon: Icon, label, value }) {
  if (!value) return null;
  return (
    <div className="flex items-center gap-3 text-sm">
      <Icon size={14} className="text-slate-400 shrink-0" />
      <span className="text-slate-400 w-20 shrink-0">{label}</span>
      <span className="text-slate-700 font-medium">{value}</span>
    </div>
  );
}

function SubEventCard({ subEvent }) {
  return (
    <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg border border-slate-100">
      <div>
        <p className="text-sm font-medium text-slate-800">{subEvent.title}</p>
        {subEvent.venue_name && (
          <p className="text-xs text-slate-400 mt-0.5">{subEvent.venue_name}</p>
        )}
        {subEvent.start_datetime && (
          <p className="text-xs text-slate-400">
            {new Date(subEvent.start_datetime).toLocaleDateString("id-ID", {
              day: "numeric", month: "short", year: "numeric",
            })}
          </p>
        )}
      </div>
      <div className="text-right">
        <p className="text-xs text-slate-400">Kapasitas</p>
        <p className="text-sm font-semibold text-slate-700">{subEvent.capacity} pax</p>
      </div>
    </div>
  );
}

function QuotationCard({ quotation, projectId }) {
  const navigate = useNavigate();
  const statusMap = {
    draft:      { label: "Draft",      className: "bg-slate-100 text-slate-500" },
    sent:       { label: "Terkirim",   className: "bg-blue-50 text-blue-600" },
    approved:   { label: "Disetujui", className: "bg-emerald-50 text-emerald-600" },
    rejected:   { label: "Ditolak",   className: "bg-red-50 text-red-600" },
    superseded: { label: "Diganti",   className: "bg-slate-50 text-slate-400" },
  };
  const s = statusMap[quotation.status] ?? statusMap.draft;

  return (
    <div
      className="flex items-center justify-between p-3 bg-white rounded-lg border hover:border-slate-300 cursor-pointer transition-colors"
      onClick={() => navigate(`/mice/quotation/${quotation.id}`)}
    >
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-slate-900 flex items-center justify-center text-white text-xs font-bold">
          R{quotation.revision}
        </div>
        <div>
          <p className="text-sm font-medium text-slate-800">
            Revision {quotation.revision}
          </p>
          <span className={`text-xs px-2 py-0.5 rounded-full ${s.className}`}>
            {s.label}
          </span>
        </div>
      </div>
      <div className="flex items-center gap-4">
        <div className="text-right hidden sm:block">
          <p className="text-xs text-slate-400">Total Klien</p>
          <p className="text-sm font-bold font-mono text-emerald-600">
            {IDR(quotation.total_after_tax)}
          </p>
        </div>
        <ChevronRight size={16} className="text-slate-300" />
      </div>
    </div>
  );
}

export default function MICEProjectDetailPage() {
  const { projectId }   = useParams();
  const navigate        = useNavigate();
  const { toast }       = useToast();
  const { data: project, isLoading } = useMICEProject(projectId);
  const createQuotation = useCreateQuotation();
  const createSubEvent  = useCreateSubEvent();
  const activate        = useActivateMICEProject();

  const [showSubEventForm, setShowSubEventForm] = useState(false);
  const [subEventForm, setSubEventForm] = useState({
    title: "", venue_name: "", capacity: "", start_datetime: "", end_datetime: "",
  });

  if (isLoading) return (
    <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-800" />
    </div>
  );

  if (!project) return (
    <div className="text-center py-20 text-slate-400">Project tidak ditemukan.</div>
  );

  const statusCfg = STATUS_CONFIG[project.status] ?? STATUS_CONFIG.draft;

  const handleCreateQuotation = () => {
    createQuotation.mutate(
      { mice_project: project.id },
      {
        onSuccess: (data) => {
          toast({ title: "Quotation berhasil dibuat!" });
          navigate(`/mice/quotation/${data.id}`);
        },
        onError: () => toast({ title: "Gagal membuat quotation", variant: "destructive" }),
      }
    );
  };

  const handleAddSubEvent = (e) => {
    e.preventDefault();
    createSubEvent.mutate(
      { projectId: project.id, data: subEventForm },
      {
        onSuccess: () => {
          toast({ title: "Sub-event ditambahkan!" });
          setShowSubEventForm(false);
          setSubEventForm({ title: "", venue_name: "", capacity: "", start_datetime: "", end_datetime: "" });
        },
        onError: () => toast({ title: "Gagal menambah sub-event", variant: "destructive" }),
      }
    );
  };

  const handleActivate = () => {
    if (!confirm("Aktifkan project? Ini akan membuat TicketTier untuk setiap sub-event.")) return;
    activate.mutate(project.id, {
      onSuccess: () => toast({ title: "Project berhasil diaktifkan! 🚀" }),
      onError: (err) => toast({
        title: err?.response?.data?.detail || "Gagal mengaktifkan",
        variant: "destructive",
      }),
    });
  };

  return (
    <div className="space-y-6 max-w-6xl">

      {/* Header */}
      <div>
        <button
          onClick={() => navigate("/mice/projects")}
          className="flex items-center gap-1.5 text-sm text-slate-400 hover:text-slate-600 mb-4 transition-colors"
        >
          <ArrowLeft size={14} />
          Kembali ke Projects
        </button>

        <div className="flex items-start justify-between gap-4 flex-wrap">
          <div>
            <div className="flex items-center gap-3 mb-1">
              <h1 className="text-2xl font-bold text-slate-900">
                {project.event_title}
              </h1>
              <span className={`text-xs font-medium px-2.5 py-1 rounded-full ${statusCfg.className}`}>
                {statusCfg.label}
              </span>
            </div>
            <p className="text-sm text-slate-500">
              {project.quotation_number} · {project.client_company}
            </p>
          </div>

          <div className="flex items-center gap-2">
            {project.status === "approved" && (
              <Button
                onClick={handleActivate}
                disabled={activate.isPending}
                className="bg-emerald-600 hover:bg-emerald-700 gap-2"
                size="sm"
              >
                <Rocket size={14} />
                Aktifkan Project
              </Button>
            )}
            <Button
              onClick={handleCreateQuotation}
              disabled={createQuotation.isPending}
              className="bg-slate-900 hover:bg-slate-700 gap-2"
              size="sm"
            >
              <FileText size={14} />
              {createQuotation.isPending ? "Membuat..." : "Buat Quotation"}
            </Button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* Left column */}
        <div className="lg:col-span-1 space-y-4">

          {/* Client info */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-semibold text-slate-600 uppercase tracking-wide">
                Informasi Klien
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2.5">
              <InfoRow icon={Building2} label="Perusahaan" value={project.client_company} />
              <InfoRow icon={User} label="PIC" value={project.client_pic} />
              <InfoRow icon={Mail} label="Email" value={project.client_email} />
              <InfoRow icon={Phone} label="Telepon" value={project.client_phone} />
            </CardContent>
          </Card>

          {/* Event info */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-semibold text-slate-600 uppercase tracking-wide">
                Detail Event
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2.5">
              <InfoRow icon={Calendar} label="Mulai" value={
                project.event_start
                  ? new Date(project.event_start).toLocaleDateString("id-ID", { day: "numeric", month: "long", year: "numeric" })
                  : null
              } />
              <InfoRow icon={Calendar} label="Selesai" value={
                project.event_end
                  ? new Date(project.event_end).toLocaleDateString("id-ID", { day: "numeric", month: "long", year: "numeric" })
                  : null
              } />
              <InfoRow icon={Building2} label="Venue" value={project.event_venue} />
              <InfoRow icon={Building2} label="Kota" value={project.event_city} />
            </CardContent>
          </Card>

          {/* Task summary */}
          {project.tasks?.length > 0 && (
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-semibold text-slate-600 uppercase tracking-wide">
                  Tasks
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {project.tasks.slice(0, 5).map(task => (
                    <div key={task.id} className="flex items-center gap-2 text-sm">
                      {task.status === "done"
                        ? <CheckCircle2 size={14} className="text-emerald-500 shrink-0" />
                        : task.is_overdue
                        ? <Clock size={14} className="text-red-400 shrink-0" />
                        : <div className="w-3.5 h-3.5 rounded-full border-2 border-slate-300 shrink-0" />
                      }
                      <span className={`truncate ${task.status === "done" ? "text-slate-400 line-through" : "text-slate-700"}`}>
                        {task.title}
                      </span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Right column */}
        <div className="lg:col-span-2 space-y-4">

          {/* Sub-events */}
          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm font-semibold text-slate-600 uppercase tracking-wide">
                  Sub-Events ({project.sub_events?.length ?? 0})
                </CardTitle>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-7 text-xs gap-1"
                  onClick={() => setShowSubEventForm(s => !s)}
                >
                  <Plus size={12} />
                  Tambah
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-2">
              {showSubEventForm && (
                <form onSubmit={handleAddSubEvent} className="p-3 bg-slate-50 rounded-lg border border-slate-200 space-y-3 mb-3">
                  <div className="grid grid-cols-2 gap-2">
                    <div className="col-span-2">
                      <Label className="text-xs mb-1 block">Nama Sub-Event *</Label>
                      <Input
                        value={subEventForm.title}
                        onChange={e => setSubEventForm(f => ({ ...f, title: e.target.value }))}
                        placeholder="e.g. Welcome Dinner"
                        className="h-8 text-sm"
                        required
                      />
                    </div>
                    <div>
                      <Label className="text-xs mb-1 block">Venue</Label>
                      <Input
                        value={subEventForm.venue_name}
                        onChange={e => setSubEventForm(f => ({ ...f, venue_name: e.target.value }))}
                        placeholder="Nama venue"
                        className="h-8 text-sm"
                      />
                    </div>
                    <div>
                      <Label className="text-xs mb-1 block">Kapasitas (pax)</Label>
                      <Input
                        type="number"
                        value={subEventForm.capacity}
                        onChange={e => setSubEventForm(f => ({ ...f, capacity: e.target.value }))}
                        placeholder="280"
                        className="h-8 text-sm"
                      />
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button type="submit" size="sm" className="h-7 text-xs bg-slate-900 hover:bg-slate-700" disabled={createSubEvent.isPending}>
                      {createSubEvent.isPending ? "..." : "Simpan"}
                    </Button>
                    <Button type="button" variant="ghost" size="sm" className="h-7 text-xs" onClick={() => setShowSubEventForm(false)}>
                      Batal
                    </Button>
                  </div>
                </form>
              )}

              {project.sub_events?.length === 0 && !showSubEventForm && (
                <div className="text-center py-6 text-slate-400 text-sm">
                  Belum ada sub-event. Tambahkan sub-event seperti Welcome Dinner, Special Dinner, dll.
                </div>
              )}

              {project.sub_events?.map(se => (
                <SubEventCard key={se.id} subEvent={se} />
              ))}
            </CardContent>
          </Card>

          {/* Quotations */}
          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm font-semibold text-slate-600 uppercase tracking-wide">
                  Quotations ({project.quotations?.length ?? 0})
                </CardTitle>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-7 text-xs gap-1"
                  onClick={handleCreateQuotation}
                  disabled={createQuotation.isPending}
                >
                  <Plus size={12} />
                  Buat Quotation
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-2">
              {project.quotations?.length === 0 && (
                <div className="text-center py-6">
                  <FileText size={28} className="mx-auto text-slate-300 mb-2" />
                  <p className="text-sm text-slate-400 mb-3">
                    Belum ada quotation. Buat quotation pertama untuk project ini.
                  </p>
                  <Button
                    size="sm"
                    className="bg-slate-900 hover:bg-slate-700 gap-1.5"
                    onClick={handleCreateQuotation}
                    disabled={createQuotation.isPending}
                  >
                    <Zap size={13} />
                    Buat Quotation
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => navigate(`/mice/projects/${project.id}/assets`)}
                    className="gap-2"
                  >
                    <FolderOpen size={14} />
                    Asset Hub
                  </Button>

                </div>
              )}
              {project.quotations?.map(q => (
                <QuotationCard key={q.id} quotation={q} projectId={project.id} />
              ))}
            </CardContent>
          </Card>

        </div>
      </div>
    </div>
  );
}
