// src/pages/QuotationBuilderPage.jsx
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { useToast } from "@/hooks/use-toast";
import {
  useBulkCreateStandardSections,
  useCreateLineItem,
  useCreateQuotationRevision,
  useCreateSection,
  useDeleteLineItem,
  useDeleteSection,
  useQuotation,
  useRecalculateQuotation,
  useSendQuotationToClient,
  useUpdateLineItem,
} from "@/hooks/useMICE";
import {
  ArrowLeft,
  ChevronDown,
  ChevronUp,
  Copy,
  FilePlus,
  GitBranch,
  Layers,
  Plus,
  RefreshCw,
  Send,
  Trash2,
} from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

const IDR = (val) =>
  new Intl.NumberFormat("id-ID", {
    style: "currency", currency: "IDR", maximumFractionDigits: 0,
  }).format(val ?? 0);

const PCT = (val) => `${(parseFloat(val ?? 0) * 100).toFixed(1)}%`;

// ── Line Item Row ─────────────────────────────────────────────────────────────
function LineItemRow({ item, quotationId, sectionId }) {
  const { toast }   = useToast();
  const update      = useUpdateLineItem();
  const deleteItem  = useDeleteLineItem();
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState({
    item_name:   item.item_name ?? "",
    detail:      item.detail ?? "",
    qty:         item.qty ?? "1",
    vol_unit:    item.vol_unit ?? "pax",
    duration:    item.duration ?? "1",
    dur_unit:    item.dur_unit ?? "day",
    modal_price: item.modal_price ?? "0",
    margin_pct:  item.margin_pct ? (parseFloat(item.margin_pct) * 100).toFixed(0) : "15",
  });

  useEffect(() => {
    setForm({
      item_name: item.item_name ?? "",
      detail: item.detail ?? "",
      qty: item.qty ?? "1",
      vol_unit: item.vol_unit ?? "pax",
      duration: item.duration ?? "1",
      dur_unit: item.dur_unit ?? "day",
      modal_price: item.modal_price ?? "0",
      margin_pct: item.margin_pct ? (parseFloat(item.margin_pct) * 100).toFixed(0) : "15",
    });
  }, [item]);

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }));

  const handleSave = () => {
    update.mutate({
      quotationId, sectionId, itemId: item.id,
      data: { ...form, margin_pct: (parseFloat(form.margin_pct) / 100).toFixed(4) },
    }, {
      onSuccess: () => { setEditing(false); toast({ title: "Item diperbarui" }); },
      onError: () => toast({ title: "Gagal menyimpan", variant: "destructive" }),
    });
  };

  if (!editing) {
    return (
      <tr
        className="border-b border-slate-100 hover:bg-blue-50/30 cursor-pointer group transition-colors"
        onClick={() => setEditing(true)}
      >
        <td className="px-3 py-2.5 text-xs text-slate-400 w-8">{(item.sort_order ?? 0) + 1}</td>
        <td className="px-3 py-2.5">
          <p className="text-sm font-medium text-slate-800">{item.item_name}</p>
          {item.detail && <p className="text-xs text-slate-400 mt-0.5">{item.detail}</p>}
        </td>
        <td className="px-3 py-2.5 text-xs text-slate-500 whitespace-nowrap">{item.qty} {item.vol_unit}</td>
        <td className="px-3 py-2.5 text-xs text-slate-500 whitespace-nowrap">{item.duration} {item.dur_unit}</td>
        <td className="px-3 py-2.5 text-xs text-slate-400 text-right font-mono whitespace-nowrap">
          {IDR(item.modal_price)}
        </td>
        <td className="px-3 py-2.5 text-xs text-slate-500 text-right font-mono whitespace-nowrap">
          {IDR(item.total_modal)}
        </td>
        <td className="px-3 py-2.5 text-xs text-slate-500 text-right whitespace-nowrap">
          {(parseFloat(item.margin_pct ?? 0) * 100).toFixed(0)}%
        </td>
        <td className="px-3 py-2.5 text-xs text-slate-400 text-right font-mono whitespace-nowrap">
          {IDR(item.pph_amt)}
        </td>
        <td className="px-3 py-2.5 text-xs text-slate-600 text-right font-mono whitespace-nowrap">
          {IDR(item.client_price)}
        </td>
        <td className="px-3 py-2.5 text-sm font-semibold text-emerald-600 text-right font-mono whitespace-nowrap">
          {IDR(item.total_client)}
        </td>
        <td className="px-3 py-2.5 w-8">
          <button
            className="opacity-0 group-hover:opacity-100 transition-opacity text-slate-300 hover:text-red-500"
            onClick={(e) => {
              e.stopPropagation();
              if (!confirm(`Hapus "${item.item_name}"?`)) return;
              deleteItem.mutate({ quotationId, sectionId, itemId: item.id }, {
                onSuccess: () => toast({ title: "Item dihapus" }),
              });
            }}
          >
            <Trash2 size={13} />
          </button>
        </td>
      </tr>
    );
  }

  return (
    <tr className="border-b-2 border-blue-300 bg-blue-50/50">
      <td className="px-3 py-2 text-xs text-slate-400 w-8">{(item.sort_order ?? 0) + 1}</td>
      <td className="px-3 py-2 min-w-52">
        <Input value={form.item_name} onChange={e => set("item_name", e.target.value)} placeholder="Nama item" className="h-7 text-sm mb-1" />
        <Input value={form.detail} onChange={e => set("detail", e.target.value)} placeholder="Detail" className="h-6 text-xs" />
      </td>
      <td className="px-3 py-2">
        <div className="flex gap-1">
          <Input type="number" value={form.qty} onChange={e => set("qty", e.target.value)} className="h-7 w-14 text-sm" />
          <Input value={form.vol_unit} onChange={e => set("vol_unit", e.target.value)} className="h-7 w-16 text-xs" placeholder="pax" />
        </div>
      </td>
      <td className="px-3 py-2">
        <div className="flex gap-1">
          <Input type="number" value={form.duration} onChange={e => set("duration", e.target.value)} className="h-7 w-14 text-sm" />
          <Input value={form.dur_unit} onChange={e => set("dur_unit", e.target.value)} className="h-7 w-16 text-xs" placeholder="day" />
        </div>
      </td>
      <td className="px-3 py-2">
        <Input type="number" value={form.modal_price} onChange={e => set("modal_price", e.target.value)} className="h-7 w-36 text-sm text-right font-mono" min="0" />
      </td>
      <td className="px-3 py-2 text-xs text-slate-400 text-right font-mono">{IDR(item.total_modal)}</td>
      <td className="px-3 py-2">
        <div className="flex items-center gap-1">
          <Input type="number" value={form.margin_pct} onChange={e => set("margin_pct", e.target.value)} className="h-7 w-14 text-sm text-right" min="0" max="1000" />
          <span className="text-xs text-slate-400">%</span>
        </div>
      </td>
      <td className="px-3 py-2 text-xs text-slate-400 text-right font-mono">{IDR(item.pph_amt)}</td>
      <td className="px-3 py-2 text-xs text-slate-600 text-right font-mono">{IDR(item.client_price)}</td>
      <td className="px-3 py-2 text-sm font-semibold text-emerald-600 text-right font-mono">{IDR(item.total_client)}</td>
      <td className="px-3 py-2">
        <div className="flex gap-1">
          <Button size="sm" className="h-7 text-xs px-2 bg-slate-900 hover:bg-slate-700" onClick={handleSave} disabled={update.isPending}>
            {update.isPending ? "..." : "Simpan"}
          </Button>
          <Button size="sm" variant="ghost" className="h-7 text-xs px-2" onClick={() => setEditing(false)}>
            ✕
          </Button>
        </div>
      </td>
    </tr>
  );
}

// ── Add Line Item Form ────────────────────────────────────────────────────────
function AddLineItemForm({ quotationId, sectionId, onDone }) {
  const { toast } = useToast();
  const create    = useCreateLineItem();
  const [form, setForm] = useState({
    item_name: "", detail: "", qty: "1", vol_unit: "pax",
    duration: "1", dur_unit: "day", modal_price: "", margin_pct: "0.15",
  });
  const set = (k, v) => setForm(f => ({ ...f, [k]: v }));

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!form.item_name || !form.modal_price) {
      toast({ title: "Nama item dan modal price wajib diisi", variant: "destructive" });
      return;
    }
    create.mutate({ quotationId, sectionId, data: form }, {
      onSuccess: () => {
        setForm({ item_name: "", detail: "", qty: "1", vol_unit: "pax", duration: "1", dur_unit: "day", modal_price: "", margin_pct: "0.15" });
        onDone?.();
        toast({ title: "Item ditambahkan" });
      },
      onError: () => toast({ title: "Gagal menambah item", variant: "destructive" }),
    });
  };

  return (
    <tr className="bg-slate-50 border-b">
      <td colSpan={12} className="px-4 py-3">
        <form onSubmit={handleSubmit} className="flex flex-wrap gap-2 items-end">
          <div className="flex-1 min-w-36">
            <Label className="text-xs mb-1 block">Nama Item *</Label>
            <Input value={form.item_name} onChange={e => set("item_name", e.target.value)} placeholder="e.g. Content Managing" className="h-8 text-sm" required />
          </div>
          <div className="w-36">
            <Label className="text-xs mb-1 block">Detail</Label>
            <Input value={form.detail} onChange={e => set("detail", e.target.value)} placeholder="e.g. Idea & Creative" className="h-8 text-sm" />
          </div>
          <div className="w-14">
            <Label className="text-xs mb-1 block">QTY</Label>
            <Input type="number" value={form.qty} onChange={e => set("qty", e.target.value)} className="h-8 text-sm" min="0.01" />
          </div>
          <div className="w-16">
            <Label className="text-xs mb-1 block">Vol</Label>
            <Input value={form.vol_unit} onChange={e => set("vol_unit", e.target.value)} className="h-8 text-sm" placeholder="pax" />
          </div>
          <div className="w-14">
            <Label className="text-xs mb-1 block">Dur</Label>
            <Input type="number" value={form.duration} onChange={e => set("duration", e.target.value)} className="h-8 text-sm" min="0.01" />
          </div>
          <div className="w-16">
            <Label className="text-xs mb-1 block">Unit</Label>
            <Input value={form.dur_unit} onChange={e => set("dur_unit", e.target.value)} className="h-8 text-sm" placeholder="day" />
          </div>
          <div className="w-36">
            <Label className="text-xs mb-1 block">Modal Price (Rp) *</Label>
            <Input type="number" value={form.modal_price} onChange={e => set("modal_price", e.target.value)} className="h-8 text-sm font-mono text-right" placeholder="15000000" required />
          </div>
          <div className="w-20">
            <Label className="text-xs mb-1 block">Margin %</Label>
            <div className="flex items-center gap-1">
              <Input
                type="number"
                value={(parseFloat(form.margin_pct) * 100).toFixed(0)}
                onChange={e => set("margin_pct", (parseFloat(e.target.value) / 100).toFixed(4))}
                className="h-8 text-sm"
                min="0" max="1000"
              />
              <span className="text-xs text-slate-400">%</span>
            </div>
          </div>
          <Button type="submit" size="sm" className="h-8 bg-slate-900 hover:bg-slate-700" disabled={create.isPending}>
            {create.isPending ? "..." : "Tambah"}
          </Button>
          <Button type="button" variant="ghost" size="sm" className="h-8" onClick={() => onDone?.()}>
            Batal
          </Button>
        </form>
      </td>
    </tr>
  );
}

// ── Section Block ─────────────────────────────────────────────────────────────
function SectionBlock({ section, quotationId, readOnly }) {
  const { toast }     = useToast();
  const deleteSection = useDeleteSection();
  const [collapsed, setCollapsed]   = useState(false);
  const [addingItem, setAddingItem] = useState(false);

  return (
    <Card className="overflow-hidden border-slate-200">
      <div
        className="flex items-center justify-between px-4 py-3 bg-slate-50 border-b border-slate-200 cursor-pointer hover:bg-slate-100 transition-colors"
        onClick={() => setCollapsed(c => !c)}
      >
        <div className="flex items-center gap-3">
          <span className="text-xs font-bold uppercase tracking-widest text-slate-500">
            {section.name}
          </span>
          <span className="text-xs bg-white border border-slate-200 text-slate-500 px-2 py-0.5 rounded-full">
            {section.line_items?.length ?? 0} item
          </span>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-sm font-bold font-mono text-emerald-600 hidden sm:block">
            {IDR(section.subtotal_client)}
          </span>
          {!readOnly && (
            <button
              className="text-slate-300 hover:text-red-500 transition-colors"
              onClick={(e) => {
                e.stopPropagation();
                if (!confirm(`Hapus section "${section.name}"?`)) return;
                deleteSection.mutate({ quotationId, sectionId: section.id }, {
                  onSuccess: () => toast({ title: "Section dihapus" }),
                });
              }}
            >
              <Trash2 size={14} />
            </button>
          )}
          {collapsed ? <ChevronDown size={15} className="text-slate-400" /> : <ChevronUp size={15} className="text-slate-400" />}
        </div>
      </div>

      {!collapsed && (
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="bg-white border-b border-slate-100">
                  <th className="px-3 py-2 text-xs font-medium text-slate-400 w-8">#</th>
                  <th className="px-3 py-2 text-xs font-medium text-slate-400 min-w-48">Item / Detail</th>
                  <th className="px-3 py-2 text-xs font-medium text-slate-400">QTY</th>
                  <th className="px-3 py-2 text-xs font-medium text-slate-400">Dur</th>
                  <th className="px-3 py-2 text-xs font-medium text-slate-400 text-right">Modal</th>
                  <th className="px-3 py-2 text-xs font-medium text-slate-400 text-right">Total Modal</th>
                  <th className="px-3 py-2 text-xs font-medium text-slate-400 text-right">Margin</th>
                  <th className="px-3 py-2 text-xs font-medium text-slate-400 text-right">Pph</th>
                  <th className="px-3 py-2 text-xs font-medium text-slate-500 text-right">Harga Klien</th>
                  <th className="px-3 py-2 text-xs font-bold text-emerald-600 text-right">Total Klien</th>
                  {!readOnly && <th className="px-3 py-2 w-8" />}
                </tr>
              </thead>
              <tbody>
                {(section.line_items ?? []).map(item => (
                  <LineItemRow
                    key={item.id}
                    item={item}
                    quotationId={quotationId}
                    sectionId={section.id}
                    readOnly={readOnly}
                  />
                ))}
                {addingItem && !readOnly && (
                  <AddLineItemForm
                    quotationId={quotationId}
                    sectionId={section.id}
                    onDone={() => setAddingItem(false)}
                  />
                )}
              </tbody>
              {!readOnly && (
                <tfoot>
                  <tr>
                    <td colSpan={12} className="px-4 py-2 bg-white border-t border-slate-50">
                      <button
                        className="text-xs text-blue-600 hover:text-blue-700 flex items-center gap-1 font-medium"
                        onClick={() => setAddingItem(a => !a)}
                      >
                        <Plus size={12} />
                        {addingItem ? "Tutup" : "Tambah Item"}
                      </button>
                    </td>
                  </tr>
                </tfoot>
              )}
            </table>
          </div>
        </CardContent>
      )}
    </Card>
  );
}

// ── Financial Summary Sidebar ─────────────────────────────────────────────────
function FinancialSummary({ quotation }) {
  const { toast }    = useToast();
  const recalc       = useRecalculateQuotation();
  const sendToClient = useSendQuotationToClient();
  const q = quotation;

  const handleCopyLink = () => {
    navigator.clipboard.writeText(q.client_portal_url);
    toast({ title: "Link portal disalin!", description: q.client_portal_url });
  };

  const handleSend = () => {
    sendToClient.mutate(q.id, {
      onSuccess: (data) => toast({
        title: "Quotation terkirim ke klien!",
        description: `Portal: ${data.client_portal_url}`,
      }),
      onError: () => toast({ title: "Gagal mengirim", variant: "destructive" }),
    });
  };

  return (
    <div className="space-y-3">
      {/* Actions */}
      <Card className="border-slate-200">
        <CardContent className="p-4 space-y-2">
          <div className="flex items-center justify-between mb-3">
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Status</p>
            <span className={`text-xs font-medium px-2.5 py-1 rounded-full ${
              q.status === "approved" ? "bg-emerald-50 text-emerald-700" :
              q.status === "sent" ? "bg-blue-50 text-blue-700" :
              "bg-slate-100 text-slate-500"
            }`}>
              {q.status === "draft" ? "Draft" :
               q.status === "sent" ? "Terkirim" :
               q.status === "approved" ? "Disetujui" : q.status}
            </span>
          </div>
          <Button
            variant="outline" size="sm" className="w-full text-xs gap-2 h-8"
            onClick={() => recalc.mutate(q.id, { onSuccess: () => toast({ title: "Kalkulasi diperbarui" }) })}
            disabled={recalc.isPending}
          >
            <RefreshCw size={12} className={recalc.isPending ? "animate-spin" : ""} />
            Hitung Ulang
          </Button>
          {(q.status === "draft" || q.status === "sent") && (
            <Button
              size="sm"
              className="w-full text-xs gap-2 h-8 bg-slate-900 hover:bg-slate-700"
              onClick={handleSend}
              disabled={sendToClient.isPending}
            >
              <Send size={12} />
              {q.status === "sent" ? "Kirim Ulang" : "Kirim ke Klien"}
            </Button>
          )}
          {(q.status === "sent" || q.status === "approved") && (
            <Button variant="outline" size="sm" className="w-full text-xs gap-2 h-8" onClick={handleCopyLink}>
              <Copy size={12} />
              Salin Link Portal
            </Button>
          )}
        </CardContent>
      </Card>

      {/* Client-facing totals */}
      <Card className="border-slate-200">
        <CardHeader className="pb-2 pt-4 px-4">
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide">Yang Dibayar Klien</p>
        </CardHeader>
        <CardContent className="px-4 pb-4 space-y-1.5">
          <div className="flex justify-between text-sm">
            <span className="text-slate-500">Subtotal</span>
            <span className="font-mono text-slate-700">{IDR(q.subtotal_client)}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-slate-500">Fee ({PCT(q.fee_management_pct)})</span>
            <span className="font-mono text-slate-700">{IDR(q.fee_management_amt)}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-slate-500">PPN ({PCT(q.ppn_pct)})</span>
            <span className="font-mono text-slate-700">{IDR(q.ppn_amt)}</span>
          </div>
          <Separator className="my-2" />
          <div className="flex justify-between font-bold">
            <span className="text-slate-800">TOTAL</span>
            <span className="font-mono text-emerald-600 text-base">{IDR(q.total_after_tax)}</span>
          </div>
        </CardContent>
      </Card>

      {/* Internal margin — organizer only */}
      <Card className="border-slate-200 border-l-4 border-l-slate-800">
        <CardHeader className="pb-2 pt-4 px-4">
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide">Internal (tidak ke klien)</p>
        </CardHeader>
        <CardContent className="px-4 pb-4 space-y-1.5">
          <div className="flex justify-between text-sm">
            <span className="text-slate-400">Subtotal Modal</span>
            <span className="font-mono text-slate-500">{IDR(q.subtotal_modal)}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-slate-500">Margin Produksi</span>
            <span className="font-mono text-slate-700">{IDR(q.margin_produksi)}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-slate-500">Margin Fee</span>
            <span className="font-mono text-slate-700">{IDR(q.margin_fee_amt)}</span>
          </div>
          <Separator className="my-2" />
          <div className="flex justify-between font-semibold text-sm">
            <span className="text-slate-700">Total Margin</span>
            <span className="font-mono text-slate-800">{IDR(q.total_margin)}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-slate-400">Sodaqoh ({PCT(q.sodaqoh_pct)})</span>
            <span className="font-mono text-slate-400">− {IDR(q.sodaqoh_amt)}</span>
          </div>
          <Separator className="my-2" />
          <div className="flex justify-between font-bold">
            <span className="text-slate-800">Net Margin</span>
            <span className="font-mono text-slate-900">{IDR(q.net_margin)}</span>
          </div>
          <div className="flex justify-between text-xs text-slate-400">
            <span>Margin %</span>
            <span className="font-mono">{PCT(q.margin_pct_of_total)}</span>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

// ── Main Page ─────────────────────────────────────────────────────────────────
export default function QuotationBuilderPage() {
  const { quotationId }   = useParams();
  const navigate          = useNavigate();
  const { toast }         = useToast();
  const { data: quotation, isLoading } = useQuotation(quotationId);
  const createSection     = useCreateSection();
  const bulkSections      = useBulkCreateStandardSections();
  const createRevision    = useCreateQuotationRevision();

  const [newSectionName, setNewSectionName]   = useState("");
  const [showAddSection, setShowAddSection]   = useState(false);

  if (isLoading) return (
    <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-800" />
    </div>
  );

  if (!quotation) return (
    <div className="text-center py-20 text-slate-400">Quotation tidak ditemukan.</div>
  );

  const q        = quotation;
  const readOnly = q.status === "approved" || q.status === "superseded";

  const handleAddSection = () => {
    if (!newSectionName.trim()) return;
    createSection.mutate({
      quotationId: q.id,
      data: { quotation: q.id, name: newSectionName.trim(), sort_order: q.sections?.length ?? 0 },
    }, {
      onSuccess: () => { setNewSectionName(""); setShowAddSection(false); toast({ title: "Section ditambahkan" }); },
      onError: () => toast({ title: "Gagal menambah section", variant: "destructive" }),
    });
  };

  const handleNewRevision = () => {
    if (!confirm("Buat revisi baru? Quotation ini akan jadi superseded.")) return;
    createRevision.mutate(q.id, {
      onSuccess: (newQ) => {
        toast({ title: `Revisi ${newQ.revision} berhasil dibuat` });
        navigate(`/mice/quotation/${newQ.id}`);
      },
      onError: () => toast({ title: "Gagal membuat revisi", variant: "destructive" }),
    });
  };

  return (
    <div className="space-y-6 max-w-7xl">

      {/* Header */}
      <div>
        <button
          onClick={() => navigate(-1)}
          className="flex items-center gap-1.5 text-sm text-slate-400 hover:text-slate-600 mb-4 transition-colors"
        >
          <ArrowLeft size={14} />
          Kembali
        </button>

        <div className="flex items-start justify-between gap-4 flex-wrap">
          <div>
            <div className="flex items-center gap-3 mb-1">
              <h1 className="text-2xl font-bold text-slate-900">Quotation Builder</h1>
              <span className="text-xs font-bold bg-slate-900 text-white px-2.5 py-1 rounded-full">
                Rev. {q.revision}
              </span>
              {readOnly && (
                <span className="text-xs bg-amber-50 text-amber-700 border border-amber-200 px-2.5 py-1 rounded-full">
                  Read Only
                </span>
              )}
            </div>
            <p className="text-sm text-slate-500">
              {q.mice_project_name} ·{" "}
              <span className="font-medium text-slate-700">{q.client_company}</span>
            </p>
          </div>

          {!readOnly && (
            <Button
              variant="outline" size="sm"
              onClick={handleNewRevision}
              disabled={createRevision.isPending}
              className="gap-2"
            >
              <GitBranch size={14} />
              Buat Revisi Baru
            </Button>
          )}
        </div>
      </div>

      {/* Main layout */}
      <div className="flex flex-col lg:flex-row gap-6">

        {/* Sections */}
        <div className="flex-1 min-w-0 space-y-3">

          {/* Toolbar */}
          {!readOnly && (
            <div className="flex items-center gap-2 flex-wrap">
              <Button
                variant="outline" size="sm"
                className="gap-2 h-8 text-xs"
                onClick={() => setShowAddSection(s => !s)}
              >
                <FilePlus size={13} />
                Tambah Section
              </Button>
              {(q.sections?.length ?? 0) === 0 && (
                <Button
                  size="sm"
                  className="gap-2 h-8 text-xs bg-slate-900 hover:bg-slate-700"
                  onClick={() => bulkSections.mutate(q.id, {
                    onSuccess: () => toast({ title: "7 section standar berhasil dibuat!" }),
                    onError: () => toast({ title: "Gagal", variant: "destructive" }),
                  })}
                  disabled={bulkSections.isPending}
                >
                  <Layers size={13} />
                  {bulkSections.isPending ? "Membuat..." : "Buat 7 Section Standar"}
                </Button>
              )}
            </div>
          )}

          {/* Add section form */}
          {showAddSection && (
            <Card className="border-blue-200">
              <CardContent className="p-3">
                <div className="flex gap-2">
                  <Input
                    value={newSectionName}
                    onChange={e => setNewSectionName(e.target.value)}
                    placeholder="Nama section, e.g. Venue & Arrangement"
                    className="flex-1"
                    onKeyDown={e => e.key === "Enter" && handleAddSection()}
                    autoFocus
                  />
                  <Button size="sm" onClick={handleAddSection} disabled={createSection.isPending} className="bg-slate-900 hover:bg-slate-700">
                    {createSection.isPending ? "..." : "Tambah"}
                  </Button>
                  <Button size="sm" variant="ghost" onClick={() => setShowAddSection(false)}>Batal</Button>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Empty state */}
          {(q.sections?.length ?? 0) === 0 && !showAddSection && (
            <div className="border-2 border-dashed border-slate-200 rounded-xl py-16 text-center">
              <Layers size={32} className="mx-auto text-slate-300 mb-3" />
              <p className="text-slate-500 font-medium mb-1">Belum ada section</p>
              <p className="text-sm text-slate-400 mb-4">
                Buat 7 section standar sesuai format MUFEST, atau tambah manual.
              </p>
              {!readOnly && (
                <Button
                  onClick={() => bulkSections.mutate(q.id, {
                    onSuccess: () => toast({ title: "7 section standar berhasil dibuat!" }),
                  })}
                  disabled={bulkSections.isPending}
                  className="bg-slate-900 hover:bg-slate-700 gap-2"
                >
                  <Layers size={14} />
                  Buat Section Standar
                </Button>
              )}
            </div>
          )}

          {/* Section blocks */}
          {(q.sections ?? []).map(section => (
            <SectionBlock
              key={section.id}
              section={section}
              quotationId={q.id}
              readOnly={readOnly}
            />
          ))}
        </div>

        {/* Financial summary sidebar */}
        <div className="w-full lg:w-72 shrink-0">
          <div className="lg:sticky lg:top-6">
            <FinancialSummary quotation={q} />
          </div>
        </div>

      </div>
    </div>
  );
}
