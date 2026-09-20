# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** Nhóm G30 
**Thành viên:**  
- Hoàng Trung Khải  
- Nguyễn Minh Dương
- Nguyễn Thu Trang

**Ngày:** 2026-09-19  

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Học bổng & Quy định đào tạo của Đại học Quốc gia Hà Nội (VNU-HUS, VNU-IS, VNU-ULIS).

**Tại sao nhóm chọn chủ đề này?**
> Đây là thông tin quan trọng, cập nhật và có nhu cầu tra cứu cao từ sinh viên, học viên và tân sinh viên. Tất cả nguồn đều là trang chính thức của các đơn vị thuộc ĐHQGHN (hus.vnu.edu.vn, is.vnu.edu.vn, ulis.vnu.edu.vn), công khai, không chứa dữ liệu cá nhân. Chủ đề có cấu trúc rõ ràng (điều kiện xét duyệt, mức hỗ trợ, đối tượng, thời hạn) nên rất phù hợp để xây dựng hệ thống RAG có khả năng lọc metadata theo đối tượng (`audience`) và loại học bổng (`category`).

### Danh sách tài liệu (Data Inventory)

| #   | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
| --- | ------------ | ------------------ | -------------------- | -------- | --------------- |
| 1   | Cơ hội nhận học bổng Chính phủ theo Nghị định 179 tại Trường ĐHKHTN | https://hus.vnu.edu.vn/tin-tuc-su-kien/dao-tao-tuyen-sinh/co-hoi-nhan-hoc-bong-chinh-phu-theo-nghi-dinh-179-tai-truong-dai-hoc-khoa-hoc-tu-nhien-dhqghn-145744 | 2026-09-19 / 2026 | 10,882 | doc_id=vnu-hus-nghi-dinh-179, audience=prospective-student, category=scholarship, language=vi |
| 2   | Học bổng ngắn hạn - Trường Quốc tế - ĐHQGHN | https://www.is.vnu.edu.vn/doi-song-sinh-vien/hoc-bong-ngan-han/ | 2026-09-19 / not-stated | 6,535 | doc_id=vnu-is-hoc-bong-ngan-han, audience=student, category=scholarship, language=vi |
| 3   | Học bổng dự kiến năm 2026 - Trường Quốc tế - ĐHQGHN | https://www.is.vnu.edu.vn/tuyen-sinh/hoc-bong/ | 2026-09-19 / 2026 | 13,989 | doc_id=vnu-is-hoc-bong-tuyen-sinh, audience=prospective-student, category=scholarship, language=vi |
| 4   | Tổng quan hệ thống học bổng - Trường Quốc tế - ĐHQGHN | https://www.is.vnu.edu.vn/doi-song-sinh-vien/tong-quan-he-thong-hoc-bong/ | 2026-09-19 / not-stated | 7,063 | doc_id=vnu-is-tong-quan-hoc-bong, audience=student, category=scholarship, language=vi |
| 5   | Cẩm nang Học bổng cho học sinh sinh viên Trường ĐH Ngoại ngữ | https://ulis.vnu.edu.vn/cam-nang-hoc-bong-cho-hoc-sinh-sinh-vien-hoc-vien-cua-truong-dai-hoc-ngoai-ngu/ | 2026-09-19 / not-stated | 16,606 | doc_id=vnu-ulis-cam-nang-hoc-bong, audience=student, category=scholarship, language=vi |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata       | Kiểu     | Ví dụ giá trị                                      | Tại sao hữu ích cho truy xuất (retrieval)? |
| --------------------- | -------- | -------------------------------------------------- | ------------------------------------------ |
| url / source_url      | string   | https://hus.vnu.edu.vn/...                         | Truy xuất nguồn gốc, kiểm chứng thông tin  |
| retrieved_at          | date     | 2026-09-19                                         | Biết độ mới của dữ liệu                    |
| doc_id                | string   | vnu-hus-nghi-dinh-179                              | Định danh duy nhất, dễ quản lý & cập nhật  |
| title                 | string   | Cơ hội nhận học bổng Chính phủ...                  | Hiển thị kết quả, hỗ trợ keyword search    |
| audience              | string   | student / prospective-student                      | Lọc chính xác theo đối tượng (sinh viên / tân sinh viên) |
| department            | string   | admissions / student-affairs                       | Lọc theo đơn vị ban hành                   |
| category              | string   | scholarship                                        | Lọc theo loại học bổng                     |
| language              | string   | vi                                                 | Đảm bảo ngôn ngữ phù hợp                   |
| document_version      | string   | 2026 / not-stated                                  | Ưu tiên tài liệu mới / đúng phiên bản      |
| license_or_permission | string   | public-source                                      | Xác nhận quyền sử dụng hợp pháp            |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên tài liệu `vnu-ulis-cam-nang-hoc-bong.md` (tham số `chunk_size = 200`):

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| `vnu-ulis-cam-nang-hoc-bong.md` | FixedSizeChunker (`fixed_size`) | 91 | 198.09 | **Kém.** Cắt cứng nhắc theo số ký tự. Dễ cắt ngang giữa câu hoặc chia cắt danh sách làm mất tiêu đề/ngữ cảnh. |
| `vnu-ulis-cam-nang-hoc-bong.md` | SentenceChunker (`by_sentences`) | 34 | 467.82 | **Kém.** Chunk quá dài (>460 ký tự). Dễ gom thành các khối khổng lồ nếu văn bản dùng nhiều gạch đầu dòng thay vì dấu chấm câu. |
| `vnu-ulis-cam-nang-hoc-bong.md` | RecursiveChunker (`recursive`) | 123 | 130.08 | **Khá.** Ưu tiên cắt theo đoạn/câu nên giữ ngữ nghĩa tốt hơn. Tuy nhiên, các đoạn quá dài vẫn bị ép cắt ngang, có thể làm đứt liên kết với tiêu đề. |

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

<!-- **Thành viên 1 — [Tên]**
- **Loại chiến lược:** [FixedSize / Sentence / Recursive / custom]
- **Mô tả & lý do chọn cho chủ đề này:** *(2-3 câu)*
- **Code snippet (nếu custom):**
```python
# Dán mã nguồn (implementation) vào đây
``` -->

**Thành viên 1 — Hoàng Trung Khải**
- **Loại chiến lược:** MarkdownHeading
- **Mô tả & lý do chọn cho chủ đề này:** Chiến lược này phân tách văn bản dựa trên các thẻ tiêu đề (Heading) của Markdown và tự động đính kèm tiêu đề đó vào phần đầu của các chunk con nếu đoạn văn bên dưới quá dài. Vì dữ liệu về quy chế học bổng luôn được cấu trúc chặt chẽ theo các mục (ví dụ: tên học bổng, đối tượng, điều kiện, mức cấp phát), cách làm này giúp bảo toàn ngữ cảnh trọn vẹn, đảm bảo hệ thống RAG không bao giờ trả về một "điều kiện xét tuyển" lơ lửng mà thiếu đi thông tin nó thuộc loại học bổng nào.
- **Code snippet:**
```python
class MarkdownHeadingChunker:
    def __init__(self, chunk_size: int = 300):
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        chunks = []
        parts = re.split(r'(^#+\s+.*$)', text, flags=re.MULTILINE)
        
        current_heading = ""
        current_block = ""
        
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

    def _split_large_block(self, text: str, current_heading: str) -> list[str]:
        """Chia nhỏ một khối văn bản nếu nó vượt quá chunk_size, luôn đính kèm heading."""
        if len(text) <= self.chunk_size:
            return [text.strip()]
            
        sub_chunks = []
        paragraphs = text.split('\n\n')
        
        temp_chunk = current_heading + "\n" if current_heading else ""
        
        for p in paragraphs:
            p = p.strip()
            if not p or p == current_heading:
                continue
                
            if len(temp_chunk) + len(p) < self.chunk_size:
                temp_chunk += p + "\n\n"
            else:
                if temp_chunk.strip() and temp_chunk.strip() != current_heading:
                    sub_chunks.append(temp_chunk.strip())
                temp_chunk = (current_heading + "\n" + p + "\n\n") if current_heading else (p + "\n\n")
                
        if temp_chunk.strip() and temp_chunk.strip() != current_heading:
            sub_chunks.append(temp_chunk.strip())
            
        return sub_chunks
```


**Thành viên 2 — Nguyễn Thu Trang**
- **Loại chiến lược:** RecursiveChunker
- **Mô tả & lý do chọn:** Chiến lược này phân tách văn bản đệ quy dựa trên mức độ ưu tiên của các dấu phân cách (như xuống dòng kép, dấu chấm câu, khoảng trắng) nhằm giữ trọn vẹn các đoạn văn hoặc câu dưới một giới hạn kích thước nhất định.
- **Code snippet:**
```python
class RecursiveChunker:
    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        return self._split(text, self.separators)

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        if len(current_text) <= self.chunk_size:
            return [current_text] if current_text else []

        if not remaining_separators:
            return [
                current_text[i : i + self.chunk_size]
                for i in range(0, len(current_text), self.chunk_size)
            ] if current_text else []

        separator = remaining_separators[0]
        next_separators = remaining_separators[1:]

        splits = current_text.split(separator)
        good_splits = []
        for part in splits:
            if len(part) > self.chunk_size:
                sub_chunks = self._split(part, next_separators)
                good_splits.extend(sub_chunks)
            else:
                good_splits.append(part)

        merged_chunks, current_chunk = [], ""
        for part in good_splits:
            if not part:
                continue
            if not current_chunk:
                current_chunk = part
            else:
                candidate = current_chunk + separator + part
                if len(candidate) <= self.chunk_size:
                    current_chunk = candidate
                else:
                    merged_chunks.append(current_chunk)
                    current_chunk = part

        if current_chunk:
            merged_chunks.append(current_chunk)

        return merged_chunks if merged_chunks else [current_text]
```

**Thành viên 3 — Nguyễn Minh Dương**
- **Loại chiến lược:** SentenceChunker
- **Mô tả & lý do chọn:** Chiến lược này phân tách văn bản dựa trên ranh giới của các câu hoàn chỉnh (thường được nhận diện qua dấu chấm, dấu chấm hỏi hoặc dấu chấm cảm). Việc chọn SentenceChunker giúp đảm bảo mỗi đoạn văn bản (chunk) luôn giữ được trọn vẹn ý nghĩa của câu, không bị ngắt quãng giữa chừng.
- **Code snippet:**
```python
class SentenceChunker:
    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        raw_sentences = re.split(r'(?<=[.!?])\s+|(?<=\.)\n', text)
        sentences = [s.strip() for s in raw_sentences if s.strip()]

        if not sentences:
            return []

        chunks: list[str] = []
        for i in range(0, len(sentences), self.max_sentences_per_chunk):
            group = sentences[i : i + self.max_sentences_per_chunk]
            chunk_str = " ".join(group).strip()
            if chunk_str:
                chunks.append(chunk_str)
        return chunks
```

# Đánh Giá Và So Sánh Chiến Lược Phân Tách Dữ Liệu (Chunking)

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| **1. Hoàng Trung Khải** | MarkdownHeading | 9/10 | Giữ vững ngữ cảnh phân cấp, luôn gắn chặt các thông tin chi tiết (điều kiện, mức thưởng) với tên học bổng tương ứng. | Phụ thuộc hoàn toàn vào việc văn bản gốc phải được định dạng thẻ heading (Markdown) rõ ràng, chuẩn xác. |
| **2. Nguyễn Thu Trang** | RecursiveChunker | 7.5/10 | Cân bằng tốt kích thước chunk và linh hoạt xử lý được nhiều loại định dạng văn bản khác nhau. | Dễ làm đứt gãy mối liên kết giữa tiêu đề (tên học bổng) và nội dung bên dưới nếu đoạn văn bản quá dài. |
| **3. Nguyễn Minh Dương** | SentenceChunker | 5.0/10 | Đảm bảo không bao giờ bị ngắt ý giữa chừng; các đoạn trích xuất luôn là câu hoàn chỉnh về mặt ngữ pháp. | Phá vỡ hoàn toàn cấu trúc tài liệu; các câu điều kiện (VD: "GPA từ 3.2") khi đứng độc lập sẽ bị mất ngữ cảnh, không biết thuộc học bổng nào. |

### Chiến lược nào tốt nhất cho chủ đề này? Tại sao?

> MarkdownHeading là chiến lược tốt nhất cho chủ đề "Quy chế học bổng" vì loại văn bản này có tính cấu trúc phân tầng cực kỳ chặt chẽ. Việc tự động đính kèm tiêu đề mục vào mọi đoạn văn con giúp giải quyết triệt để tình trạng "mất ngữ cảnh" trong RAG, đảm bảo hệ thống luôn biết chính xác một điều kiện xét tuyển hay mức hỗ trợ tài chính đang thuộc về loại học bổng cụ thể nào. Tuy nhiên trong data không phải lúc nào cũng có cấu trúc Markdown thật nhưng MarkdownHeading có fallback về Recursive để giải quyết tình huống này.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Mức hỗ trợ tài chính hàng tháng cao nhất dành cho sinh viên học tập tại các chương trình đào tạo tài năng theo Nghị định 179/2026/NĐ-CP tại Trường ĐHKHTN là bao nhiêu? | Mức hỗ trợ tài chính hàng tháng cao nhất là 5.500.000 đồng/tháng dành riêng cho sinh viên học tập tại các chương trình đào tạo tài năng (thuộc danh mục ưu tiên). | `vnu-hus-nghi-dinh-179.md` *(Yêu cầu `filter={"audience": "prospective-student"}`)* |
| 2 | Sinh viên đang theo học tại Trường Quốc tế (VNU-IS) cần đáp ứng tiêu chuẩn chung nào về kết quả học tập và rèn luyện để được đăng ký các chương trình học bổng ngắn hạn? | Kết quả học tập đạt loại Giỏi trở lên (GPA $\ge 3.2$), điểm rèn luyện đạt loại Tốt trở lên ($\ge 80$ điểm), không bị kỷ luật từ mức khiển trách. | `vnu-is-hoc-bong-ngan-han.md` *(Yêu cầu `filter={"audience": "student"}`)* |
| 3 | Điều kiện về điểm thi THPT để thí sinh nhận Học bổng Chính phủ theo Nghị định 179/2026/NĐ-CP tại Trường ĐHKHTN là gì? | Tổng điểm Toán và 2 môn tổ hợp đạt từ 22,50/30 trở lên (không tính điểm ưu tiên) và nằm trong top 30% điểm trúng tuyển cao nhất của nhóm ngành. | `vnu-hus-nghi-dinh-179.md` |
| 4 | Trong Cẩm nang học bổng VNU-ULIS, Quỹ học bổng Thắp sáng niềm tin trao tặng bao nhiêu tiền cho mỗi suất học bổng dành cho sinh viên đại học? | Quỹ học bổng Thắp sáng niềm tin trao 12.000.000 VNĐ/học bổng cho mỗi sinh viên. | `vnu-ulis-cam-nang-hoc-bong.md` *(Yêu cầu `filter={"audience": "student"}`)* |
| 5 | Trường Quốc tế (VNU-IS) phân loại hệ thống học bổng dành cho sinh viên thành những nhóm nguồn chính nào? | Gồm 3 nhóm chính: 1) Nguồn ngân sách nhà nước; 2) Tài trợ ngoài ngân sách (doanh nghiệp/tổ chức); 3) Hỗ trợ sinh viên có hoàn cảnh khó khăn. | `vnu-is-tong-quan-hoc-bong.md` *(Yêu cầu `filter={"category": "scholarship"}`)* |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Mức hỗ trợ tài chính hàng tháng cao nhất dành cho sinh viên học tập tại các chương trình đào tạo tài năng theo Nghị định 179/2026/NĐ-CP tại Trường ĐHKHTN là bao nhiêu? | MarkdownHeading + Filter | Có (Top 1) - Score: 2 | Bắt buộc dùng filter `audience="prospective-student"` để hệ thống không lấy nhầm các mức hỗ trợ của sinh viên đang học. |
| 2 | Sinh viên đang theo học tại Trường Quốc tế (VNU-IS) cần đáp ứng tiêu chuẩn chung nào về kết quả học tập và rèn luyện để được đăng ký các chương trình học bổng ngắn hạn? | RecursiveChunker | Có (Top 1) - Score: 2 | Các điều kiện (GPA, rèn luyện, kỷ luật) viết thành 1 đoạn dài. Recursive giữ trọn vẹn đoạn này tốt hơn SentenceChunker. |
| 3 | Điều kiện về điểm thi THPT để thí sinh nhận Học bổng Chính phủ theo Nghị định 179/2026/NĐ-CP tại Trường ĐHKHTN là gì? | MarkdownHeading | Có (Top 2/3) - Score: 1 | Chiến lược giúp đính kèm trọn vẹn tiêu đề 'Nghị định 179' vào chi tiết điều kiện điểm THPT. |
| 4 | Trong Cẩm nang học bổng VNU-ULIS, Quỹ học bổng Thắp sáng niềm tin trao tặng bao nhiêu tiền cho mỗi suất học bổng dành cho sinh viên đại học? | SentenceChunker + Filter | Có (Top 1) - Score: 2 | Trích xuất được đúng câu có số '12.000.000 VNĐ', nhưng dễ bị ngắt khỏi ngữ cảnh nếu không cẩn thận. |
| 5 | Trường Quốc tế (VNU-IS) phân loại hệ thống học bổng dành cho sinh viên thành những nhóm nguồn chính nào? | MarkdownHeading | Có (Top 1) - Score: 2 | Gom trọn vẹn được danh sách 3 nhóm liệt kê dưới thẻ tiêu đề `## Hệ thống học bổng`. |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Có, lọc bằng metadata đặc biệt phát huy tác dụng ở **Câu 1** và **Câu 4**. Nhờ giới hạn từ khóa `audience="prospective-student"` (thí sinh tuyển sinh) hay `audience="student"` (sinh viên đang học), hệ thống RAG thu hẹp được phạm vi tìm kiếm, tránh việc Cosine Similarity lấy nhầm chính sách hỗ trợ tài chính của nhóm đối tượng khác, từ đó giúp Agent trả lời chính xác số tiền và điều kiện mà không bị "ảo giác" (hallucinate).

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> Điểm Cosine Similarity đo lường sự tương đồng về "chủ đề" và "từ vựng" chứ không đo lường logic. Một câu khẳng định và một câu phủ định hoàn toàn có thể đạt điểm Cosine > 0.9. Do đó, Metadata Filtering là chốt chặn bắt buộc để hệ thống không bị "ảo giác" (hallucinate).

> Thuật toán phân mảnh (Chunking) quyết định trực tiếp đến năng lực của Agent. Một Agent dùng mô hình LLM xịn đến mấy cũng sẽ trả lời sai nếu Chunking cắt đứt cụm từ chứa đáp án ra khỏi ngữ cảnh của nó.

> Việc xử lý cấu trúc văn bản (như dùng MarkdownHeadingChunker) luôn mang lại hiệu quả cao hơn các thuật toán chia nhỏ mù quáng theo số lượng ký tự (FixedSize).

**Bài học rút ra khi so sánh trong nhóm:**
> Qua việc so sánh chéo, nhóm nhận ra rằng cùng một bộ tài liệu và cùng một câu hỏi, chiến lược SentenceChunker thường làm đứt gãy ngữ cảnh (vì các câu điều kiện đứng độc lập trở nên vô nghĩa), trong khi MarkdownHeadingChunker xuất sắc trong việc gắn kết chi tiết với tiêu đề gốc.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Thay vì chỉ gán metadata tĩnh, nhóm sẽ áp dụng phương pháp LLM-extracted Metadata (Dùng LLM đọc lướt tài liệu để tự động sinh ra các tag metadata như giá_trị_học_bổng, yêu_cầu_gpa...).

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 9 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | ** 39 / 40** |
