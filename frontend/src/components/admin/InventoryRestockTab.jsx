import React, { useState, useEffect } from 'react';
import { Layers, Plus, RefreshCw, AlertCircle } from 'lucide-react';
import { adminApi } from '../../api';
import { useToast } from '../../context/ToastContext';

export default function InventoryRestockTab() {
  const { showToast } = useToast();
  const [inventory, setInventory] = useState([]);
  const [selectedEditionId, setSelectedEditionId] = useState('');
  const [restockQty, setRestockQty] = useState(10);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const fetchInventory = () => {
    setIsLoading(true);
    adminApi
      .getInventory()
      .then((data) => {
        const items = data.inventory || [];
        setInventory(items);
        if (items.length > 0 && !selectedEditionId) {
          setSelectedEditionId(items[0].edition_id);
        }
      })
      .catch((err) => showToast('Lỗi tải tồn kho: ' + err.message, 'error'))
      .finally(() => setIsLoading(false));
  };

  useEffect(() => {
    fetchInventory();
  }, []);

  const handleRestockSubmit = async (e) => {
    e.preventDefault();
    if (!selectedEditionId || restockQty <= 0) return;

    setIsSubmitting(true);
    try {
      await adminApi.restock(selectedEditionId, restockQty);
      showToast(`Đã nhập kho thành công +${restockQty} cuốn cho ấn bản!`, 'success');
      fetchInventory();
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Restock Form */}
      <div className="bg-white rounded-2xl border border-stone-200 p-6 shadow-sm">
        <div className="flex items-center gap-2 pb-3 mb-4 border-b border-stone-100">
          <Plus className="w-5 h-5 text-crimson-700" />
          <h3 className="font-serif-title font-bold text-base text-stone-900">
            Lập Phiếu Nhập Kho Ấn Bản Mới (UC12)
          </h3>
        </div>

        <form onSubmit={handleRestockSubmit} className="grid grid-cols-1 sm:grid-cols-12 gap-3 items-end">
          <div className="sm:col-span-7">
            <label className="block text-[11px] font-bold text-stone-600 mb-1">
              Chọn Tựa Sách & Quy Cách Ấn Bản (SKU):
            </label>
            <select
              value={selectedEditionId}
              onChange={(e) => setSelectedEditionId(e.target.value)}
              className="w-full bg-stone-50 border border-stone-300 rounded-xl px-3 py-2 text-xs text-stone-800 font-medium focus:outline-none focus:ring-2 focus:ring-crimson-700/20"
            >
              {inventory.map((item) => (
                <option key={item.edition_id} value={item.edition_id}>
                  {item.title} ({item.binding_type === 'PAPERBACK' ? 'Bìa Mềm' : 'Bìa Cứng'}) - SKU: {item.sku}
                </option>
              ))}
            </select>
          </div>

          <div className="sm:col-span-3">
            <label className="block text-[11px] font-bold text-stone-600 mb-1">
              Số Lượng Nhập (Cuốn):
            </label>
            <input
              type="number"
              min="1"
              max="500"
              value={restockQty}
              onChange={(e) => setRestockQty(parseInt(e.target.value, 10) || 1)}
              className="w-full bg-stone-50 border border-stone-300 rounded-xl px-3 py-2 text-xs font-bold text-stone-800 focus:outline-none focus:ring-2 focus:ring-crimson-700/20"
            />
          </div>

          <div className="sm:col-span-2">
            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full py-2 px-4 rounded-xl bg-crimson-700 hover:bg-crimson-800 text-white text-xs font-bold transition shadow disabled:opacity-50 flex items-center justify-center gap-1.5"
            >
              <Plus className="w-4 h-4" />
              <span>{isSubmitting ? 'Đang Nhập...' : 'Nhập Kho'}</span>
            </button>
          </div>
        </form>
      </div>

      {/* 3-State Inventory Table */}
      <div className="bg-white rounded-2xl border border-stone-200 p-6 shadow-sm space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-stone-100">
          <div>
            <h3 className="font-serif-title font-bold text-base text-stone-900">
              Kiểm Soát Tồn Kho 3 Trạng Thái Thời Gian Thực
            </h3>
            <p className="text-xs text-stone-500">
              Tồn thực tế = Tồn giữ chỗ 15 phút + Tồn khả dụng (Invariant Check)
            </p>
          </div>
          <button
            onClick={fetchInventory}
            className="p-2 text-stone-500 hover:text-crimson-700 rounded-lg hover:bg-stone-50 transition"
            title="Làm mới"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
        </div>

        {isLoading ? (
          <div className="py-16 text-center text-xs text-stone-500">Đang đồng bộ số liệu tồn kho...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-stone-200 text-stone-400 font-semibold uppercase text-[10px]">
                  <th className="py-3 px-2">SKU</th>
                  <th className="py-3 px-2">Tác Phẩm & Quy Cách</th>
                  <th className="py-3 px-2 text-center">Tồn Thực Tế</th>
                  <th className="py-3 px-2 text-center">Đang Giữ Chỗ (15p)</th>
                  <th className="py-3 px-2 text-center">Khả Dụng Bán</th>
                  <th className="py-3 px-2 text-center">Trạng Thái</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-stone-100">
                {inventory.map((item) => {
                  const isLowStock = (item.available_stock || 0) <= 2;
                  return (
                    <tr key={item.edition_id} className="hover:bg-stone-50/70 transition">
                      <td className="py-3 px-2 font-mono font-bold text-stone-700">{item.sku}</td>
                      <td className="py-3 px-2">
                        <span className="font-bold text-stone-900 block">{item.title}</span>
                        <span className="text-[10px] text-stone-500">
                          {item.binding_type === 'PAPERBACK' ? '📖 Bìa Mềm' : '📕 Bìa Cứng'} • {item.weight_grams}g
                        </span>
                      </td>
                      <td className="py-3 px-2 text-center font-bold text-stone-800">
                        {item.stock_on_hand}
                      </td>
                      <td className="py-3 px-2 text-center font-bold text-amber-600">
                        {item.stock_reserved || 0}
                      </td>
                      <td className="py-3 px-2 text-center font-bold text-emerald-700 text-sm">
                        {item.available_stock}
                      </td>
                      <td className="py-3 px-2 text-center">
                        {isLowStock ? (
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-red-100 text-red-800">
                            Sắp Hết
                          </span>
                        ) : (
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800">
                            Dồi Dào
                          </span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
