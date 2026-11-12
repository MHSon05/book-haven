import React from 'react';
import { X, ZoomIn } from 'lucide-react';

export default function LightboxModal({ isOpen, onClose, imageSrc, title }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-stone-950/80 backdrop-blur-md transition-opacity"
        onClick={onClose}
      ></div>

      {/* Content */}
      <div className="relative z-10 max-w-2xl max-h-[90vh] flex flex-col items-center">
        <button
          onClick={onClose}
          className="absolute -top-10 right-0 text-white/80 hover:text-white p-1 rounded-full bg-stone-800/60 transition"
          title="Đóng (ESC)"
        >
          <X className="w-6 h-6" />
        </button>

        <img
          src={imageSrc}
          alt={title}
          className="max-h-[80vh] w-auto object-contain rounded-2xl shadow-2xl border border-white/20"
        />

        <div className="mt-3 text-center">
          <p className="text-white text-sm font-bold font-serif-title">{title}</p>
          <p className="text-stone-400 text-xs">Ảnh bìa độ phân giải cao phục vụ triển lãm và sưu tầm</p>
        </div>
      </div>
    </div>
  );
}
