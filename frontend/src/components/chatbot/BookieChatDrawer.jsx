import React, { useState, useRef, useEffect } from 'react';
import { X, Send, Sparkles, ShoppingCart, Bot } from 'lucide-react';
import { chatbotApi, formatVND } from '../../api';
import { useCart } from '../../context/CartContext';

export default function BookieChatDrawer({ isOpen, onClose, onSelectBook }) {
  const { addToCart } = useCart();
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      sender: 'ai',
      text: 'Xin chào bạn! Tôi là Trợ lý AI BookHaven ✨ — Tôi nắm rõ toàn bộ kho sách thực tế và quy cách ấn bản hiện có. Bạn đang tìm kiếm tác phẩm hay chủ đề nào?',
      books: [],
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isSending, setIsSending] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, isOpen]);

  const handleSend = async (messageText) => {
    const textToSend = (messageText || inputValue).trim();
    if (!textToSend || isSending) return;

    const userMsg = {
      id: 'msg_' + Date.now(),
      sender: 'user',
      text: textToSend,
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputValue('');
    setIsSending(true);

    try {
      const res = await chatbotApi.sendMessage(textToSend);
      const aiMsg = {
        id: 'msg_ai_' + Date.now(),
        sender: 'ai',
        text: res.reply || 'Dạ tôi đã tìm thấy một số tác phẩm phù hợp trong kho:',
        books: res.suggested_books || res.recommended_books || [],
      };
      setMessages((prev) => [...prev, aiMsg]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: 'msg_err_' + Date.now(),
          sender: 'ai',
          text: 'Xin lỗi bạn, kết nối trợ lý ảo gặp gián đoạn: ' + err.message,
        },
      ]);
    } finally {
      setIsSending(false);
    }
  };

  const handleQuickAdd = async (editionId) => {
    try {
      await addToCart(editionId, 1);
    } catch {
      // CartContext đã hiển thị thông báo lỗi
    }
  };

  const handleOpenBook = (bookId) => {
    if (!bookId || !onSelectBook) return;
    onClose();
    onSelectBook(bookId);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-stone-950/40 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      ></div>

      <div className="fixed inset-y-0 right-0 max-w-full flex pl-10">
        <div className="w-screen max-w-md bg-white shadow-2xl flex flex-col">
          {/* Header */}
          <div className="p-4 bg-stone-900 text-white flex items-center justify-between shadow">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-full bg-crimson-700 flex items-center justify-center text-white shadow-inner">
                <Bot className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className="font-serif-title font-bold text-sm text-white flex items-center gap-1.5">
                  <span>Trợ lý AI BookHaven</span>
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                </h3>
                <p className="text-[10px] text-stone-400">
                  Tư vấn kho sách thông minh theo chuẩn RAG (BR08)
                </p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-1.5 rounded-full text-stone-400 hover:text-white hover:bg-stone-800 transition"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Messages Flow */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex gap-2.5 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {msg.sender === 'ai' && (
                  <div className="w-7 h-7 rounded-full bg-crimson-700 text-white flex items-center justify-center text-xs shrink-0 mt-1 shadow-sm">
                    <Bot className="w-4 h-4 text-white" />
                  </div>
                )}

                <div
                  className={`max-w-[85%] rounded-2xl p-3.5 text-xs leading-relaxed ${
                    msg.sender === 'user'
                      ? 'bg-crimson-700 text-white rounded-br-none'
                      : 'bg-stone-100 text-stone-800 rounded-bl-none border border-stone-200'
                  }`}
                >
                  <p className="whitespace-pre-line">{msg.text}</p>

                  {/* Embedded Recommended Book Cards */}
                  {msg.books && msg.books.length > 0 && (
                    <div className="mt-3 space-y-2 pt-2 border-t border-stone-200">
                      {msg.books.map((b) => (
                        <div
                          key={b.edition_id || b.book_id}
                          role="button"
                          tabIndex={0}
                          title={`Xem chi tiết "${b.title}"`}
                          onClick={() => handleOpenBook(b.book_id)}
                          onKeyDown={(e) => {
                            if (e.target === e.currentTarget && (e.key === 'Enter' || e.key === ' ')) {
                              e.preventDefault();
                              handleOpenBook(b.book_id);
                            }
                          }}
                          className="p-2.5 rounded-xl bg-white border border-stone-200 hover:border-crimson-300 hover:bg-crimson-50/40 flex items-center justify-between gap-2 shadow-sm cursor-pointer transition group"
                        >
                          <div className="flex-1 min-w-0">
                            <h5 className="font-bold text-stone-900 group-hover:text-crimson-700 truncate transition-colors">
                              {b.title}
                            </h5>
                            <p className="text-[10px] text-stone-500">
                              {b.binding_type === 'PAPERBACK' ? 'Bìa Mềm' : 'Bìa Cứng'} •{' '}
                              <strong className="text-crimson-700">{formatVND(b.unit_price || b.price)}</strong>
                            </p>
                          </div>
                          <button
                            type="button"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleQuickAdd(b.edition_id);
                            }}
                            className="px-2.5 py-1 rounded-lg bg-crimson-700 hover:bg-crimson-800 text-white text-[10px] font-bold flex items-center gap-1 transition shadow-sm shrink-0"
                          >
                            <ShoppingCart className="w-3 h-3" />
                            <span>+ Giỏ</span>
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
            {isSending && (
              <div className="flex gap-2.5 items-center text-xs text-stone-400 italic">
                <span className="w-6 h-6 rounded-full bg-crimson-700 text-white flex items-center justify-center text-xs shadow-sm">
                  <Bot className="w-3.5 h-3.5 text-white" />
                </span>
                <span>Trợ lý AI đang tra cứu dữ liệu kho sách...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Footer */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="p-3 bg-stone-50 border-t border-stone-200 flex items-center gap-2"
          >
            <input
              type="text"
              placeholder="Hỏi về cốt truyện, tác giả, tựa sách..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              className="flex-1 bg-white border border-stone-300 rounded-full px-4 py-2 text-xs text-stone-800 focus:outline-none focus:ring-2 focus:ring-crimson-700/20"
            />
            <button
              type="submit"
              disabled={!inputValue.trim() || isSending}
              className="p-2.5 rounded-full bg-crimson-700 hover:bg-crimson-800 text-white transition shadow disabled:opacity-40"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
