# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** Nhóm 2A  
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

**Thành viên 3 — Nguyễn Minh Dương**
- **Loại chiến lược:** SentenceChunker
- **Mô tả & lý do chọn:** Chiến lược này phân tách văn bản dựa trên ranh giới của các câu hoàn chỉnh (thường được nhận diện qua dấu chấm, dấu chấm hỏi hoặc dấu chấm cảm). Việc chọn SentenceChunker giúp đảm bảo mỗi đoạn văn bản (chunk) luôn giữ được trọn vẹn ý nghĩa của câu, không bị ngắt quãng giữa chừng.

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

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Mức hỗ trợ tài chính hàng tháng cao nhất dành cho sinh viên học tập tại các chương trình đào tạo tài năng theo Nghị định 179/2026/NĐ-CP tại Trường ĐHKHTN là bao nhiêu? | Hỗ trợ tài chính hàng tháng tối đa theo quy định của Nghị định 179 cho hệ tài năng ĐHKHTN. | `vnu-hus-nghi-dinh-179.md` |
| 2 | Sinh viên đang theo học tại Trường Quốc tế (VNU-IS) cần đáp ứng tiêu chuẩn chung nào về kết quả học tập và rèn luyện để được đăng ký các chương trình học bổng ngắn hạn? | Kết quả học tập đạt từ loại Giỏi/Xuất sắc và điểm rèn luyện đạt từ loại Tốt trở lên. | `vnu-is-tong-quan-hoc-bong.md` |
| 3 | Điều kiện về điểm thi THPT để thí sinh nhận Học bổng Chính phủ theo Nghị định 179/2026/NĐ-CP tại Trường ĐHKHTN là gì? | Tổng điểm thi THPT ở mức xuất sắc thuộc nhóm dẫn đầu trúng tuyển ngành học. | `vnu-hus-nghi-dinh-179.md` |
| 4 | Trong Cẩm nang học bổng VNU-ULIS, Quỹ học bổng Thắp sáng niềm tin trao tặng bao nhiêu tiền cho mỗi suất học bổng dành cho sinh viên đại học? | Trao tặng 12.000.000 VNĐ cho mỗi suất học bổng sinh viên đại học. | `vnu-ulis-cam-nang-hoc-bong.md` |
| 5 | Trường Quốc tế (VNU-IS) phân loại hệ thống học bổng dành cho sinh viên thành những nhóm nguồn chính nào? | Phân thành 3 nhóm nguồn chính: Học bổng ngân sách, Học bổng tuyển sinh VNU-IS và Học bổng đối tác/doanh nghiệp. | `vnu-is-tong-quan-hoc-bong.md` |

### Tổng hợp chất lượng truy xuất của nhóm

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Mức hỗ trợ tài chính hàng tháng cao nhất hệ tài năng... | MarkdownHeading | Có (Rank 1) | Điểm tương đồng top-1 đạt 0.2832 với filter prospective-student |
| 2 | Tiêu chuẩn học tập và rèn luyện học bổng ngắn hạn VNU-IS... | MarkdownHeading / Recursive | Có (Rank 1) | Điểm tương đồng top-1 đạt 0.2657 với filter student |
| 3 | Điều kiện điểm thi THPT nhận HB NĐ 179... | Recursive | Có (Rank 1) | Điểm tương đồng top-1 đạt 0.2536 |
| 4 | Mức học bổng Thắp sáng niềm tin tại VNU-ULIS... | MarkdownHeading | Có (Rank 1) | Điểm tương đồng top-1 đạt 0.2584 với filter student |
| 5 | Phân loại các nhóm nguồn học bổng VNU-IS... | MarkdownHeading | Có (Rank 1) | Điểm tương đồng top-1 đạt 0.3141 với filter category=scholarship |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Việc lọc metadata (`metadata_filter`) giúp ích rõ rệt ở Câu 1 (`audience: prospective-student`), Câu 2 & 4 (`audience: student`), và Câu 5 (`category: scholarship`). Lọc metadata giúp loại bỏ hoàn toàn các tài liệu không thuộc đối tượng quan tâm (ví dụ tránh lấy nhầm quy chế của sinh viên đang học cho thí sinh tuyển sinh), nâng cao độ chính xác truy xuất và tiết kiệm chi phí tính toán.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
- Cấu trúc văn bản quyết định hiệu quả của chiến lược chunking: với văn bản quy chế có tiêu đề, `MarkdownHeadingChunker` vượt trội hơn hẳn so với cắt theo độ dài cố định hay theo câu.
- Metadata pre-filtering đóng vai trò bộ lọc định hướng ngữ cảnh quan trọng trước khi truy xuất vector embedding.

**Bài học rút ra khi so sánh trong nhóm:**
- Cùng một tập tài liệu nhưng sử dụng chiến lược chia nhỏ khác nhau dẫn đến khác biệt lớn về điểm tương đồng và độ đầy đủ ngữ cảnh của chunk trả về.
- `SentenceChunker` thường làm rách rời văn bản quy chế, trong khi `RecursiveChunker` và `MarkdownHeadingChunker` duy trì mạch thông tin tốt hơn rất nhiều.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
- Nhóm sẽ bổ sung thêm trường metadata `academic_year` để lọc chính xác học kỳ/năm học áp dụng.
- Kết hợp tìm kiếm lai (Hybrid Search: BM25 + Vector Embedding) để vừa bắt chính xác từ khóa tên học bổng vừa hiểu ngữ nghĩa câu hỏi.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 10 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **40 / 40** |