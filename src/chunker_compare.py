import re
import math

# ==========================================
# 1. CÁC CLASS CHUNKING STRATEGIES
# ==========================================
class FixedSizeChunker:
    def __init__(self, chunk_size: int = 200, overlap: int = 20):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        if not text: return []
        step = self.chunk_size - self.overlap
        chunks = []
        for start in range(0, len(text), step):
            chunks.append(text[start : start + self.chunk_size])
            if start + self.chunk_size >= len(text): break
        return chunks

class SentenceChunker:
    def __init__(self, max_sentences: int = 2):
        self.max_sentences = max_sentences

    def chunk(self, text: str) -> list[str]:
        if not text: return []
        sentences = re.split(r"(?<=[.!?])(?:\s+)", text.strip())
        sentences = [s.strip() for s in sentences if s.strip()]
        chunks = []
        for i in range(0, len(sentences), self.max_sentences):
            chunks.append(" ".join(sentences[i:i + self.max_sentences]))
        return chunks

class RecursiveChunker:
    def __init__(self, chunk_size: int = 200):
        self.separators = ["\n\n", "\n", ". ", " ", ""]
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        return self._split(text, self.separators)

    def _split(self, text: str, separators: list[str]) -> list[str]:
        if len(text) <= self.chunk_size: return [text]
        sep = next((s for s in separators if s in text or s == ""), "")
        splits = text.split(sep) if sep else list(text)
        
        chunks, curr_chunk, curr_len = [], [], 0
        next_seps = separators[separators.index(sep)+1:] if sep in separators else []
        
        for s in splits:
            if len(s) > self.chunk_size:
                if curr_chunk: chunks.append(sep.join(curr_chunk))
                chunks.extend(self._split(s, next_seps))
                curr_chunk, curr_len = [], 0
            elif curr_len + len(s) + len(sep) > self.chunk_size:
                chunks.append(sep.join(curr_chunk))
                curr_chunk, curr_len = [s], len(s)
            else:
                curr_chunk.append(s)
                curr_len += len(s) + (len(sep) if curr_chunk else 0)
        if curr_chunk: chunks.append(sep.join(curr_chunk))
        return chunks

class MarkdownHeadingChunker:
    """Tự động đính kèm heading vào các chunk con nếu vượt quá giới hạn size."""
    def __init__(self, chunk_size: int = 200):
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        chunks = []
        parts = re.split(r'(^#+\s+.*$)', text, flags=re.MULTILINE)
        current_heading, current_block = "", ""
        
        for part in parts:
            if re.match(r'^#+\s+', part):
                if current_block.strip():
                    chunks.extend(self._split_large_block(current_block, current_heading))
                current_heading = part.strip()
                current_block = current_heading + "\n"
            else:
                current_block += part
        if current_block.strip():
            chunks.extend(self._split_large_block(current_block, current_heading))
        return [c for c in chunks if c.strip()]

    def _split_large_block(self, text: str, heading: str) -> list[str]:
        if len(text) <= self.chunk_size: return [text.strip()]
        sub_chunks = []
        temp_chunk = heading + "\n" if heading else ""
        for p in text.split('\n\n'):
            p = p.strip()
            if not p or p == heading: continue
            if len(temp_chunk) + len(p) < self.chunk_size:
                temp_chunk += p + "\n\n"
            else:
                if temp_chunk.strip() and temp_chunk.strip() != heading:
                    sub_chunks.append(temp_chunk.strip())
                temp_chunk = (heading + "\n" + p + "\n\n") if heading else (p + "\n\n")
        if temp_chunk.strip() and temp_chunk.strip() != heading:
            sub_chunks.append(temp_chunk.strip())
        return sub_chunks

# ==========================================
# 2. HÀM ĐÁNH GIÁ & TẠO BẢNG MARKDOWN
# ==========================================
def evaluate_and_generate_markdown():
    sample_text = """# Học bổng Xuất sắc Toàn diện 2026
Học bổng Xuất sắc Toàn diện là chương trình hỗ trợ tài chính cao nhất của trường đại học dành cho sinh viên có thành tích nổi bật. Học bổng này nhằm tôn vinh những nỗ lực học tập và rèn luyện.

## Điều kiện xét duyệt
Để đạt được học bổng này, sinh viên cần có điểm trung bình tích lũy (GPA) từ 3.6/4.0 trở lên trong năm học vừa qua. 
Đồng thời, điểm rèn luyện phải đạt từ 90 điểm trở lên. Sinh viên không bị kỷ luật dưới mọi hình thức.

## Mức cấp phát
Học bổng bao gồm 100% học phí của năm học tiếp theo. Ngoài ra, sinh viên sẽ nhận được khoản hỗ trợ sinh hoạt phí trị giá 2.000.000 VNĐ/tháng, kéo dài trong 10 tháng."""

    strategies = {
        "fixed_size": FixedSizeChunker(chunk_size=200, overlap=20),
        "by_sentences": SentenceChunker(max_sentences=2),
        "recursive": RecursiveChunker(chunk_size=200),
        "markdown_heading": MarkdownHeadingChunker(chunk_size=250)
    }

    print("| Chiến lược (Strategy) | Số chunks | Độ dài TB | Đánh giá giữ ngữ cảnh (Tìm đoạn chứa \"3.6/4.0\") | Nội dung đoạn trích xuất (Preview) |")
    print("|-------------------|:---:|:---:|---|---|")

    for name, chunker in strategies.items():
        chunks = chunker.chunk(sample_text)
        count = len(chunks)
        avg_len = sum(len(c) for c in chunks) / count if count > 0 else 0

        # TÌM CHUNK CHỨA ĐIỀU KIỆN "3.6/4.0"
        target_chunk = next((c for c in chunks if "3.6/4.0" in c), None)
        
        if target_chunk:
            # KIỂM TRA NGỮ CẢNH
            if "Xuất sắc Toàn diện" in target_chunk or "Điều kiện xét duyệt" in target_chunk:
                eval_str = "✅ **Giữ ngữ cảnh** (Có chứa \"Xuất sắc Toàn diện\")"
            else:
                eval_str = "❌ **Mất ngữ cảnh** (Không chứa tên học bổng)"
                
            preview = target_chunk.replace('\n', ' <br> ')
            preview = preview[:170] + "..." if len(preview) > 170 else preview
        else:
            eval_str = "⚠️ Không tìm thấy"
            preview = ""

        print(f"| **{name}** | {count} | {avg_len:.1f} | {eval_str} | `{preview}` |")

if __name__ == "__main__":
    evaluate_and_generate_markdown()