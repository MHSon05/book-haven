import React from 'react';
import { ArrowRight, Compass } from 'lucide-react';
import chuaMotCotImg from '../../assets/chua_mot_cot.jpg';

export default function HeroBanner() {
  const handleExplore = (e) => {
    e.preventDefault();
    const el = document.getElementById('books-grid');
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };
  return (
    <div className="relative mb-8 overflow-hidden rounded-3xl bg-[#120a08] text-white shadow-2xl border border-stone-800/50 min-h-[360px] sm:min-h-[400px] flex items-center">
      {/* Right Side: High-Resolution Photographic Chùa Một Cột Artwork */}
      <div className="absolute right-0 top-0 bottom-0 w-full sm:w-2/3 lg:w-3/5 pointer-events-none select-none overflow-hidden">
        {/* Smooth horizontal gradient fade on the left edge of the image */}
        <div className="absolute inset-0 bg-gradient-to-r from-[#120a08] via-[#120a08]/80 sm:via-[#120a08]/40 to-transparent z-10 pointer-events-none"></div>
        {/* Subtle top and bottom dark vignettes */}
        <div className="absolute inset-0 bg-gradient-to-t from-[#120a08]/70 via-transparent to-[#120a08]/40 z-10 pointer-events-none"></div>
        <img
          src={chuaMotCotImg}
          alt="Chùa Một Cột Hà Nội & Hồ Sen"
          className="h-full w-full object-cover object-right sm:object-center"
        />
      </div>

      {/* Left Side: Sharp, Crisp Vector HTML/CSS Typography & Single CTA */}
      <div className="relative z-20 max-w-2xl p-6 sm:p-10 md:p-12 lg:p-14">
        {/* Official Publisher & Drone Badge */}
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white/10 backdrop-blur-md border border-white/15 text-[10px] sm:text-[11px] font-semibold text-amber-300 mb-4 sm:mb-6 shadow-sm">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
          <span>CHÍNH HÃNG KIM ĐỒNG & NXB TRẺ • GIAO HỎA TỐC BẰNG DRONE</span>
        </div>

        {/* Elegant Serif Headline */}
        <h1 className="font-serif-title text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold leading-tight mb-4 text-stone-100 drop-shadow">
          Những Câu Chuyện <br />
          <span className="text-crimson-500 italic font-serif">Lay Động Tâm Hồn</span>{' '}
          <span className="text-stone-100">& Tri Thức Bất Tận</span>
        </h1>

        {/* Crisp Subtitle */}
        <p className="text-xs sm:text-sm text-stone-300 font-light leading-relaxed mb-6 max-w-xl drop-shadow">
          Chào mừng bạn đến với <strong>BookHaven</strong> — không gian sách tuyển chọn, quy tụ các ấn bản sưu tầm và giấy mỹ thuật cao cấp. Trải nghiệm hệ thống giao vận bằng Drone thế hệ mới và tư vấn sách thông minh cùng Trợ lý ảo AI BookHaven.
        </p>

        {/* Single Modern CTA Button */}
        <div>
          <button
            type="button"
            onClick={handleExplore}
            className="inline-flex items-center gap-2 px-6 py-2.5 rounded-full bg-crimson-700 hover:bg-crimson-800 text-white text-xs font-bold transition-all duration-200 shadow-xl hover:shadow-crimson-900/50 hover:scale-105 active:scale-95 border border-crimson-500/40 cursor-pointer"
          >
            <Compass className="w-4 h-4 text-white" />
            <span>Khám phá ngay</span>
            <ArrowRight className="w-3.5 h-3.5 text-white/80" />
          </button>
        </div>
      </div>
    </div>
  );
}
