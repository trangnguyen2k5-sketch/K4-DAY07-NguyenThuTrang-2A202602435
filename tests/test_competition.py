import os
from dotenv import load_dotenv

from src.chunking import MarkdownHeadingChunker, compute_similarity
from src.embeddings import GeminiEmbedder

# ==========================================
# 1. CẤU TRÚC LƯU TRỮ VÀ TÌM KIẾM
# ==========================================
class ChunkRecord:
    def __init__(self, text: str, metadata: dict = None, embedder=None):
        self.text = text
        self.metadata = metadata or {}
        # Tự động chuyển text thành vector
        self.embedding = embedder(text) if embedder else []

def retrieve_top_k(query_emb: list[float], chunks: list[ChunkRecord], top_k: int = 3, filter_dict: dict = None):
    """Tìm kiếm Top K chunks gần nhất, có hỗ trợ metadata filter"""
    valid_chunks = chunks
    if filter_dict:
        valid_chunks = [
            c for c in chunks 
            if all(c.metadata.get(k) == v for k, v in filter_dict.items())
        ]
        
    scored = []
    for c in valid_chunks:
        score = compute_similarity(query_emb, c.embedding)
        scored.append((c, score))
        
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]

def evaluate_score(retrieved_tuples, gold_string: str) -> int:
    """Chấm điểm 2 (Top 1), 1 (Top 2-3), 0 (Không có)"""
    for i, (chunk, score) in enumerate(retrieved_tuples):
        if gold_string.lower() in chunk.text.lower():
            if i == 0: return 2
            elif i in [1, 2]: return 1
    return 0

# ==========================================
# 2. CHẠY TEST 5 CÂU HỎI BENCHMARK
# ==========================================
def run_competition_benchmark():
    load_dotenv()
    print("Đang khởi tạo GeminiEmbedder và xử lý tài liệu...\n")
    embedder = GeminiEmbedder()
    chunker = MarkdownHeadingChunker(chunk_size=300)

    # 2.1. Chuẩn bị tài liệu giả định (Raw Texts + Metadata)
    raw_documents = [
        {
            "text": "# Học bổng Khuyến khích học tập\n\n## Điều kiện xét duyệt (Khuyến khích học tập)\nSinh viên năm nhất cần đạt điểm trung bình tích lũy (GPA) từ 3.0/4.0 trở lên để nhận học bổng này.",
            "meta": {"đối_tượng": "năm nhất"}
        },
        {
            "text": "# Học bổng Xuất sắc Toàn diện\n\n## Mức cấp phát (Học bổng Xuất sắc Toàn diện)\nHọc bổng bao gồm 100% học phí của năm học tiếp theo. Ngoài ra, sinh viên sẽ nhận được khoản hỗ trợ sinh hoạt phí trị giá 2.000.000 VNĐ/tháng, kéo dài trong 10 tháng.",
            "meta": {"đối_tượng": "toàn trường"}
        },
        {
            "text": "# Học bổng Vượt Khó\n\n## Điều kiện xét duyệt (Học bổng Vượt Khó)\nSinh viên thuộc diện hộ nghèo hoặc cận nghèo. Đồng thời, sinh viên phải không bị kỷ luật dưới mọi hình thức trong năm học.",
            "meta": {"đối_tượng": "toàn trường"}
        },
        {
            "text": "# Học bổng Doanh nghiệp tài trợ\n\n## Yêu cầu (Học bổng Doanh nghiệp)\nỨng viên phải có kết quả học tập xếp loại Giỏi. Điểm rèn luyện từ 80 điểm trở lên.",
            "meta": {"đối_tượng": "toàn trường"}
        },
        {
            "text": "# Học bổng Tài năng\n\n## Hồ sơ đăng ký (Học bổng Tài năng)\nĐể nộp hồ sơ, sinh viên cần chuẩn bị: Đơn xin học bổng, Bảng điểm có mộc đỏ xác nhận của phòng đào tạo, và Bản sao CCCD.",
            "meta": {"đối_tượng": "toàn trường"}
        }
    ]

    # Chunking và tạo Vector Database in-memory
    database = []
    for doc in raw_documents:
        chunks_text = chunker.chunk(doc["text"])
        for text in chunks_text:
            database.append(ChunkRecord(text=text, metadata=doc["meta"], embedder=embedder))

    # 2.2. Khai báo 5 câu hỏi, chuỗi kỳ vọng (Gold) và Agent mock answer
    benchmark_queries = [
        {
            "query": "Sinh viên năm nhất ngành CNTT cần đạt GPA bao nhiêu để nhận học bổng Khuyến khích?",
            "gold": "3.0/4.0",
            "filter": {"đối_tượng": "năm nhất"},
            "agent_mock": "Sinh viên năm nhất cần đạt GPA tối thiểu 3.0/4.0 để nhận học bổng này."
        },
        {
            "query": "Mức hỗ trợ của Học bổng Xuất sắc Toàn diện bao gồm những khoản nào?",
            "gold": "2.000.000 VNĐ",
            "filter": None,
            "agent_mock": "Bao gồm 100% học phí năm tiếp theo và 2.000.000 VNĐ/tháng (kéo dài 10 tháng)."
        },
        {
            "query": "Sinh viên bị kỷ luật cảnh cáo có được xét học bổng Vượt Khó không?",
            "gold": "không bị kỷ luật",
            "filter": None,
            "agent_mock": "Không, điều kiện bắt buộc là sinh viên không bị kỷ luật dưới mọi hình thức."
        },
        {
            "query": "Học bổng Doanh nghiệp tài trợ yêu cầu điểm rèn luyện tối thiểu là bao nhiêu?",
            "gold": "80 điểm",
            "filter": None,
            "agent_mock": "Điểm rèn luyện yêu cầu tối thiểu là từ 80 điểm trở lên."
        },
        {
            "query": "Cần chuẩn bị những giấy tờ gì để nộp hồ sơ Học bổng Tài năng?",
            "gold": "Bảng điểm có mộc đỏ",
            "filter": None,
            "agent_mock": "Cần chuẩn bị: Đơn xin học bổng, Bảng điểm có mộc đỏ của trường, và Bản sao CCCD."
        }
    ]

    # 2.3. Chạy truy vấn và In bảng Markdown
    print("="*100)
    print("COPY BẢNG DƯỚI ĐÂY DÁN VÀO REPORT_CANHAN.md:")
    print("="*100)
    print("| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |")
    print("|---|---|---|:---:|:---:|---|")

    total_relevant = 0

    for i, item in enumerate(benchmark_queries, 1):
        q_emb = embedder(item["query"])
        retrieved = retrieve_top_k(q_emb, database, top_k=3, filter_dict=item["filter"])
        
        score = evaluate_score(retrieved, item["gold"])
        
        # Format Top 1 preview
        top1_text = retrieved[0][0].text.replace('\n', ' ') if retrieved else "Không tìm thấy"
        if len(top1_text) > 80:
            top1_text = top1_text[:80] + "..."
            
        is_relevant = "Có" if score > 0 else "Không"
        if score > 0: total_relevant += 1
            
        print(f"| {i} | {item['query']} | `{top1_text}` | **{score}** | {is_relevant} | {item['agent_mock']} |")

    print("\n**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** **{}** / 5".format(total_relevant))

if __name__ == "__main__":
    run_competition_benchmark()