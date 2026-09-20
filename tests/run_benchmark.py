import os
from dotenv import load_dotenv

# Import từ các module bạn đã viết
from src.chunking import SentenceChunker, MarkdownHeadingChunker, compute_similarity
from src.embeddings import GeminiEmbedder

load_dotenv()

class ChunkRecord:
    def __init__(self, text: str, metadata: dict = None, embedder=None):
        self.text = text
        self.metadata = metadata or {}
        # Tự động chuyển text thành vector khi khởi tạo
        self.embedding = embedder(text) if embedder else []

def retrieve_chunks(query_embedding: list[float], chunks: list[ChunkRecord], top_k: int = 3, metadata_filter: dict = None):
    """Hàm tìm kiếm có hỗ trợ metadata filter và dùng compute_similarity của bạn"""
    filtered_chunks = chunks
    if metadata_filter:
        filtered_chunks = [
            c for c in chunks 
            if all(c.metadata.get(k) == v for k, v in metadata_filter.items())
        ]

    scored_chunks = []
    for c in filtered_chunks:
        score = compute_similarity(query_embedding, c.embedding)
        scored_chunks.append((c, score))
        
    scored_chunks.sort(key=lambda x: x[1], reverse=True)
    return scored_chunks[:top_k]

def evaluate_retrieval(retrieved_tuples, gold_string: str) -> int:
    """Chấm điểm 2-1-0 theo yêu cầu Lab"""
    for i, (chunk, score) in enumerate(retrieved_tuples):
        if gold_string.lower() in chunk.text.lower():
            if i == 0: return 2
            elif i in [1, 2]: return 1
    return 0

if __name__ == "__main__":
    print("Đang khởi tạo GeminiEmbedder...")
    embedder = GeminiEmbedder()

    # =================================================================
    # 1. THỬ NGHIỆM A/B: HIỆU QUẢ CỦA METADATA FILTER
    # =================================================================
    print("\n" + "="*60)
    print("1. THỬ NGHIỆM A/B: METADATA FILTER")
    print("="*60)
    
    db_ab = [
        ChunkRecord("Khuyến khích học tập: GPA 3.2 (Năm 2,3,4)", {"doi_tuong": "nam_234"}, embedder),
        ChunkRecord("Tân sinh viên xuất sắc: Tặng laptop", {"doi_tuong": "nam_nhat"}, embedder),
        ChunkRecord("Khuyến khích học tập: GPA 3.0 (Năm nhất)", {"doi_tuong": "nam_nhat"}, embedder),
    ]
    
    query = "Sinh viên năm nhất ngành CNTT cần đạt GPA bao nhiêu để nhận học bổng Khuyến khích học tập?"
    query_emb = embedder(query)
    gold = "GPA 3.0"
    
    print(f"Câu hỏi: {query}\nCần tìm: '{gold}'")
    
    print("\n--- LẦN 1: KHÔNG DÙNG FILTER ---")
    res_no_filter = retrieve_chunks(query_emb, db_ab, top_k=3)
    for i, (res, score) in enumerate(res_no_filter, 1):
        print(f"Top {i} (Score: {score:.3f}): {res.text}")
    print(f">> Điểm: {evaluate_retrieval(res_no_filter, gold)} điểm")

    print("\n--- LẦN 2: CÓ DÙNG FILTER {'doi_tuong': 'nam_nhat'} ---")
    res_with_filter = retrieve_chunks(query_emb, db_ab, top_k=3, metadata_filter={"doi_tuong": "nam_nhat"})
    for i, (res, score) in enumerate(res_with_filter, 1):
        print(f"Top {i} (Score: {score:.3f}): {res.text}")
    print(f">> Điểm: {evaluate_retrieval(res_with_filter, gold)} điểm")

    # =================================================================
    # 2. PHÂN TÍCH LỖI (FAILURE CASE) VỚI SENTENCE CHUNKER
    # =================================================================
    print("\n\n" + "="*60)
    print("2. PHÂN TÍCH LỖI: SENTENCE CHUNKER LÀM ĐỨT GÃY NGỮ CẢNH")
    print("="*60)
    
    # Giả lập văn bản bị SentenceChunker cắt đôi bằng dấu chấm
    db_fail = [
        ChunkRecord("Học bổng bao gồm 100% học phí của năm học tiếp theo.", embedder=embedder),
        ChunkRecord("Ngoài ra, sinh viên nhận được sinh hoạt phí trị giá 2.000.000 VNĐ/tháng.", embedder=embedder),
        ChunkRecord("Sinh viên được ưu tiên xếp chỗ ở trong ký túc xá.", embedder=embedder)
    ]
    
    query_fail = "Mức hỗ trợ của Học bổng Xuất sắc Toàn diện bao gồm những khoản nào?"
    query_fail_emb = embedder(query_fail)
    gold_fail = "2.000.000 VNĐ"
    
    print(f"Câu hỏi: {query_fail}\nCần tìm (Gold): '{gold_fail}'")
    
    res_fail = retrieve_chunks(query_fail_emb, db_fail, top_k=2)
    print("\n--- KẾT QUẢ RETRIEVAL ---")
    for i, (res, score) in enumerate(res_fail, 1):
         print(f"Top {i} (Score: {score:.3f}): {res.text}")
         
    # Ép chấm Top 1 để minh họa lỗi
    final_score = evaluate_retrieval([res_fail[0]], gold_fail) 
    print(f"\n>> Điểm đạt được ở Top 1: {final_score} điểm (Lỗi: Câu trả lời chứa số tiền bị đẩy xuống Top 2)")