import React from 'react';

export default function AnnouncementBar() {
  return (
    <div className="bg-stone-900 text-stone-200 text-xs py-2 px-4 border-b border-stone-800">
      <div className="max-w-7xl mx-auto flex justify-center items-center gap-2 text-center">
        <span className="inline-block w-2 h-2 rounded-full bg-emerald-500 animate-pulse shrink-0"></span>
        <span>
          Chính Hãng NXB Trẻ, Kim Đồng, Dân Trí • Giao siêu tốc nội thành bằng{' '}
          <strong className="text-white">Hanoi Drone</strong> (dưới 2kg) trong 30-45 phút
        </span>
      </div>
    </div>
  );
}
