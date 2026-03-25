// src/pages/AssetHubPage.jsx
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";
import {
  useAssetsByType,
  useDeleteAsset,
  useToggleAssetVisibility,
  useUploadAsset,
} from "@/hooks/useMICE";
import {
  ArrowLeft,
  Download,
  Eye,
  EyeOff,
  File,
  FileImage,
  FileText,
  FileVideo,
  Folder,
  Plus,
  Trash2,
  Upload,
  Users
} from "lucide-react";
import { useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

// ── Asset type config ─────────────────────────────────────────────────────────
const TYPE_CONFIG = {
  sow:        { icon: FileText,  color: "bg-blue-50 text-blue-600 border-blue-200",    label: "Scope of Work" },
  key_visual: { icon: FileImage, color: "bg-purple-50 text-purple-600 border-purple-200", label: "Key Visual 2D" },
  stage_3d:   { icon: Folder,    color: "bg-amber-50 text-amber-600 border-amber-200",  label: "Stage Design 3D" },
  multimedia: { icon: FileVideo, color: "bg-rose-50 text-rose-600 border-rose-200",    label: "Multimedia / Video" },
  contract:   { icon: File,      color: "bg-slate-50 text-slate-600 border-slate-200", label: "Vendor Contract" },
  report:     { icon: FileText,  color: "bg-emerald-50 text-emerald-600 border-emerald-200", label: "Post-Event Report" },
  other:      { icon: File,      color: "bg-gray-50 text-gray-500 border-gray-200",    label: "Other" },
};

const ACCEPT_MAP = {
  key_visual: "image/*",
  stage_3d:   "image/*,.pdf,.ai,.psd,.fig",
  multimedia: "video/*",
  contract:   ".pdf,.doc,.docx",
  sow:        ".pdf,.doc,.docx",
  report:     ".pdf,.doc,.docx,.pptx",
  other:      "*",
};

function formatBytes(bytes) {
  if (!bytes) return "—";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

// ── Upload Form ───────────────────────────────────────────────────────────────
function UploadForm({ projectId, assetType, onClose }) {
  const { toast }   = useToast();
  const upload      = useUploadAsset();
  const fileRef     = useRef();
  const [form, setForm] = useState({
    title: "", description: "", version: "", client_visible: false,
  });
  const [file, setFile]       = useState(null);
  const [dragging, setDragging] = useState(false);

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }));

  const handleFile = (f) => {
    setFile(f);
    if (!form.title) set("title", f.name.replace(/\.[^.]+$/, ""));
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    const f = e.dataTransfer.files[0];
    if (f) handleFile(f);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!file) {
      toast({ title: "Pilih file terlebih dahulu", variant: "destructive" });
      return;
    }
    const fd = new FormData();
    fd.append("file",           file);
    fd.append("title",          form.title);
    fd.append("description",    form.description);
    fd.append("version",        form.version);
    fd.append("asset_type",     assetType);
    fd.append("client_visible", form.client_visible);

    upload.mutate({ projectId, formData: fd }, {
      onSuccess: () => {
        toast({ title: "File berhasil diupload!" });
        onClose();
      },
      onError: (err) => {
        const msg = err?.response?.data?.file?.[0] || "Upload gagal";
        toast({ title: msg, variant: "destructive" });
      },
    });
  };

  const cfg = TYPE_CONFIG[assetType] ?? TYPE_CONFIG.other;

  return (
    <div
      className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <Card className="w-full max-w-md shadow-2xl">
        <CardHeader className="pb-4">
          <div className="flex items-center justify-between">
            <CardTitle className="text-base">Upload {cfg.label}</CardTitle>
            <button onClick={onClose} className="text-slate-400 hover:text-slate-600">✕</button>
          </div>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">

            {/* Drop zone */}
            <div
              className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-colors ${
                dragging
                  ? "border-slate-800 bg-slate-50"
                  : file
                  ? "border-emerald-400 bg-emerald-50"
                  : "border-slate-200 hover:border-slate-400"
              }`}
              onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
              onDragLeave={() => setDragging(false)}
              onDrop={handleDrop}
              onClick={() => fileRef.current?.click()}
            >
              <input
                ref={fileRef}
                type="file"
                className="hidden"
                accept={ACCEPT_MAP[assetType] ?? "*"}
                onChange={(e) => e.target.files[0] && handleFile(e.target.files[0])}
              />
              {file ? (
                <div>
                  <p className="text-sm font-medium text-emerald-700">{file.name}</p>
                  <p className="text-xs text-emerald-500 mt-1">{formatBytes(file.size)}</p>
                </div>
              ) : (
                <div>
                  <Upload size={24} className="mx-auto text-slate-300 mb-2" />
                  <p className="text-sm text-slate-500">
                    Drag & drop atau <span className="text-slate-800 font-medium">klik untuk pilih file</span>
                  </p>
                  <p className="text-xs text-slate-400 mt-1">
                    {ACCEPT_MAP[assetType] === "*" ? "Semua tipe file" : ACCEPT_MAP[assetType]}
                  </p>
                </div>
              )}
            </div>

            <div>
              <Label className="text-sm mb-1.5 block">Judul *</Label>
              <Input
                value={form.title}
                onChange={(e) => set("title", e.target.value)}
                placeholder="e.g. Key Visual MUFEST 2025 Final"
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label className="text-sm mb-1.5 block">Versi</Label>
                <Input
                  value={form.version}
                  onChange={(e) => set("version", e.target.value)}
                  placeholder="v1, v2-final"
                />
              </div>
              <div className="flex items-end pb-0.5">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={form.client_visible}
                    onChange={(e) => set("client_visible", e.target.checked)}
                    className="w-4 h-4 rounded"
                  />
                  <div>
                    <p className="text-sm font-medium text-slate-700">Visible ke klien</p>
                    <p className="text-xs text-slate-400">Tampil di portal klien</p>
                  </div>
                </label>
              </div>
            </div>

            <div>
              <Label className="text-sm mb-1.5 block">Deskripsi</Label>
              <Input
                value={form.description}
                onChange={(e) => set("description", e.target.value)}
                placeholder="Catatan tambahan (opsional)"
              />
            </div>

            <div className="flex gap-2 pt-1">
              <Button
                type="submit"
                className="flex-1 bg-slate-900 hover:bg-slate-700 gap-2"
                disabled={upload.isPending}
              >
                <Upload size={14} />
                {upload.isPending ? "Mengupload..." : "Upload"}
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

// ── Asset Card ────────────────────────────────────────────────────────────────
function AssetCard({ asset, projectId }) {
  const { toast }   = useToast();
  const toggle      = useToggleAssetVisibility();
  const deleteAsset = useDeleteAsset();

  const handleToggle = () => {
    toggle.mutate({ projectId, assetId: asset.id }, {
      onSuccess: (data) => toast({
        title: data.client_visible
          ? "Asset sekarang visible ke klien"
          : "Asset disembunyikan dari klien",
      }),
    });
  };

  const handleDelete = () => {
    if (!confirm(`Hapus "${asset.title}"?`)) return;
    deleteAsset.mutate({ projectId, assetId: asset.id }, {
      onSuccess: () => toast({ title: "Asset dihapus" }),
      onError: () => toast({ title: "Gagal menghapus", variant: "destructive" }),
    });
  };

  return (
    <div className="flex items-center gap-3 p-3 bg-white rounded-lg border border-slate-100 hover:border-slate-200 hover:shadow-sm transition-all group">

      {/* File icon or image preview */}
      <div className="w-10 h-10 rounded-lg bg-slate-100 flex items-center justify-center shrink-0 overflow-hidden">
        {asset.is_image && asset.file_url ? (
          <img src={asset.file_url} alt={asset.title} className="w-full h-full object-cover" />
        ) : (
          <File size={18} className="text-slate-400" />
        )}
      </div>

      {/* Info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <p className="text-sm font-medium text-slate-800 truncate">{asset.title}</p>
          {asset.version && (
            <span className="text-xs bg-slate-100 text-slate-500 px-1.5 py-0.5 rounded shrink-0">
              {asset.version}
            </span>
          )}
        </div>
        <div className="flex items-center gap-3 mt-0.5">
          <p className="text-xs text-slate-400">{formatBytes(asset.file_size)}</p>
          {asset.uploaded_by_name && (
            <p className="text-xs text-slate-400 flex items-center gap-1">
              <Users size={10} />
              {asset.uploaded_by_name}
            </p>
          )}
          <p className="text-xs text-slate-300">
            {new Date(asset.created_at).toLocaleDateString("id-ID", {
              day: "numeric", month: "short",
            })}
          </p>
        </div>
      </div>

      {/* Client visible badge */}
      {asset.client_visible && (
        <span className="text-xs bg-emerald-50 text-emerald-600 border border-emerald-200 px-2 py-0.5 rounded-full shrink-0 flex items-center gap-1">
          <Eye size={10} />
          Klien
        </span>
      )}

      {/* Actions */}
      <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
        <a
          href={asset.file_url}
          target="_blank"
          rel="noopener noreferrer"
          className="p-1.5 rounded hover:bg-slate-100 text-slate-400 hover:text-slate-600"
          title="Download / Preview"
        >
          <Download size={14} />
        </a>
        <button
          className={`p-1.5 rounded hover:bg-slate-100 transition-colors ${
            asset.client_visible
              ? "text-emerald-500 hover:text-emerald-700"
              : "text-slate-300 hover:text-slate-600"
          }`}
          onClick={handleToggle}
          disabled={toggle.isPending}
          title={asset.client_visible ? "Sembunyikan dari klien" : "Tampilkan ke klien"}
        >
          {asset.client_visible ? <Eye size={14} /> : <EyeOff size={14} />}
        </button>
        <button
          className="p-1.5 rounded hover:bg-red-50 text-slate-300 hover:text-red-500 transition-colors"
          onClick={handleDelete}
          title="Hapus"
        >
          <Trash2 size={14} />
        </button>
      </div>
    </div>
  );
}

// ── Section Block ─────────────────────────────────────────────────────────────
function AssetSection({ group, projectId }) {
  const cfg = TYPE_CONFIG[group.type] ?? TYPE_CONFIG.other;
  const Icon = cfg.icon;
  const [uploading, setUploading] = useState(false);

  // Vendor contracts — always internal, no client visibility toggle shown
  const isInternal = group.type === "contract";

  return (
    <Card className="border-slate-200">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={`w-8 h-8 rounded-lg border flex items-center justify-center ${cfg.color}`}>
              <Icon size={15} />
            </div>
            <div>
              <CardTitle className="text-sm font-semibold text-slate-700">
                {group.label}
              </CardTitle>
              <p className="text-xs text-slate-400 mt-0.5">
                {group.count} file{group.count !== 1 ? "s" : ""}
                {isInternal && (
                  <span className="ml-2 text-slate-300">· internal only</span>
                )}
              </p>
            </div>
          </div>
          <Button
            variant="ghost"
            size="sm"
            className="h-7 text-xs gap-1 text-slate-500 hover:text-slate-800"
            onClick={() => setUploading(true)}
          >
            <Plus size={12} />
            Upload
          </Button>
        </div>
      </CardHeader>

      <CardContent className="pt-0 space-y-2">
        {group.assets.length === 0 ? (
          <div
            className="border-2 border-dashed border-slate-100 rounded-lg py-6 text-center cursor-pointer hover:border-slate-300 transition-colors"
            onClick={() => setUploading(true)}
          >
            <Upload size={20} className="mx-auto text-slate-300 mb-1.5" />
            <p className="text-xs text-slate-400">Upload file {group.label}</p>
          </div>
        ) : (
          group.assets.map(asset => (
            <AssetCard
              key={asset.id}
              asset={asset}
              projectId={projectId}
            />
          ))
        )}
      </CardContent>

      {uploading && (
        <UploadForm
          projectId={projectId}
          assetType={group.type}
          onClose={() => setUploading(false)}
        />
      )}
    </Card>
  );
}

// ── Empty state ───────────────────────────────────────────────────────────────
function EmptyState({ projectId }) {
  const [uploading, setUploading] = useState(false);

  return (
    <div className="border-2 border-dashed border-slate-200 rounded-2xl py-20 text-center">
      <Folder size={40} className="mx-auto text-slate-300 mb-4" />
      <h3 className="font-semibold text-slate-600 mb-1">Belum ada asset</h3>
      <p className="text-sm text-slate-400 mb-6 max-w-sm mx-auto">
        Upload Key Visual, SOW, Stage Design, dan file lainnya untuk project ini.
      </p>
      <Button
        onClick={() => setUploading(true)}
        className="bg-slate-900 hover:bg-slate-700 gap-2"
      >
        <Upload size={14} />
        Upload File Pertama
      </Button>
      {uploading && (
        <UploadForm
          projectId={projectId}
          assetType="other"
          onClose={() => setUploading(false)}
        />
      )}
    </div>
  );
}

// ── Main Page ─────────────────────────────────────────────────────────────────
export default function AssetHubPage() {
  const { projectId }   = useParams();
  const navigate        = useNavigate();
  const { data: groups = [], isLoading } = useAssetsByType(projectId);

  const totalFiles    = groups.reduce((sum, g) => sum + g.count, 0);
  const clientVisible = groups.reduce(
    (sum, g) => sum + g.assets.filter(a => a.client_visible).length, 0
  );

  return (
    <div className="space-y-6 max-w-5xl">

      {/* Header */}
      <div>
        <button
          onClick={() => navigate(`/mice/projects/${projectId}`)}
          className="flex items-center gap-1.5 text-sm text-slate-400 hover:text-slate-600 mb-4 transition-colors"
        >
          <ArrowLeft size={14} />
          Kembali ke Project
        </button>

        <div className="flex items-start justify-between gap-4 flex-wrap">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Asset Hub</h1>
            <p className="text-sm text-slate-500 mt-1">
              File organisasi A–Z · {totalFiles} file total ·{" "}
              <span className="text-emerald-600 font-medium">
                {clientVisible} visible ke klien
              </span>
            </p>
          </div>

          {/* Legend */}
          <div className="flex items-center gap-4 text-xs text-slate-400">
            <div className="flex items-center gap-1.5">
              <Eye size={12} className="text-emerald-500" />
              <span>Visible ke klien</span>
            </div>
            <div className="flex items-center gap-1.5">
              <EyeOff size={12} className="text-slate-300" />
              <span>Internal only</span>
            </div>
          </div>
        </div>
      </div>

      {/* Loading */}
      {isLoading && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {[1, 2, 3, 4].map(i => (
            <div key={i} className="h-32 rounded-xl bg-slate-100 animate-pulse" />
          ))}
        </div>
      )}

      {/* Empty state — no groups returned yet */}
      {!isLoading && groups.length === 0 && (
        <EmptyState projectId={projectId} />
      )}

      {/* Asset sections grid */}
      {!isLoading && groups.length > 0 && (
        <>
          {/* Quick stats */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {groups.map(group => {
              const cfg  = TYPE_CONFIG[group.type] ?? TYPE_CONFIG.other;
              const Icon = cfg.icon;
              return (
                <div
                  key={group.type}
                  className={`flex items-center gap-3 p-3 rounded-xl border ${cfg.color} cursor-pointer hover:shadow-sm transition-shadow`}
                >
                  <Icon size={16} />
                  <div>
                    <p className="text-xs font-semibold truncate">{group.label}</p>
                    <p className="text-lg font-bold leading-none mt-0.5">{group.count}</p>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Sections */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {groups.map(group => (
              <AssetSection
                key={group.type}
                group={group}
                projectId={projectId}
              />
            ))}
          </div>
        </>
      )}

      {/* If no files uploaded yet but sections exist — show all empty sections */}
      {!isLoading && groups.length === 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {Object.entries(TYPE_CONFIG).map(([type, cfg]) => {
            const Icon = cfg.icon;
            return (
              <AssetSection
                key={type}
                group={{ type, label: cfg.label, assets: [], count: 0 }}
                projectId={projectId}
              />
            );
          })}
        </div>
      )}
    </div>
  );
}
