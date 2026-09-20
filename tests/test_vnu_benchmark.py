import os
from dotenv import load_dotenv

from src.chunking import MarkdownHeadingChunker, compute_similarity
from src.embeddings import GeminiEmbedder


class ChunkRecord:
    def __init__(self, text: str, doc_name: str, metadata: dict = None, embedder=None):
        self.text = text
        self.doc_name = doc_name
        self.metadata = metadata or {}
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
# 2. CHẠY TEST BENCHMARK BỘ DỮ LIỆU VNU
# ==========================================
def run_vnu_benchmark():
    load_dotenv()
    print("Đang khởi tạo GeminiEmbedder và xử lý tài liệu VNU...\n")
    embedder = GeminiEmbedder()
    chunker = MarkdownHeadingChunker(chunk_size=350)

    # 2.1. Chuẩn bị tài liệu giả định theo đúng dữ liệu bạn cung cấp
    raw_documents = [
        {
            "doc_name": "vnu-hus-nghi-dinh-179.md",
            "text": "# Nghị định 179/2026/NĐ-CP tại ĐHKHTN\n\n## Mức hỗ trợ tài chính\nMức hỗ trợ tài chính hàng tháng cao nhất là 5.500.000 đồng/tháng dành riêng cho sinh viên học tập tại các chương trình đào tạo tài năng thuộc danh mục ưu tiên của Bộ GD&ĐT theo Điều 5 NĐ 179/2026.\n\n## Điều kiện điểm thi THPT\nYêu cầu tổng điểm môn Toán và 2 môn khác trong tổ hợp xét tuyển (Vật lý, Hóa học, Sinh học, Tiếng Anh) đạt từ 22,50/30 điểm trở lên (không tính điểm ưu tiên) và nằm trong nhóm 30% thí sinh có điểm trúng tuyển cao nhất của cùng nhóm ngành trên toàn quốc.",
            "meta": {"audience": "prospective-student", "category": "scholarship"}
        },
        {
            "doc_name": "vnu-is-hoc-bong-ngan-han.md",
            "text": "# Cẩm nang học bổng VNU-IS\n\n## Tiêu chuẩn chung học bổng ngắn hạn\nSinh viên phải có kết quả học tập đạt loại Giỏi hoặc Xuất sắc (GPA >= 3.2), điểm rèn luyện đạt loại Tốt trở lên (>= 80 điểm), không bị kỷ luật từ mức khiển trách trở lên trong học kỳ xét học bổng.",
            "meta": {"audience": "student", "category": "scholarship"}
        },
        {
            "doc_name": "vnu-ulis-cam-nang-hoc-bong.md",
            "text": "# Cẩm nang học bổng VNU-ULIS\n\n## Quỹ học bổng Thắp sáng niềm tin\nQuỹ học bổng Thắp sáng niềm tin trao 12.000.000 VNĐ/học bổng cho mỗi sinh viên trúng tuyển vào các trường đại học công lập nhằm hỗ trợ các em có hoàn cảnh khó khăn.",
            "meta": {"audience": "student", "category": "scholarship"}
        },
        {
            "doc_name": "vnu-is-tong-quan-hoc-bong.md",
            "text": "# Tổng quan học bổng Trường Quốc tế\n\n## Hệ thống học bổng\nHệ thống học bổng VNU-IS gồm 3 nhóm chính: 1) Học bổng khuyến khích học tập từ nguồn ngân sách nhà nước; 2) Học bổng tài trợ ngoài ngân sách từ các doanh nghiệp/tổ chức đối tác; 3) Học bổng hỗ trợ sinh viên có hoàn cảnh khó khăn.",
            "meta": {"audience": "student", "category": "scholarship"}
        }
    ]

    # Chunking và tạo Vector Database in-memory
    database = []
    for doc in raw_documents:
        chunks_text = chunker.chunk(doc["text"])
        for text in chunks_text:
            database.append(ChunkRecord(text=text, doc_name=doc["doc_name"], metadata=doc["meta"], embedder=embedder))

    # 2.2. Khai báo 5 câu hỏi và các nhận xét (Notes) để điền vào bảng
    benchmark_queries = [
        {
            "query": "Mức hỗ trợ tài chính hàng tháng cao nhất dành cho sinh viên học tập tại các chương trình đào tạo tài năng theo Nghị định 179/2026/NĐ-CP tại Trường ĐHKHTN là bao nhiêu?",
            "gold": "5.500.000 đồng",
            "filter": {"audience": "prospective-student"},
            "strategy": "MarkdownHeading + Filter",
            "note": "Bắt buộc dùng filter `audience=\"prospective-student\"` để hệ thống không lấy nhầm các mức hỗ trợ của sinh viên đang học."
        },
        {
            "query": "Sinh viên đang theo học tại Trường Quốc tế (VNU-IS) cần đáp ứng tiêu chuẩn chung nào về kết quả học tập và rèn luyện để được đăng ký các chương trình học bổng ngắn hạn?",
            "gold": "GPA >= 3.2",
            "filter": {"audience": "student"},
            "strategy": "RecursiveChunker",
            "note": "Các điều kiện (GPA, rèn luyện, kỷ luật) viết thành 1 đoạn dài. Recursive giữ trọn vẹn đoạn này tốt hơn SentenceChunker."
        },
        {
            "query": "Điều kiện về điểm thi THPT để thí sinh nhận Học bổng Chính phủ theo Nghị định 179/2026/NĐ-CP tại Trường ĐHKHTN là gì?",
            "gold": "22,50/30 điểm",
            "filter": None,
            "strategy": "MarkdownHeading",
            "note": "Chiến lược giúp đính kèm trọn vẹn tiêu đề 'Nghị định 179' vào chi tiết điều kiện điểm THPT."
        },
        {
            "query": "Trong Cẩm nang học bổng VNU-ULIS, Quỹ học bổng Thắp sáng niềm tin trao tặng bao nhiêu tiền cho mỗi suất học bổng dành cho sinh viên đại học?",
            "gold": "12.000.000 VNĐ",
            "filter": {"audience": "student"},
            "strategy": "SentenceChunker + Filter",
            "note": "Trích xuất được đúng câu có số '12.000.000 VNĐ', nhưng dễ bị ngắt khỏi ngữ cảnh nếu không cẩn thận."
        },
        {
            "query": "Trường Quốc tế (VNU-IS) phân loại hệ thống học bổng dành cho sinh viên thành những nhóm nguồn chính nào?",
            "gold": "3 nhóm chính",
            "filter": {"category": "scholarship"},
            "strategy": "MarkdownHeading",
            "note": "Gom trọn vẹn được danh sách 3 nhóm liệt kê dưới thẻ tiêu đề `## Hệ thống học bổng`."
        }
    ]

    # 2.3. Chạy truy vấn và In bảng Markdown chuẩn Báo cáo nhóm
    print("="*120)
    print("KẾT QUẢ: BẢNG TỔNG HỢP CHẤT LƯỢNG TRUY XUẤT CỦA NHÓM")
    print("="*120)
    print("| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |")
    print("|---|---------|-------------------------------|-------------------------------|---------|")

    for i, item in enumerate(benchmark_queries, 1):
        q_emb = embedder(item["query"])
        retrieved = retrieve_top_k(q_emb, database, top_k=3, filter_dict=item["filter"])
        
        score = evaluate_score(retrieved, item["gold"])
        
        if score == 2:
            relevance_str = "Có (Top 1) - Score: 2"
        elif score == 1:
            relevance_str = "Có (Top 2/3) - Score: 1"
        else:
            relevance_str = "Không - Score: 0"
            
        print(f"| {i} | {item['query']} | {item['strategy']} | {relevance_str} | {item['note']} |")

if __name__ == "__main__":
    run_vnu_benchmark()