import React, { useState, useRef } from 'react';
import { Search, Sparkles, Mic, Camera, X } from 'lucide-react';
import { useSpeechRecognition } from '../../hooks/useSpeechRecognition';
import { useToast } from '../../context/ToastContext';
import { searchApi } from '../../api';

export default function MultiModalSearchBar({
  onSearch,
  searchMode,
  setSearchMode,
  searchQuery,
  setSearchQuery,
  onImageMatched,
}) {
  const { showToast } = useToast();
  const fileInputRef = useRef(null);
  const searchInputRef = useRef(null);
  const [isUploadingImage, setIsUploadingImage] = useState(false);

  const isAiActive = searchMode === 'SEMANTIC';

  const toggleAiMode = () => {
    const nextMode = isAiActive ? 'KEYWORD' : 'SEMANTIC';
    setSearchMode(nextMode);
  };

  const { isListening, hasSupport, toggleListening } = useSpeechRecognition({
    onResult: (transcript) => {
      setSearchQuery(transcript);
      showToast('Đã nhận diện giọng nói. Vui lòng kiểm tra câu truy vấn và nhấn Enter hoặc kính lúp để tìm (BR08).', 'info');
      setTimeout(() => searchInputRef.current?.focus(), 50);
    },
    onError: (friendlyMsg) => {
      showToast(friendlyMsg, 'error');
    },
  });

  const handleSubmit = (e) => {
    if (e) e.preventDefault();
    onSearch(searchQuery, searchMode);
  };

  const handleVoiceClick = () => {
    if (!hasSupport) {
      showToast('Trình duyệt chưa hỗ trợ Web Speech API. Vui lòng dùng Chrome hoặc Edge!', 'error');
      return;
    }
    toggleListening();
  };

  const handleImageFileChange = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploadingImage(true);
    try {
      const res = await searchApi.searchImage(file);
      if (res.results && res.results.length > 0) {
        const book = res.results[0];
        if (onImageMatched) {
          onImageMatched(book);
        }
      } else {
        showToast('Không tìm thấy ảnh bìa nào trong kho khớp với ảnh tải lên.', 'error');
      }
    } catch (err) {
      showToast('Lỗi nhận diện ảnh bìa: ' + err.message, 'error');
    } finally {
      setIsUploadingImage(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  return (
    <div className="relative flex-1 max-w-2xl">
      <form
        onSubmit={handleSubmit}
        className={`flex items-center h-11 rounded-full border transition-all duration-300 shadow-sm overflow-hidden relative pl-0 pr-1.5 ${
          isAiActive
            ? 'bg-amber-50/30 border-amber-400 ring-2 ring-amber-100'
            : 'bg-stone-100/90 border-stone-300 focus-within:border-crimson-700 focus-within:ring-2 focus-within:ring-crimson-100'
        }`}
      >
        {/* Full-height Left Segment AI Toggle Button */}
        <button
          type="button"
          onClick={toggleAiMode}
          title={isAiActive ? 'Chế độ AI đang bật (nhấn để tắt)' : 'Nhấn để bật tìm kiếm Cốt truyện AI'}
          className={`h-full flex items-center gap-1.5 px-4 text-xs font-bold transition-all duration-300 shrink-0 select-none cursor-pointer border-r ${
            isAiActive
              ? 'bg-gradient-to-r from-amber-500 via-rose-500 to-crimson-700 text-white border-amber-300/80 shadow-inner'
              : 'bg-white hover:bg-stone-50 text-stone-600 border-stone-200'
          }`}
        >
          <Sparkles
            className={`w-3.5 h-3.5 shrink-0 transition-transform ${
              isAiActive ? 'text-amber-200 fill-amber-200 animate-pulse' : 'text-stone-400'
            }`}
          />
          <span className="tracking-wide">AI</span>
          <span className="relative flex h-2 w-2 shrink-0 ml-0.5">
            {isAiActive && (
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-300 opacity-75"></span>
            )}
            <span
              className={`relative inline-flex rounded-full h-2 w-2 transition-colors ${
                isAiActive ? 'bg-emerald-400' : 'bg-stone-300'
              }`}
            ></span>
          </span>
        </button>

        {/* Input with stable layout */}
        <input
          ref={searchInputRef}
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder={
            isListening
              ? '🎙️ Đang nghe bạn nói... (Hãy nói tên tác phẩm, tác giả)'
              : isAiActive
              ? '✨ AI đang bật: Hãy miêu tả nội dung, cốt truyện, nhân vật bạn nhớ...'
              : 'Tìm kiếm theo tựa sách, tác giả, nhà xuất bản...'
          }
          className="flex-1 h-full bg-transparent px-3 text-xs text-stone-800 placeholder-stone-400 focus:outline-none"
        />

        {/* Clear query */}
        {searchQuery && (
          <button
            type="button"
            onClick={() => {
              setSearchQuery('');
              onSearch('', searchMode);
            }}
            className="p-1 text-stone-400 hover:text-stone-600 transition shrink-0"
          >
            <X className="w-4 h-4" />
          </button>
        )}

        {/* Voice Button */}
        <button
          type="button"
          onClick={handleVoiceClick}
          title={isListening ? 'Đang lắng nghe... (Nhấn để dừng)' : 'Tìm kiếm bằng giọng nói tiếng Việt'}
          className={`p-2 transition shrink-0 ${
            isListening
              ? 'voice-recording text-crimson-700 bg-crimson-50 rounded-full'
              : 'text-stone-500 hover:text-crimson-700'
          }`}
        >
          <Mic className={`w-4 h-4 ${isListening ? 'animate-bounce text-crimson-700' : ''}`} />
        </button>

        {/* Camera / Image Button */}
        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          disabled={isUploadingImage}
          title="Tải ảnh bìa để tìm kiếm bằng thị giác dHash"
          className="p-2 text-stone-500 hover:text-crimson-700 transition shrink-0"
        >
          <Camera className={`w-4 h-4 ${isUploadingImage ? 'animate-spin' : ''}`} />
        </button>
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleImageFileChange}
          className="hidden"
        />

        {/* Submit Search Button */}
        <button
          type="submit"
          className="p-2.5 bg-crimson-700 hover:bg-crimson-800 text-white rounded-full transition shadow shrink-0"
        >
          <Search className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
}
