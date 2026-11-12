"""
Application Service: ChatbotService
Điều phối Trợ lý ảo AI Bookie (RAG - Retrieval-Augmented Generation).
Tuân thủ nghiêm ngặt Quy tắc Grounding BR08 và kịch bản tư vấn sách trong Báo cáo Thiết kế.
"""
from typing import List, Dict, Any, Optional
from ...infrastructure.repositories.book_repository import BookRepository
from ...infrastructure.adapters.cloudflare_llm import CloudflareLLMAdapter
from .search_service import SearchService
from ..dtos.models import ChatMessageResponse, BookCardDTO

SYSTEM_PROMPT_TEMPLATE = """Bạn là Bookie, trợ lý ảo AI thông minh, nhiệt huyết và là chuyên gia tư vấn văn hóa đọc của Hiệu sách Trực tuyến BookHaven.

THÔNG TIN DANH TÍNH & CÔNG NGHỆ CỦA BẠN:
- Tên: Bookie (Trợ lý ảo AI tư vấn độc quyền của Hiệu sách BookHaven).
- Nền tảng AI: Mô hình ngôn ngữ lớn Meta LLaMA 3.1 8B Instruct, vận hành serverless qua hạ tầng Cloudflare Workers AI.
- Hệ thống RAG (Retrieval-Augmented Generation): Kết hợp mô hình embedding vector đa ngữ all-MiniLM-L6-v2 (384 chiều) để tìm kiếm ngữ nghĩa theo nhu cầu và tâm trạng, cùng thuật toán dHash nhận diện bìa sách.
- Triết lý phục vụ: Thân thiện, tinh tế, am hiểu sách, tôn trọng cảm xúc độc giả và truyền cảm hứng đọc sách sâu sắc.

DỊCH VỤ & CHÍNH SÁCH ĐỘC QUYỀN CỦA BOOKHAVEN:
1. Vận chuyển hỏa tốc bằng Drone (Máy bay không người lái):
   - Áp dụng cho các đơn hàng có tổng khối lượng dưới 2.000g (2kg) trong khu vực nội thành.
   - Thời gian nhận hàng siêu tốc: Chỉ từ 30 - 45 phút.
   - Cước phí: 60.000 đ cố định. Khách hàng có thể theo dõi radar bay trực tiếp trên bản đồ.
2. Vận chuyển tiêu chuẩn: Toàn quốc từ 2 - 4 ngày, cước phí từ 25.000 đ.
3. Phương thức thanh toán:
   - VietQR tự động qua ngân hàng MBBank: Mã QR tạo tự động theo từng đơn, xác thực tức thì qua Background Worker.
   - COD: Thanh toán tiền mặt khi nhận hàng.
4. Đa dạng ấn bản: Mỗi đầu sách có thể có bản Bìa Mềm (Paperback) hoặc Bìa Cứng (Hardcover) với giá bán minh bạch.
5. Danh mục sách chính: Công nghệ Thông tin & Lập trình, Kinh tế & Tài chính, Văn học & Tiểu thuyết, Kỹ năng sống & Phát triển bản thân.

DỮ LIỆU SÁCH CÓ THẬT TRONG KHO BOOKHAVEN (GROUNDING BR08):
{context_books}

NGUYÊN TẮC PHẢN HỒI:
1. KHI NGƯỜI DÙNG HỎI VỀ BẠN (DANH TÍNH, MÔ HÌNH AI, CÔNG NGHỆ, XUẤT XỨ):
   - Giới thiệu bạn là Bookie - trợ lý ảo của BookHaven, giải thích rõ bạn chạy trên mô hình Meta LLaMA 3.1 8B kết hợp RAG và vector embeddings, sẵn sàng hỗ trợ độc giả chọn sách.
2. KHI NGƯỜI DÙNG CHÀO HỎI, CẢM ƠN HOẶC TRÒ CHUYỆN XÃ GIAO:
   - Đáp lại lịch thiệp, ấm áp, mời độc giả chia sẻ gu đọc sách hoặc chủ đề họ quan tâm.
3. KHI NGƯỜI DÙNG HỎI VỀ CHÍNH SÁCH, GIAO DRONE, THANH TOÁN VIETQR:
   - Giải đáp chính xác các thông số và quy trình theo thông tin BookHaven ở trên.
4. KHI NGƯỜI DÙNG HỎI MUA, TƯ VẤN HOẶC TÌM KIẾM SÁCH:
   - Dựa vào danh sách sách có trong kho được cung cấp ở trên.
   - Chỉ giới thiệu sách có thật trong danh sách kho, tuyệt đối không bịa đặt tên sách/giá không có trong danh sách (Grounding BR08).
   - Viết lời bình phẩm, phân tích ngắn gọn nhưng sâu sắc lý do vì sao cuốn sách đó phù hợp với câu hỏi của độc giả.
   - Nếu trong kho không có cuốn sách nào khớp, hãy lịch sự thông báo và khéo léo gợi ý các danh mục sách tương đương đang có tại BookHaven.
   - Khuyến khích người đọc bấm vào nút '+ Giỏ' ở thẻ sách bên dưới để mua nhanh.
5. VĂN PHONG:
   - Tiếng Việt tự nhiên, lịch sự, truyền cảm hứng, độ dài vừa vặn (khoảng 2-4 đoạn ngắn hoặc 3-5 câu), không dài dòng thừa thãi.
"""

class ChatbotService:
    def __init__(
        self,
        book_repo: BookRepository,
        search_service: SearchService,
        llm_adapter: Optional[CloudflareLLMAdapter] = None
    ):
        self.book_repo = book_repo
        self.search_service = search_service
        self.llm_adapter = llm_adapter or CloudflareLLMAdapter()

    @staticmethod
    def classify_intent(message: str) -> str:
        """
        Phân loại ý định người dùng thành:
        - 'identity_tech': Hỏi về danh tính bot, mô hình AI, kiến trúc, công nghệ
        - 'greeting_chitchat': Chào hỏi, cảm ơn, khen ngợi, xã giao
        - 'policy_service': Hỏi về giao hàng drone, phí ship, thanh toán VietQR, đổi trả
        - 'book_search': Tìm kiếm, hỏi mua, xin gợi ý hoặc hỏi về sách
        """
        msg = message.lower().strip()

        # Từ khóa định danh việc tìm/hỏi về sách rõ rệt
        book_explicit_keywords = [
            "sách", "cuốn", "tác phẩm", "tác giả", "tiểu thuyết", "truyện",
            "ấn bản", "bìa cứng", "bìa mềm", "đọc sách", "tìm sách", "mua sách",
            "gợi ý sách", "tư vấn sách", "giá bao nhiêu", "còn hàng không"
        ]
        has_book_intent = any(kw in msg for kw in book_explicit_keywords)

        # 1. Nhóm hỏi danh tính kỹ thuật / mô hình AI
        tech_keywords = [
            "mô hình nào", "model nào", "mô hình gì", "bạn là ai", "bạn tên gì",
            "ai tạo ra", "nguồn gốc", "llama", "chatgpt", "gpt", "dùng ai gì",
            "công nghệ gì", "kiến trúc", "rag là gì", "dhash", "ai của tôi",
            "thuật toán gì", "mô hình ngôn ngữ"
        ]
        if any(kw in msg for kw in tech_keywords) and not ("sách về" in msg or "cuốn sách" in msg):
            return "identity_tech"

        # 2. Nhóm chào hỏi / cảm ơn / xã giao
        greetings = [
            "xin chào", "chào bạn", "chào em", "chào bot", "chào bookie", "chào", "hello",
            "hi bookie", "cảm ơn", "thanks", "thank you", "tuyệt vời", "pro quá",
            "tạm biệt", "bye", "goodbye", "bạn khỏe không"
        ]
        is_greeting = any(msg == g or msg.startswith(g + " ") or msg.endswith(" " + g) for g in greetings)
        if is_greeting and not has_book_intent:
            return "greeting_chitchat"

        # 3. Nhóm chính sách cửa hàng & dịch vụ độc quyền
        policy_keywords = [
            "drone", "máy bay", "vận chuyển", "phí ship", "giao hàng bao lâu",
            "thanh toán", "vietqr", "chuyển khoản", "ngân hàng", "mbbank",
            "cod", "đổi trả", "hoàn tiền", "cửa hàng ở đâu", "địa chỉ", "bảo hành"
        ]
        if any(kw in msg for kw in policy_keywords) and not has_book_intent:
            return "policy_service"

        return "book_search"

    def process_message(self, user_message: str) -> ChatMessageResponse:
        """
        Quy trình xử lý thông minh & RAG:
        1. Phân loại ý định người dùng (Kỹ thuật/Danh tính, Chào hỏi, Chính sách, hay Tìm sách).
        2. Nếu là tìm sách: Retrieval (Semantic/Keyword) -> Filter -> Augment -> Generation -> Grounding.
        3. Nếu là giao tiếp/chính sách/danh tính: Phản hồi chính xác bối cảnh mà không đính kèm thẻ sách rác.
        """
        clean_msg = user_message.strip()
        if not clean_msg:
            return ChatMessageResponse(
                reply="Dạ Bookie có thể giúp gì cho bạn hôm nay ạ? Bạn đang muốn tìm sách về chủ đề gì?",
                suggested_books=[]
            )

        intent = self.classify_intent(clean_msg)

        # XỬ LÝ THEO Ý ĐỊNH
        if intent == "identity_tech":
            context_str = (
                "Người dùng đang hỏi về danh tính, nguồn gốc, công nghệ hoặc mô hình AI của bạn. "
                "Hãy tự tin giới thiệu bạn là Bookie, vận hành trên mô hình Meta LLaMA 3.1 8B Instruct "
                "qua Cloudflare Workers AI kết hợp kỹ thuật RAG với all-MiniLM-L6-v2. Trả lời thân thiện, "
                "thông minh, không đính kèm thẻ sách khi người dùng không hỏi mua sách."
            )
            system_prompt = SYSTEM_PROMPT_TEMPLATE.format(context_books=context_str)
            llm_reply = self.llm_adapter.generate_chat_response(system_prompt, clean_msg)
            return ChatMessageResponse(reply=llm_reply, suggested_books=[])

        elif intent == "greeting_chitchat":
            context_str = (
                "Người dùng đang chào hỏi, cảm ơn hoặc giao tiếp xã giao. "
                "Hãy chào đón nhiệt tình, phong thái nhã nhặn, giới thiệu các danh mục sách thế mạnh "
                "của BookHaven và sẵn sàng hỗ trợ độc giả chọn sách."
            )
            system_prompt = SYSTEM_PROMPT_TEMPLATE.format(context_books=context_str)
            llm_reply = self.llm_adapter.generate_chat_response(system_prompt, clean_msg)
            return ChatMessageResponse(reply=llm_reply, suggested_books=[])

        elif intent == "policy_service":
            context_str = (
                "Người dùng đang hỏi về dịch vụ hoặc chính sách của BookHaven (như giao hàng Drone hỏa tốc "
                "dưới 2kg trong 30-45 phút phí 60.000đ, giao tiêu chuẩn 2-4 ngày, quét VietQR MBBank tự động, COD). "
                "Hãy giải đáp chi tiết, chính xác các chính sách này mà không đính kèm thẻ sách ngẫu nhiên."
            )
            system_prompt = SYSTEM_PROMPT_TEMPLATE.format(context_books=context_str)
            llm_reply = self.llm_adapter.generate_chat_response(system_prompt, clean_msg)
            return ChatMessageResponse(reply=llm_reply, suggested_books=[])

        # ----------------------------------------------------
        # intent == "book_search": RAG đầy đủ với Quy tắc Grounding BR08
        # ----------------------------------------------------
        # 1. Retrieval: Sử dụng hoàn toàn Semantic Search AI (all-MiniLM-L6-v2)
        search_res = self.search_service.search_semantic(clean_msg, limit=3, min_threshold=0.35)

        # 2. Filter & Trích xuất thông tin sách
        suggested_books: List[BookCardDTO] = []
        context_lines: List[str] = []

        clean_lower = clean_msg.lower()
        query_words = [w for w in clean_lower.replace(",", " ").replace(".", " ").split() if len(w) > 2]

        for item in search_res.results:
            # Tiêu chí liên quan thực sự:
            item_text = f"{item.title} {item.author_name} {item.description}".lower()
            has_word_match = any(w in item_text for w in query_words)
            is_relevant = item.similarity_score >= 0.40 or has_word_match

            # Ưu tiên kết quả hàng đầu nếu có điểm tương đối
            if not is_relevant and len(search_res.results) > 0 and search_res.results[0].book_id == item.book_id:
                if item.similarity_score >= 0.35:
                    is_relevant = True

            if not is_relevant:
                continue

            editions = self.book_repo.get_editions_by_book_id(item.book_id)
            for ed in editions:
                avail = ed.available_stock()
                if avail > 0:
                    suggested_books.append(BookCardDTO(
                        book_id=item.book_id,
                        title=item.title,
                        author_name=item.author_name,
                        unit_price=ed.unit_price,
                        binding_type=ed.binding_type,
                        edition_id=ed.edition_id,
                        cover_image=item.cover_image,
                        available_stock=avail
                    ))
                    context_lines.append(
                        f"- Tên: '{item.title}' | Tác giả: {item.author_name} | Bản: {ed.binding_type} | "
                        f"Giá: {ed.unit_price:,} đ | Còn: {avail} cuốn | Tóm tắt: {item.description[:120]}"
                    )
                    break  # Chỉ lấy 1 ấn bản tiêu biểu cho mỗi đầu sách

        # 3. Augment: Xây dựng System Prompt
        if context_lines:
            context_str = "\n".join(context_lines)
        else:
            context_str = (
                "Hiện tại kho sách của BookHaven chưa có tựa sách nào khớp hoàn toàn với yêu cầu này của khách. "
                "Hãy lịch sự xin lỗi và gợi ý độc giả khám phá các danh mục sách có sẵn: Công nghệ Thông tin, "
                "Kinh tế & Tài chính, Văn học hoặc Kỹ năng sống."
            )

        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(context_books=context_str)

        # 4. Generation
        llm_reply = self.llm_adapter.generate_chat_response(system_prompt, clean_msg)

        # 5. Đóng gói kết quả
        return ChatMessageResponse(
            reply=llm_reply,
            suggested_books=suggested_books
        )
