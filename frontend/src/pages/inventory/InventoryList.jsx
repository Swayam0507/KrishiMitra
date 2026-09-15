import React, { useEffect, useState } from 'react'
import { Package, Plus, AlertTriangle, CheckCircle } from 'lucide-react'
import { inventoryService } from '../../services'
import { useToast } from '../../components/ui/Toast'

export default function InventoryList() {
  const { showToast } = useToast()
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadInventory() {
      try {
        const res = await inventoryService.list().catch(() => ({ data: [] }))
        const list = res.data?.items || res.data || [
          { id: '1', name: 'NPK 19-19-19 Fertilizer', category: 'Fertilizer', quantity: 250, unit: 'kg', min_threshold: 100, status: 'In Stock' },
          { id: '2', name: 'Copper Oxychloride Fungicide', category: 'Pesticide', quantity: 12, unit: 'kg', min_threshold: 20, status: 'Low Stock' },
          { id: '3', name: 'Drip Emitter Spare Nozzles', category: 'Equipment', quantity: 150, unit: 'pcs', min_threshold: 50, status: 'In Stock' },
          { id: '4', name: 'Hybrid Sweet Corn Seeds', category: 'Seeds', amount: 5, unit: 'kg', min_threshold: 10, status: 'Low Stock' }
        ]
        setItems(list)
      } catch (err) {
        showToast('Error loading inventory', 'error')
      } finally {
        setLoading(false)
      }
    }
    loadInventory()
  }, [])

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gradient">Farm Inventory & Supplies</h1>
          <p className="text-sm text-muted">Stock tracking for fertilizers, seeds, pesticides, and spare parts</p>
        </div>
        <button onClick={() => showToast('New stock item entry', 'info')} className="btn btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" /> Add Inventory Item
        </button>
      </div>

      {loading ? (
        <div className="card-glass p-6 text-center text-muted">Loading inventory stock...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {items.map((item) => {
            const isLow = item.quantity <= item.min_threshold || item.status === 'Low Stock'
            return (
              <div key={item.id} className={`card-glass p-5 flex flex-col justify-between ${isLow ? 'border-amber-500/50 bg-amber-500/5' : ''}`}>
                <div>
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="font-semibold text-white">{item.name}</h3>
                    <span className={`badge ${isLow ? 'badge-warning' : 'badge-success'}`}>
                      {isLow ? 'Low Stock' : 'Sufficient'}
                    </span>
                  </div>
                  <p className="text-xs text-emerald-300 font-medium mb-3">{item.category}</p>

                  <div className="text-2xl font-bold text-white mb-1">
                    {item.quantity} <span className="text-sm text-muted font-normal">{item.unit}</span>
                  </div>
                  <div className="text-xs text-muted">Reorder Threshold: {item.min_threshold} {item.unit}</div>
                </div>

                <div className="mt-4 pt-3 border-t border-white/5 flex justify-between items-center text-xs">
                  <button className="text-emerald-400 hover:underline">Adjust Stock</button>
                  {isLow && <span className="text-amber-400 flex items-center gap-1 font-medium"><AlertTriangle className="w-3 h-3" /> Restock Urgently</span>}
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
