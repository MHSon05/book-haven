import React from 'react';

export default function SpecsTable({ book, selectedEdition }) {
  return (
    <div className="bg-stone-50 rounded-2xl border border-stone-200 p-4 text-xs">
      <h4 className="font-bold text-stone-900 mb-3 uppercase tracking-wider text-[11px]">
        Thông Số Kỹ Thuật Chế Tác
      </h4>

      <div className="grid grid-cols-2 gap-y-2.5 gap-x-4">
        <div>
          <span className="text-stone-500 block text-[10px]">Nhà xuất bản:</span>
          <span className="font-semibold text-stone-800">{book.publisher_name || 'NXB Trẻ / Kim Đồng'}</span>
        </div>

        <div>
          <span className="text-stone-500 block text-[10px]">Năm xuất bản:</span>
          <span className="font-semibold text-stone-800">{book.publish_year || 2023}</span>
        </div>

        <div>
          <span className="text-stone-500 block text-[10px]">Mã chuẩn ISBN-13:</span>
          <span className="font-semibold text-stone-800 font-mono">
            {selectedEdition?.isbn13 || selectedEdition?.isbn || 'Đang cập nhật'}
          </span>
        </div>

        <div>
          <span className="text-stone-500 block text-[10px]">Trọng lượng thực tế:</span>
          <span className="font-semibold text-stone-800">{selectedEdition?.weight_gram || selectedEdition?.weight_grams || 350}g</span>
        </div>

        <div>
          <span className="text-stone-500 block text-[10px]">Tác giả tác phẩm:</span>
          <span className="font-semibold text-stone-800">{book.author_name || 'Đang cập nhật'}</span>
        </div>

        <div>
          <span className="text-stone-500 block text-[10px]">Quy cách ấn bản:</span>
          <span className="font-semibold text-stone-800">
            {selectedEdition?.binding_type === 'HARDCOVER' ? 'Bìa Cứng cao cấp' : 'Bìa Mềm tiêu chuẩn'}
          </span>
        </div>
      </div>
    </div>
  );
}
