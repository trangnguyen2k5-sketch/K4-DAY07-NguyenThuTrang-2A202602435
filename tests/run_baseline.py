import re
import yaml
from pathlib import Path
from src.chunking import ChunkingStrategyComparator

def parse_markdown_with_frontmatter(file_path: Path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    body = content
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            body = parts[2].strip()
    return body

def run_baseline_analysis():
    target_files = [
        Path("data/hoc-bong/vnu-ulis-cam-nang-hoc-bong.md")
    ]
    
    combined_text = ""
    for path in target_files:
        if path.exists():
            body = parse_markdown_with_frontmatter(path)
            combined_text += f"{body}\n\n"
            
    if not combined_text.strip():
        print("Không tìm thấy file hoặc file rỗng. Kiểm tra lại đường dẫn.")
        return

    comparator = ChunkingStrategyComparator()
    # Chạy so sánh với chunk_size=200 để dễ quan sát sự khác biệt
    results = comparator.compare(combined_text, chunk_size=200)
    
    print(f"{'Chiến lược':<20} | {'Số lượng (Count)':<15} | {'Độ dài TB (Avg Len)'}")
    print("-" * 60)
    for strategy, stats in results.items():
        print(f"{strategy:<20} | {stats['count']:<15} | {stats['avg_length']:.2f}")
        
if __name__ == "__main__":
    run_baseline_analysis()