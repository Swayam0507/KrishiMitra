import React, { useEffect, useState } from 'react'
import { Wallet, Plus, TrendingDown, DollarSign, Calendar, Search, Filter, PieChart, ArrowUpRight, Trash2, X, Download } from 'lucide-react'
import { expenseService } from '../../services'
import { useToast } from '../../components/ui/Toast'

const CATEGORIES = ['Fertilizers', 'Seeds', 'Labor', 'Irrigation', 'Pesticides', 'Equipment', 'Other']

export default function ExpenseList() {
  const { showToast } = useToast()
  const [expenses, setExpenses] = useState([
    { id: '1', title: 'NPK 19-19-19 Fertilizer Purchase (50kg)', category: 'Fertilizers', amount: 14000, date: '2026-09-02', plot: 'Plot A — Tomato', notes: 'Procured from AgriGov Depot' },
    { id: '2', title: 'Hybrid Seeds Procurement (Pioneer 3397)', category: 'Seeds', amount: 8500, date: '2026-09-05', plot: 'Plot C — Corn', notes: 'Certified hybrid seeds' },
    { id: '3', title: 'Weekly Labor Wages (Harvest & Weeding)', category: 'Labor', amount: 12800, date: '2026-09-10', plot: 'All Plots', notes: '8 workers for 4 days' },
    { id: '4', title: 'Electricity & Diesel for Drip Pump', category: 'Irrigation', amount: 7200, date: '2026-09-12', plot: 'Plot B & D', notes: 'Drip system maintenance & power' },
    { id: '5', title: 'Copper Oxychloride Fungicide (5 Liters)', category: 'Pesticides', amount: 3600, date: '2026-09-13', plot: 'Plot B — Potato', notes: 'Blight preventive spray' }
  ])

  const [loading, setLoading] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('All')
  const [isModalOpen, setIsModalOpen] = useState(false)
  
  const seasonalBudget = 75000

  // Form State
  const [formData, setFormData] = useState({
    title: '',
    category: 'Fertilizers',
    amount: '',
    plot: 'Plot A — Tomato',
    date: new Date().toISOString().split('T')[0],
    notes: ''
  })

  // Calculations
  const totalSpend = expenses.reduce((sum, exp) => sum + (Number(exp.amount) || 0), 0)
  const budgetUtilization = Math.min(100, Math.round((totalSpend / seasonalBudget) * 100))
  
  const categoryTotals = CATEGORIES.reduce((acc, cat) => {
    acc[cat] = expenses.filter(e => e.category === cat).reduce((s, e) => s + (Number(e.amount) || 0), 0)
    return acc
  }, {})

  const filteredExpenses = expenses.filter(exp => {
    const matchesSearch = exp.title.toLowerCase().includes(searchQuery.toLowerCase()) || exp.plot.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesCat = selectedCategory === 'All' || exp.category === selectedCategory
    return matchesSearch && matchesCat
  })

  const handleCreateExpense = (e) => {
    e.preventDefault()
    if (!formData.title || !formData.amount) {
      showToast('Please enter title and amount', 'error')
      return
    }

    const newExp = {
      id: Date.now().toString(),
      title: formData.title,
      category: formData.category,
      amount: Number(formData.amount),
      plot: formData.plot,
      date: formData.date,
      notes: formData.notes
    }

    setExpenses([newExp, ...expenses])
    setIsModalOpen(false)
    setFormData({
      title: '',
      category: 'Fertilizers',
      amount: '',
      plot: 'Plot A — Tomato',
      date: new Date().toISOString().split('T')[0],
      notes: ''
    })
    showToast('Expense recorded successfully!', 'success')
  }

  const handleDeleteExpense = (id) => {
    setExpenses(expenses.filter(e => e.id !== id))
    showToast('Expense item removed', 'info')
  }

  const handleExportCSV = () => {
    const headers = ['Title', 'Category', 'Plot', 'Date', 'Amount (INR)', 'Notes']
    const rows = expenses.map(e => [e.title, e.category, e.plot, e.date, e.amount, e.notes || ''])
    const csvContent = "data:text/csv;charset=utf-8," + [headers.join(','), ...rows.map(e => e.join(','))].join('\n')
    const encodedUri = encodeURI(csvContent)
    const link = document.createElement('a')
    link.setAttribute('href', encodedUri)
    link.setAttribute('download', `AgriFlow_Expenses_${new Date().toISOString().split('T')[0]}.csv`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    showToast('Expenses exported to CSV!', 'success')
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gradient flex items-center gap-2">
            <Wallet className="w-6 h-6 text-emerald-400" /> Farm Expenses & Budget
          </h1>
          <p className="text-sm text-muted">Track operational costs, input investments, and seasonal financial budget</p>
        </div>

        <div className="flex items-center gap-2">
          <button onClick={handleExportCSV} className="btn btn-secondary flex items-center gap-2 text-xs font-semibold">
            <Download className="w-4 h-4" /> Export CSV
          </button>
          <button onClick={() => setIsModalOpen(true)} className="btn btn-primary flex items-center gap-2 text-xs font-semibold">
            <Plus className="w-4 h-4" /> Record Expense
          </button>
        </div>
      </div>

      {/* Top Financial Stat Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card-glass p-5 border-l-4 border-l-emerald-500 flex flex-col justify-between">
          <div>
            <span className="text-muted text-xs uppercase font-bold tracking-wider">Total Seasonal Spend</span>
            <div className="text-3xl font-extrabold text-white mt-1 font-mono">₹{totalSpend.toLocaleString()}</div>
          </div>
          <div className="text-xs text-emerald-400 mt-2 font-medium flex items-center gap-1">
            <ArrowUpRight size={14} /> Total 10.0 Acres Farm Budget
          </div>
        </div>

        <div className="card-glass p-5 flex flex-col justify-between">
          <div>
            <span className="text-muted text-xs uppercase font-bold tracking-wider">Seasonal Budget Utilized</span>
            <div className="text-2xl font-bold text-white mt-1">{budgetUtilization}%</div>
          </div>
          <div className="w-full bg-white/10 rounded-full h-2 mt-2 overflow-hidden">
            <div
              className={`h-full transition-all duration-500 ${
                budgetUtilization > 85 ? 'bg-rose-500' : budgetUtilization > 70 ? 'bg-amber-400' : 'bg-emerald-400'
              }`}
              style={{ width: `${budgetUtilization}%` }}
            />
          </div>
          <div className="text-[11px] text-muted mt-1">₹{(seasonalBudget - totalSpend).toLocaleString()} Remaining of ₹{seasonalBudget.toLocaleString()}</div>
        </div>

        <div className="card-glass p-5 flex flex-col justify-between">
          <div>
            <span className="text-muted text-xs uppercase font-bold tracking-wider">Fertilizers & Inputs</span>
            <div className="text-2xl font-bold text-emerald-400 mt-1 font-mono">
              ₹{(categoryTotals['Fertilizers'] + categoryTotals['Pesticides'] + categoryTotals['Seeds']).toLocaleString()}
            </div>
          </div>
          <div className="text-xs text-muted mt-2">
            Seeds: ₹{categoryTotals['Seeds'].toLocaleString()} • Protection: ₹{categoryTotals['Pesticides'].toLocaleString()}
          </div>
        </div>

        <div className="card-glass p-5 flex flex-col justify-between">
          <div>
            <span className="text-muted text-xs uppercase font-bold tracking-wider">Labor & Operations</span>
            <div className="text-2xl font-bold text-amber-400 mt-1 font-mono">
              ₹{(categoryTotals['Labor'] + categoryTotals['Irrigation']).toLocaleString()}
            </div>
          </div>
          <div className="text-xs text-muted mt-2">
            Labor: ₹{categoryTotals['Labor'].toLocaleString()} • Water: ₹{categoryTotals['Irrigation'].toLocaleString()}
          </div>
        </div>
      </div>

      {/* Category Breakdown Progress Bars */}
      <div className="card-glass p-5">
        <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4 flex items-center gap-2">
          <PieChart size={16} className="text-emerald-400" /> Investment Breakdown by Category
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {CATEGORIES.map(cat => {
            const amount = categoryTotals[cat] || 0
            const pct = totalSpend > 0 ? Math.round((amount / totalSpend) * 100) : 0
            return (
              <div key={cat} className="p-3 rounded-xl bg-white/5 border border-white/5">
                <div className="text-xs text-muted font-medium">{cat}</div>
                <div className="text-lg font-bold text-white mt-0.5 font-mono">₹{amount.toLocaleString()}</div>
                <div className="flex items-center gap-2 mt-2">
                  <div className="flex-1 bg-white/10 rounded-full h-1.5 overflow-hidden">
                    <div className="bg-emerald-400 h-full" style={{ width: `${pct}%` }} />
                  </div>
                  <span className="text-[10px] text-emerald-400 font-bold">{pct}%</span>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Filters & Search Toolbar */}
      <div className="flex flex-col sm:flex-row justify-between items-center gap-3">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 absolute left-3 top-3 text-muted" />
          <input
            type="text"
            placeholder="Search expense item or plot..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            className="form-input pl-9 text-xs"
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto overflow-x-auto">
          <span className="text-xs text-muted flex items-center gap-1"><Filter size={12} /> Category:</span>
          <button
            onClick={() => setSelectedCategory('All')}
            className={`btn btn-xs ${selectedCategory === 'All' ? 'btn-primary' : 'btn-secondary text-gray-300'}`}
          >
            All ({expenses.length})
          </button>
          {CATEGORIES.map(cat => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`btn btn-xs ${selectedCategory === cat ? 'btn-primary' : 'btn-secondary text-gray-300'}`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Expense Log Table */}
      <div className="table-container card-glass">
        <table className="data-table">
          <thead>
            <tr>
              <th>Expense Item</th>
              <th>Category</th>
              <th>Plot Allocated</th>
              <th>Date Recorded</th>
              <th>Notes / Details</th>
              <th className="text-right">Amount (₹)</th>
              <th className="text-center">Action</th>
            </tr>
          </thead>
          <tbody>
            {filteredExpenses.length > 0 ? (
              filteredExpenses.map((exp) => (
                <tr key={exp.id}>
                  <td className="font-semibold text-white">{exp.title}</td>
                  <td>
                    <span className="badge badge-green text-[10px]">{exp.category}</span>
                  </td>
                  <td className="text-gray-300 text-xs">{exp.plot}</td>
                  <td className="text-muted text-xs font-mono">{exp.date}</td>
                  <td className="text-xs text-gray-400 italic max-w-xs truncate">{exp.notes || '—'}</td>
                  <td className="text-right font-mono font-bold text-emerald-400 text-sm">
                    ₹{Number(exp.amount).toLocaleString()}
                  </td>
                  <td className="text-center">
                    <button
                      onClick={() => handleDeleteExpense(exp.id)}
                      className="btn btn-ghost btn-icon text-gray-400 hover:text-rose-400 p-1"
                      title="Delete expense"
                    >
                      <Trash2 size={15} />
                    </button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="7" className="text-center py-8 text-muted">
                  No expense records match your search query or filter.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Record Expense Modal */}
      {isModalOpen && (
        <div className="modal-overlay">
          <div className="card-glass p-6 max-w-md w-full border border-white/10 space-y-4 animate-in fade-in duration-200">
            <div className="flex justify-between items-center pb-2 border-b border-white/10">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Wallet className="w-5 h-5 text-emerald-400" /> Record New Farm Expense
              </h3>
              <button onClick={() => setIsModalOpen(false)} className="btn btn-ghost btn-icon text-muted hover:text-white">
                <X size={18} />
              </button>
            </div>

            <form onSubmit={handleCreateExpense} className="space-y-4">
              <div>
                <label className="form-label">Expense Title / Description</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. NPK Fertilizer 50kg, Worker Wages"
                  className="form-input"
                  value={formData.title}
                  onChange={e => setFormData({ ...formData, title: e.target.value })}
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="form-label">Category</label>
                  <select
                    className="form-select"
                    value={formData.category}
                    onChange={e => setFormData({ ...formData, category: e.target.value })}
                  >
                    {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
                  </select>
                </div>
                <div>
                  <label className="form-label">Amount (₹)</label>
                  <input
                    type="number"
                    required
                    min="1"
                    placeholder="e.g. 5000"
                    className="form-input"
                    value={formData.amount}
                    onChange={e => setFormData({ ...formData, amount: e.target.value })}
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="form-label">Plot Allocated</label>
                  <select
                    className="form-select"
                    value={formData.plot}
                    onChange={e => setFormData({ ...formData, plot: e.target.value })}
                  >
                    <option value="All Plots">All Plots</option>
                    <option value="Plot A — Tomato">Plot A — Tomato</option>
                    <option value="Plot B — Potato">Plot B — Potato</option>
                    <option value="Plot C — Corn">Plot C — Corn</option>
                    <option value="Plot D — Pepper">Plot D — Pepper</option>
                  </select>
                </div>
                <div>
                  <label className="form-label">Date</label>
                  <input
                    type="date"
                    className="form-input"
                    value={formData.date}
                    onChange={e => setFormData({ ...formData, date: e.target.value })}
                  />
                </div>
              </div>

              <div>
                <label className="form-label">Vendor / Additional Notes</label>
                <textarea
                  rows="2"
                  placeholder="Optional notes or supplier info..."
                  className="form-input"
                  value={formData.notes}
                  onChange={e => setFormData({ ...formData, notes: e.target.value })}
                />
              </div>

              <div className="flex gap-2 pt-2">
                <button type="button" onClick={() => setIsModalOpen(false)} className="btn btn-secondary flex-1">
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary flex-1">
                  Save Expense
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
