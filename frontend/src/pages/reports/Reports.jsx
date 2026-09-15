import React from 'react'
import { FileText, Download, Share2, ShieldCheck, Printer } from 'lucide-react'
import { useToast } from '../../components/ui/Toast'

export default function Reports() {
  const { showToast } = useToast()

  function handleDownload(title) {
    showToast(`Generating ${title} PDF...`, 'info')
    setTimeout(() => {
      showToast(`${title} ready for download!`, 'success')
    }, 1500)
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gradient flex items-center gap-2">
            <FileText className="w-6 h-6 text-emerald-400" /> Agronomic Reports & Exports
          </h1>
          <p className="text-sm text-muted">Generate certified farm health audits, disease logs, and financial summaries</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card-glass p-6 space-y-4 hover:border-emerald-500/40 transition">
          <div className="w-12 h-12 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <h3 className="font-bold text-lg text-white">Full Farm Health Audit</h3>
            <p className="text-xs text-muted mt-1">Includes soil score, disease diagnostic log, moisture trends, and AI recommendations.</p>
          </div>
          <button onClick={() => handleDownload('Farm Health Audit')} className="btn btn-primary w-full text-xs flex items-center justify-center gap-2">
            <Download className="w-4 h-4" /> Download PDF Report
          </button>
        </div>

        <div className="card-glass p-6 space-y-4 hover:border-cyan-500/40 transition">
          <div className="w-12 h-12 rounded-xl bg-cyan-500/20 text-cyan-400 flex items-center justify-center">
            <FileText className="w-6 h-6" />
          </div>
          <div>
            <h3 className="font-bold text-lg text-white">Financial & Expense Ledger</h3>
            <p className="text-xs text-muted mt-1">Categorized spending, labor costs, input fertilizer investments, and yield ROI.</p>
          </div>
          <button onClick={() => handleDownload('Expense Ledger')} className="btn btn-secondary w-full text-xs flex items-center justify-center gap-2">
            <Download className="w-4 h-4" /> Export CSV / PDF
          </button>
        </div>

        <div className="card-glass p-6 space-y-4 hover:border-purple-500/40 transition">
          <div className="w-12 h-12 rounded-xl bg-purple-500/20 text-purple-400 flex items-center justify-center">
            <Printer className="w-6 h-6" />
          </div>
          <div>
            <h3 className="font-bold text-lg text-white">SIH 2026 Compliance Audit</h3>
            <p className="text-xs text-muted mt-1">Technical report covering PyTorch leaf disease metrics, confusion matrix, and agent traces.</p>
          </div>
          <button onClick={() => handleDownload('SIH Compliance Report')} className="btn btn-secondary w-full text-xs flex items-center justify-center gap-2">
            <Download className="w-4 h-4" /> Export Audit Doc
          </button>
        </div>
      </div>
    </div>
  )
}
