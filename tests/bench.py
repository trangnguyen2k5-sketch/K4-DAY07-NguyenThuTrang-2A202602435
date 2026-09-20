import argparse
import yaml
from pathlib import Path

# Đảm bảo đường dẫn import phù hợp với cấu trúc dự án của bạn
from src.store import EmbeddingStore         
from src.models import Document              
from src.chunking import RecursiveChunker, MarkdownHeadingChunker 

def parse_markdown_with_frontmatter(file_path: Path):
    """Đọc file md, tách YAML frontmatter ra khỏi content."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    metadata = {}
    body = content
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            try:
                metadata = yaml.safe_load(parts[1]) or {}
                body = parts[2].strip()
            except yaml.YAMLError as e:
                print(f"Lỗi parse YAML ở file {file_path}: {e}")
                
    return metadata, body

def run_benchmark(chunker_strategy, top_k: int, threshold: float):
    """
    Hàm benchmark linh hoạt, hỗ trợ chunker, top_k và score threshold.
    """
    strategy_name = chunker_strategy.__class__.__name__
    print(f"\n{'='*65}")
    print(f"🚀 BENCHMARK: {strategy_name}")
    print(f"⚙️  CẤU HÌNH: Chunk Size = {chunker_strategy.chunk_size} | Top-K = {top_k} | Threshold = {threshold}")
    print(f"{'='*65}")

    # Tạo collection riêng cho từng cấu hình
    store = EmbeddingStore(collection_name=f"benchmark_{strategy_name.lower()}")
    docs_dir = Path("data/hoc-bong")
    
    if not docs_dir.exists():
        print(f"Không tìm thấy thư mục {docs_dir}.")
        return

    documents = []
    print("1. ĐANG ĐỌC VÀ CHUNK DỮ LIỆU...")
    for file_path in docs_dir.glob("*.md"):
        frontmatter, body = parse_markdown_with_frontmatter(file_path)
        
        # Đảm bảo doc_id từ file name nếu frontmatter thiếu
        if "doc_id" not in frontmatter:
            frontmatter["doc_id"] = file_path.stem
            
        chunks = chunker_strategy.chunk(body)
        
        for i, chunk_text in enumerate(chunks):
            chunk_id = f"{file_path.stem}#{i}"
            doc = Document(id=chunk_id, content=chunk_text, metadata=frontmatter)
            documents.append(doc)
            
    if documents:
        print(f"-> Đã chunk được {len(documents)} mảnh. Đang nạp vào Vector Store...")
        store.add_documents(documents)
    else:
        print("Không có tài liệu nào để nạp.")
        return
        
    # Định nghĩa queries
    queries = [
        {"q": "Thí sinh có IELTS 7.0 và GPA 9.0 thì được xét học bổng gì và giá trị bao nhiêu?", "filter": None},
        {"q": "Học bổng Chu Văn An yêu cầu điều kiện gì?", "filter": None},
        {"q": "Đối tượng nào được nhận Học bổng Chân trời mới?", "filter": None},
        {"q": "Liệt kê các mức cấp của Học bổng khuyến khích học tập theo học kỳ.", "filter": None},
    ]
    
    print("\n2. KẾT QUẢ TRUY XUẤT")
    print("-" * 65)
    
    for i, item in enumerate(queries, 1):
        query_text = item["q"]
        print(f"\n[Câu {i}] Query: {query_text}")
            
        results = store.search_with_filter(query_text, top_k=top_k, metadata_filter=item["filter"])
        
        # Lọc kết quả theo ngưỡng threshold
        valid_results = [r for r in results if r.get("score", 0.0) >= threshold]
        
        if not valid_results:
            print(f"  -> ❌ Không có kết quả nào đạt ngưỡng điểm >= {threshold}")
            continue

        for rank, r in enumerate(valid_results, 1):
            score = r.get("score", 0.0)
            # Làm sạch khoảng trắng thừa để in cho đẹp
            preview = " ".join(r.get("content", "").split())[:120]
            print(f"  {rank}. Score: {score:.4f} | Nội dung: {preview}...")

def main():
    parser = argparse.ArgumentParser(description="Công cụ chạy Benchmark đánh giá chiến lược Chunking & Truy xuất.")
    
    # Các tham số Chunking
    parser.add_argument(
        "--chunker", 
        type=str, 
        choices=["recursive", "markdown-heading"], 
        default="markdown-heading",
        help="Chọn chiến lược chunking (mặc định: markdown-heading)"
    )
    parser.add_argument(
        "--chunk-size", 
        type=int, 
        default=300, 
        help="Kích thước ký tự tối đa của mỗi chunk (mặc định: 300)"
    )

    # Các tham số Search / Retrieval
    parser.add_argument(
        "--top-k", 
        type=int, 
        default=3, 
        help="Số lượng kết quả truy xuất tối đa cần lấy (mặc định: 3)"
    )
    parser.add_argument(
        "--threshold", 
        type=float, 
        default=0.0, 
        help="Ngưỡng điểm tương đồng tối thiểu (mặc định: 0.0, ví dụ: 0.65)"
    )

    args = parser.parse_args()

    # Khởi tạo Chunker tương ứng
    if args.chunker == "recursive":
        chunker = RecursiveChunker(chunk_size=args.chunk_size)
    elif args.chunker == "markdown-heading":
        chunker = MarkdownHeadingChunker(chunk_size=args.chunk_size)
    else:
        print("Lựa chọn chunker không hợp lệ.")
        return

    # Chạy benchmark
    run_benchmark(
        chunker_strategy=chunker,
        top_k=args.top_k,
        threshold=args.threshold
    )

if __name__ == "__main__":
    main()