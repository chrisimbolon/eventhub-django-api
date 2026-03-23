// src/pages/ClientPortalPage.jsx
// PUBLIC — no auth required. Client views and approves quotation.
import { approveQuotationAsClient, fetchClientPortal } from "@/api/mice";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { CheckCircle, FileText } from "lucide-react";
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

const IDR = (val) =>
  new Intl.NumberFormat("id-ID", {
    style: "currency", currency: "IDR", maximumFractionDigits: 0,
  }).format(val ?? 0);

export default function ClientPortalPage() {
  const { token }               = useParams();
  const [quotation, setQ]       = useState(null);
  const [loading, setLoading]   = useState(true);
  const [error, setError]       = useState(null);
  const [approving, setApproving] = useState(false);
  const [approved, setApproved] = useState(false);

  useEffect(() => {
    fetchClientPortal(token)
      .then(setQ)
      .catch(() => setError("Quotation tidak ditemukan atau link tidak valid."))
      .finally(() => setLoading(false));
  }, [token]);

  const handleApprove = async () => {
    if (!confirm("Anda yakin ingin menyetujui quotation ini?")) return;
    setApproving(true);
    try {
      await approveQuotationAsClient(token);
      setApproved(true);
      setQ(q => ({ ...q, status: "approved" }));
    } catch {
      alert("Gagal menyetujui. Silakan coba lagi.");
    } finally {
      setApproving(false);
    }
  };

  if (loading) return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-800" />
    </div>
  );

  if (error) return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
      <Card className="max-w-md w-full">
        <CardContent className="py-12 text-center">
          <p className="text-slate-500">{error}</p>
        </CardContent>
      </Card>
    </div>
  );

  if (!quotation) return null;
  const q = quotation;

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Top bar */}
      <div className="bg-white border-b">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-slate-900 rounded-lg flex items-center justify-center">
              <FileText size={16} className="text-white" />
            </div>
            <div>
              <p className="font-bold text-slate-900 text-sm">EventHub</p>
              <p className="text-xs text-slate-400">Quotation Portal</p>
            </div>
          </div>
          <span className={`text-xs font-medium px-3 py-1.5 rounded-full border ${
            q.status === "approved"
              ? "bg-emerald-50 text-emerald-700 border-emerald-200"
              : "bg-blue-50 text-blue-700 border-blue-200"
          }`}>
            {q.status === "approved" ? "✓ Disetujui" : "Menunggu Persetujuan"}
          </span>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 py-8 space-y-6">

        {/* Header card */}
        <Card className="border-slate-200">
          <CardContent className="p-6">
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 text-sm">
              <div>
                <p className="text-xs text-slate-400 mb-1">Event</p>
                <p className="font-semibold text-slate-800">{q.event_title}</p>
              </div>
              <div>
                <p className="text-xs text-slate-400 mb-1">No. Quotation</p>
                <p className="font-mono font-medium text-slate-700">{q.quotation_number}</p>
              </div>
              <div>
                <p className="text-xs text-slate-400 mb-1">Revisi</p>
                <p className="font-medium text-slate-700">Rev. {q.revision}</p>
              </div>
              <div>
                <p className="text-xs text-slate-400 mb-1">Klien</p>
                <p className="font-semibold text-slate-800">{q.client_company}</p>
              </div>
              <div>
                <p className="text-xs text-slate-400 mb-1">PIC</p>
                <p className="font-medium text-slate-700">{q.client_pic}</p>
              </div>
              {q.event_dates?.start && (
                <div>
                  <p className="text-xs text-slate-400 mb-1">Tanggal Event</p>
                  <p className="font-medium text-slate-700">
                    {new Date(q.event_dates.start).toLocaleDateString("id-ID", {
                      day: "numeric", month: "long", year: "numeric",
                    })}
                  </p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Sections */}
        {(q.sections ?? []).map(section => (
          <Card key={section.id} className="border-slate-200">
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <CardTitle className="text-xs font-bold uppercase tracking-widest text-slate-500">
                  {section.name}
                </CardTitle>
                <span className="text-sm font-bold font-mono text-emerald-600">
                  {IDR(section.subtotal_client)}
                </span>
              </div>
            </CardHeader>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-100 bg-slate-50">
                      <th className="px-4 py-2 text-left text-xs font-medium text-slate-400">Item</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-slate-400">Detail</th>
                      <th className="px-4 py-2 text-right text-xs font-medium text-slate-400">QTY</th>
                      <th className="px-4 py-2 text-right text-xs font-medium text-slate-400">Dur</th>
                      <th className="px-4 py-2 text-right text-xs font-medium text-slate-400">Harga Satuan</th>
                      <th className="px-4 py-2 text-right text-xs font-bold text-emerald-600">Total</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(section.line_items ?? []).map(item => (
                      <tr key={item.id} className="border-b border-slate-50 hover:bg-slate-50/50">
                        <td className="px-4 py-2.5 font-medium text-slate-800">{item.item_name}</td>
                        <td className="px-4 py-2.5 text-slate-500 text-xs">{item.detail}</td>
                        <td className="px-4 py-2.5 text-right text-xs text-slate-500">
                          {item.qty} {item.vol_unit_display || item.vol_unit}
                        </td>
                        <td className="px-4 py-2.5 text-right text-xs text-slate-500">
                          {item.duration} {item.dur_unit_display || item.dur_unit}
                        </td>
                        <td className="px-4 py-2.5 text-right font-mono text-xs text-slate-600">
                          {IDR(item.client_price)}
                        </td>
                        <td className="px-4 py-2.5 text-right font-mono font-semibold text-emerald-600">
                          {IDR(item.total_client)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        ))}

        {/* Financial summary */}
        <Card className="border-slate-200">
          <CardHeader>
            <CardTitle className="text-base">Ringkasan Pembayaran</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="max-w-xs ml-auto space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-slate-500">Subtotal</span>
                <span className="font-mono">{IDR(q.subtotal_client)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-500">Fee Management</span>
                <span className="font-mono">{IDR(q.fee_management_amt)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-500">PPN (11%)</span>
                <span className="font-mono">{IDR(q.ppn_amt)}</span>
              </div>
              <Separator />
              <div className="flex justify-between font-bold text-base">
                <span>TOTAL</span>
                <span className="font-mono text-emerald-600">{IDR(q.total_after_tax)}</span>
              </div>

              {parseFloat(q.payment_term_1) > 0 && (
                <>
                  <Separator className="my-3" />
                  <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">
                    Termin Pembayaran
                  </p>
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-500">Termin 1 (Pertama)</span>
                    <span className="font-mono">{IDR(q.payment_term_1)}</span>
                  </div>
                  {parseFloat(q.payment_term_2) > 0 && (
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-500">Termin 2 (Turun 2)</span>
                      <span className="font-mono">{IDR(q.payment_term_2)}</span>
                    </div>
                  )}
                </>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Approval */}
        {q.status !== "approved" && !approved && (
          <Card className="border-2 border-slate-800">
            <CardContent className="py-8 text-center">
              <p className="text-slate-600 mb-2 text-sm max-w-md mx-auto">
                Dengan menekan tombol di bawah, Anda menyatakan setuju dengan proposal
                dan total biaya yang tercantum.
              </p>
              <p className="text-slate-400 text-xs mb-6">
                Total: <span className="font-bold text-slate-700">{IDR(q.total_after_tax)}</span>
              </p>
              <Button
                size="lg"
                className="bg-slate-900 hover:bg-slate-700 px-10 gap-2"
                onClick={handleApprove}
                disabled={approving}
              >
                {approving ? "Memproses..." : "Setujui Quotation Ini"}
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Approved */}
        {(q.status === "approved" || approved) && (
          <Card className="border-2 border-emerald-300 bg-emerald-50">
            <CardContent className="py-10 text-center">
              <CheckCircle size={44} className="mx-auto text-emerald-500 mb-3" />
              <h2 className="text-lg font-bold text-emerald-800 mb-1">
                Quotation Telah Disetujui
              </h2>
              <p className="text-sm text-emerald-600 max-w-sm mx-auto">
                Terima kasih! Tim Mahesa Creative akan segera menghubungi Anda untuk langkah selanjutnya.
              </p>
            </CardContent>
          </Card>
        )}

        <p className="text-center text-xs text-slate-300 pb-4">
          Dokumen ini dibuat oleh EventHub · eventhub.chrisimbolon.dev
        </p>
      </div>
    </div>
  );
}
