// src/pages/MICEProjectsPage.jsx
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";
import { useAuth } from "@/hooks/useAuth";
import { useEvents } from "@/hooks/useEvents";
import { useCreateMICEProject, useMICEProjects } from "@/hooks/useMICE";
import {
  Building2,
  Calendar,
  CheckCircle2,
  Clock,
  FileText,
  Plus,
  TrendingUp,
  X,
} from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

const IDR = (val) =>
  new Intl.NumberFormat("id-ID", {
    style: "currency",
    currency: "IDR",
    notation: "compact",
    maximumFractionDigits: 1,
  }).format(val ?? 0);

const STATUS_CONFIG = {
  draft:     { label: "Draft",      className: "bg-slate-100 text-slate-600 border-slate-200" },
  quoted:    { label: "Terkirim",   className: "bg-blue-50 text-blue-700 border-blue-200" },
  approved:  { label: "Disetujui", className: "bg-emerald-50 text-emerald-700 border-emerald-200" },
  active:    { label: "Aktif",      className: "bg-green-50 text-green-700 border-green-200" },
  completed: { label: "Selesai",    className: "bg-slate-50 text-slate-500 border-slate-200" },
  cancelled: { label: "Batal",      className: "bg-red-50 text-red-600 border-red-200" },
};

function StatCard({ title, value, sub, icon: Icon, accent }) {
  return (
    <div className={`bg-white rounded-xl border p-5 flex items-start gap-4 ${accent ? "border-l-4 border-l-slate-800" : ""}`}>
      <div className="w-10 h-10 rounded-lg bg-slate-100 flex items-center justify-center shrink-0">
        <Icon size={18} className="text-slate-600" />
      </div>
      <div>
        <p className="text-xs text-slate-400 font-medium uppercase tracking-wide">{title}</p>
        <p className="text-2xl font-bold text-slate-900 mt-0.5">{value}</p>
        {sub && <p className="text-xs text-slate-400 mt-0.5">{sub}</p>}
      </div>
    </div>
  );
}

function ProjectCard({ project }) {
  const navigate  = useNavigate();
  const statusCfg = STATUS_CONFIG[project.status] ?? STATUS_CONFIG.draft;
  const q         = project.active_quotation;

  return (
    <Card
      className="cursor-pointer hover:shadow-md hover:-translate-y-0.5 transition-all duration-200 border-slate-200 group"
      onClick={() => navigate(`/mice/projects/${project.id}`)}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-slate-900 truncate group-hover:text-slate-700">
              {project.event_title}
            </h3>
            <p className="text-sm text-slate-500 mt-0.5 truncate">
              {project.client_company}
            </p>
          </div>
          <span className={`text-xs font-medium px-2.5 py-1 rounded-full border shrink-0 ${statusCfg.className}`}>
            {statusCfg.label}
          </span>
        </div>
      </CardHeader>

      <CardContent className="space-y-3 pt-0">
        <div className="flex flex-wrap items-center gap-3 text-xs text-slate-400">
          <div className="flex items-center gap-1.5">
            <FileText size={11} />
            <span className="font-mono">{project.quotation_number}</span>
          </div>
          {project.event_start && (
            <div className="flex items-center gap-1.5">
              <Calendar size={11} />
              <span>
                {new Date(project.event_start).toLocaleDateString("id-ID", {
                  day: "numeric", month: "short", year: "numeric",
                })}
              </span>
            </div>
          )}
          <div className="flex items-center gap-1.5">
            <Building2 size={11} />
            <span>{project.sub_event_count} sub-event</span>
          </div>
        </div>

        {q && (
          <div className="flex items-center justify-between pt-2 border-t border-slate-100">
            <div>
              <p className="text-xs text-slate-400">Total Klien</p>
              <p className="text-sm font-bold font-mono text-emerald-600">
                {IDR(q.total_after_tax)}
              </p>
            </div>
            <div className="text-right">
              <p className="text-xs text-slate-400">Net Margin</p>
              <p className="text-sm font-semibold font-mono text-slate-700">
                {IDR(q.net_margin)}
              </p>
            </div>
          </div>
        )}

        {project.task_counts?.total > 0 && (
          <div className="flex items-center gap-3 text-xs">
            <div className="flex items-center gap-1 text-emerald-600">
              <CheckCircle2 size={11} />
              <span>{project.task_counts.done}/{project.task_counts.total} tasks</span>
            </div>
            {project.task_counts.overdue > 0 && (
              <div className="flex items-center gap-1 text-red-500">
                <Clock size={11} />
                <span>{project.task_counts.overdue} terlambat</span>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function CreateProjectModal({ onClose }) {
  const { toast }     = useToast();
  const navigate      = useNavigate();
  const create        = useCreateMICEProject();
  const { data: events = [] } = useEvents({ status: "published" });
  const [form, setForm] = useState({
    event: "", client_company: "", client_pic: "",
    client_email: "", client_phone: "",
  });
  const set = (k, v) => setForm(f => ({ ...f, [k]: v }));

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!form.event || !form.client_company || !form.client_pic) {
      toast({ title: "Event, klien, dan PIC wajib diisi", variant: "destructive" });
      return;
    }
    create.mutate(form, {
      onSuccess: (data) => {
        toast({ title: "Project berhasil dibuat!" });
        navigate(`/mice/projects/${data.id}`);
      },
      onError: (err) => {
        const msg = err?.response?.data?.event?.[0]
          || err?.response?.data?.detail
          || "Gagal membuat project";
        toast({ title: msg, variant: "destructive" });
      },
    });
  };

  return (
    <div
      className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <Card className="w-full max-w-lg shadow-2xl">
        <CardHeader className="pb-4">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg">Buat MICE Project Baru</CardTitle>
            <button
              onClick={onClose}
              className="p-1 rounded hover:bg-slate-100 text-slate-400"
            >
              <X size={18} />
            </button>
          </div>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label className="text-sm mb-1.5 block">Event *</Label>
              <select
                className="w-full h-10 px-3 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-slate-800"
                value={form.event}
                onChange={e => set("event", e.target.value)}
                required
              >
                <option value="">-- Pilih Event --</option>
                {events.map(ev => (
                  <option key={ev.id} value={ev.id}>{ev.title}</option>
                ))}
              </select>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="col-span-2">
                <Label className="text-sm mb-1.5 block">Nama Klien / Perusahaan *</Label>
                <Input
                  value={form.client_company}
                  onChange={e => set("client_company", e.target.value)}
                  placeholder="e.g. Mandiri Utama Finance"
                  required
                />
              </div>
              <div className="col-span-2">
                <Label className="text-sm mb-1.5 block">PIC Klien *</Label>
                <Input
                  value={form.client_pic}
                  onChange={e => set("client_pic", e.target.value)}
                  placeholder="e.g. Bapak Fajar Lazuardiana"
                  required
                />
              </div>
              <div>
                <Label className="text-sm mb-1.5 block">Email Klien</Label>
                <Input
                  type="email"
                  value={form.client_email}
                  onChange={e => set("client_email", e.target.value)}
                  placeholder="klien@perusahaan.com"
                />
              </div>
              <div>
                <Label className="text-sm mb-1.5 block">Telepon</Label>
                <Input
                  value={form.client_phone}
                  onChange={e => set("client_phone", e.target.value)}
                  placeholder="+62 811 234 5678"
                />
              </div>
            </div>

            <div className="flex gap-2 pt-2">
              <Button
                type="submit"
                className="flex-1 bg-slate-900 hover:bg-slate-700"
                disabled={create.isPending}
              >
                {create.isPending ? "Membuat..." : "Buat Project"}
              </Button>
              <Button type="button" variant="outline" onClick={onClose}>
                Batal
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}

export default function MICEProjectsPage() {
  const { data: projects = [], isLoading } = useMICEProjects();
  const [showCreate, setShowCreate] = useState(false);

  const active   = projects.filter(p => p.status === "active").length;
  const approved = projects.filter(p => p.status === "approved").length;
  const totalRev = projects.reduce((sum, p) =>
    sum + parseFloat(p.active_quotation?.total_after_tax ?? 0), 0
  );

  return (
    <div className="space-y-6 max-w-6xl">

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">MICE Projects</h1>
          <p className="text-sm text-slate-500 mt-1">
            Manajemen event korporat & produksi profesional
          </p>
        </div>
        <Button
          onClick={() => setShowCreate(true)}
          className="bg-slate-900 hover:bg-slate-700 gap-2"
        >
          <Plus size={16} />
          Project Baru
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <StatCard title="Total Project" value={projects.length} icon={Building2} accent />
        <StatCard title="Aktif" value={active} icon={TrendingUp} />
        <StatCard title="Approval" value={approved} icon={CheckCircle2} />
        <StatCard
          title="Total Revenue"
          value={new Intl.NumberFormat("id-ID", {
            style: "currency", currency: "IDR",
            notation: "compact", maximumFractionDigits: 1,
          }).format(totalRev)}
          icon={FileText}
        />
      </div>

      {/* Loading */}
      {isLoading && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3].map(i => (
            <div key={i} className="h-48 rounded-xl bg-slate-100 animate-pulse" />
          ))}
        </div>
      )}

      {/* Empty state */}
      {!isLoading && projects.length === 0 && (
        <div className="border-2 border-dashed border-slate-200 rounded-2xl py-20 text-center">
          <Building2 size={40} className="mx-auto text-slate-300 mb-4" />
          <h3 className="font-semibold text-slate-600 mb-1">Belum ada MICE project</h3>
          <p className="text-sm text-slate-400 mb-6 max-w-xs mx-auto">
            Buat project pertama untuk mulai membangun quotation profesional.
          </p>
          <Button
            onClick={() => setShowCreate(true)}
            className="bg-slate-900 hover:bg-slate-700 gap-2"
          >
            <Plus size={16} />
            Buat Project Pertama
          </Button>
        </div>
      )}

      {/* Projects grid */}
      {!isLoading && projects.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {projects.map(project => (
            <ProjectCard key={project.id} project={project} />
          ))}
        </div>
      )}

      {/* Create modal */}
      {showCreate && <CreateProjectModal onClose={() => setShowCreate(false)} />}
    </div>
  );
}
