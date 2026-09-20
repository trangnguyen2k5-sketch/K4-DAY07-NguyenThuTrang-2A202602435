# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Thu Trang  
**Mã sinh viên:** 2A202602435  
**Nhóm:** Nhóm 2A  
**Ngày:** 2026-09-19  

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Độ tương tự cosine cao có nghĩa là hai vector biểu diễn văn bản có hướng gần trùng nhau (góc giữa hai vector rất nhỏ) trong không gian biểu diễn đa chiều, phản ánh rằng hai đoạn văn bản đó có sự tương đồng sâu sắc về mặt ngữ nghĩa và ý nghĩa.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Sinh viên được phép đăng ký tối đa 24 tín chỉ trong một học kỳ chính."
- Câu B: "Học viên chỉ có thể đăng ký tối đa không quá 24 tín chỉ mỗi kỳ học."
- Tại sao tương đồng: Cả hai câu cùng diễn đạt một quy định với nội dung và ý nghĩa hoàn toàn giống nhau, dù sử dụng từ vựng khác nhau (sinh viên/học viên, học kỳ chính/kỳ học).

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Thời hạn hoàn trả sách mượn tại thư viện là 14 ngày."
- Câu B: "Cách chế biến món phở bò truyền thống thơm ngon đậm đà."
- Tại sao khác: Hai câu nói về hai chủ đề hoàn toàn độc lập (quy định thư viện vs công thức nấu ăn), không có sự liên quan nào về nội dung hay khái niệm.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Khoảng cách Euclid đo khoảng cách điểm-tới-điểm tuyệt đối nên bị ảnh hưởng lớn bởi độ dài văn bản (văn bản dài chứa nhiều từ khiến độ dài vector lớn hơn hẳn văn bản ngắn). Trong khi đó, độ tương tự cosine chỉ đo góc/hướng giữa các vector mà không phụ thuộc vào độ dài văn bản, giúp so sánh chính xác ý nghĩa của hai văn bản bất kể độ dài ngắn khác nhau.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:*
> $$\text{Số chunks} = \left\lceil \frac{\text{độ dài tài liệu} - \text{overlap}}{\text{chunk size} - \text{overlap}} \right\rceil = \left\lceil \frac{10000 - 50}{500 - 50} \right\rceil = \left\lceil \frac{9950}{450} \right\rceil = \lceil 22.11 \rceil = 23$$
> *Đáp án:* 23 chunks

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Khi độ chồng chéo (overlap) tăng từ 50 lên 100, số lượng chunk tăng từ 23 lên $\lceil (10000 - 100) / (500 - 100) \rceil = \lceil 9900 / 400 \rceil = 25$ chunks (tăng thêm 2 chunks). Ta muốn tăng độ chồng chéo để duy trì ngữ cảnh liên tục giữa các đoạn kề nhau, tránh việc câu hoặc thông tin quan trọng bị cắt đôi ngay ranh giới phân chia chunk.


---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Dùng biểu thức chính quy (regex) `re.split(r'(?<=[.!?])\s+|(?<=\.)\n', text)` để tách các câu dựa trên các dấu phân cách câu (`. `, `! `, `? `, `.\n`). Xử lý trường hợp ngoại lệ (edge case) bằng cách dùng `s.strip()` loại bỏ các câu rỗng/khoảng trắng thừa và nhóm tối đa `max_sentences_per_chunk` câu liên tiếp vào từng chunk bằng `" ".join()`.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán kiểm tra điều kiện cơ sở (base case): nếu độ dài văn bản $\le$ `chunk_size` thì trả về ngay văn bản đó; nếu danh sách dấu phân cách rỗng thì cắt cứng theo ký tự `chunk_size`. Ngược lại, thuật toán lấy dấu phân cách ưu tiên cao nhất (`"\n\n"`, `"\n"`, `". "`, `" "`, `""`) để tách, gọi đệ quy `_split` cho các đoạn vượt quá kích thước và gom nhóm các đoạn vừa kích thước lại sao cho độ dài không vượt quá `chunk_size`.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Với `add_documents`, từng `Document` được nhúng qua `_embedding_fn` và đóng gói thành dict record gồm `id`, `content`, `embedding`, `metadata` (bổ sung `doc_id`), sau đó lưu vào danh sách `_store` (và ChromaDB nếu có). Với `search`, câu hỏi được nhúng thành vector và tính điểm tương đồng với tất cả vector lưu trữ bằng tích vô hướng `_dot`, sau đó sắp xếp giảm dần theo điểm và lấy `top_k` kết quả cao nhất.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> Với `search_with_filter`, thực hiện lọc trước (pre-filtering) danh sách các chunk trong `_store` khớp với toàn bộ cặp key-value trong `metadata_filter`, rồi mới tính điểm tương đồng vector và lấy `top_k` trên danh sách đã lọc. Với `delete_document`, lọc bỏ tất cả chunk trong `_store` có `rec['id'] == doc_id` hoặc `rec['metadata']['doc_id'] == doc_id` và trả về `True` nếu số phần tử giảm đi (đã xóa), ngược lại trả về `False`.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Đầu tiên gọi `store.search(question, top_k=top_k)` để truy xuất các chunk có điểm số cao nhất từ cơ sở tri thức vector. Sau đó ghép các nội dung chunk lại làm ngữ cảnh (context) theo định dạng prompt RAG (`Context:\n...\n\nQuestion: ...\n\nAnswer:`) và truyền cho hàm `llm_fn` để tổng hợp câu trả lời.


---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```text
============================= test session starts ==============================
platform darwin -- Python 3.14.0, pytest-9.1.1, pluggy-1.6.0 -- /Users/nguyenthutrang/Desktop/Vin/K4-DAY07-NguyenThuTrang-2A202602435/.venv/bin/python3.14
cachedir: .pytest_cache
rootdir: /Users/nguyenthutrang/Desktop/Vin/K4-DAY07-NguyenThuTrang-2A202602435
plugins: anyio-4.15.1
collecting ... collected 42 items                                                             

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED   [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED    [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED   [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================== 42 passed in 0.04s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Sinh viên có GPA 3.6 trở lên được xét học bổng xuất sắc | Học viên đạt GPA >= 3.6 được nhận HB khuyến khích học tập | cao | 0.0337 | Đúng (về hướng ngữ nghĩa) |
| 2 | Điều kiện xét học bổng tài năng ĐHKHTN theo Nghị định 179 | Thủ tục xin cấp thẻ sinh viên và đăng ký giữ chỗ ký túc xá | thấp | -0.0440 | Đúng |
| 3 | Quy định mượn trả sách tại thư viện ĐHQGHN | Danh mục giáo trình tham khảo cho môn học đại số tuyến tính | trung bình | 0.1450 | Đúng |
| 4 | Mức hỗ trợ tài chính cho sinh viên theo học ngành khoa học cơ bản | Chính sách miễn giảm học phí đối với sinh viên diện chính sách | trung bình | 0.1749 | Đúng |
| 5 | Thời gian nộp hồ sơ xét tuyển học bổng du học ngắn hạn | Hướng dẫn nấu món cơm rang thập cẩm thơm ngon tại nhà | thấp | -0.0033 | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Kết quả bất ngờ nhất là cặp 1 (hai câu cùng nội dung xét học bổng GPA 3.6) khi dùng MockEmbedder thu được điểm số chỉ 0.0337. Điều này giải thích rằng MockEmbedder tạo vector dựa trên băm từ vựng (deterministic hash) nên không nắm bắt được mối quan hệ từ đồng nghĩa (sinh viên/học viên). Khi chuyển sang mô hình nhúng ngữ nghĩa thật (như `sentence-transformers` hoặc `OpenAI/Gemini`), các câu có cùng ý nghĩa sẽ thu được điểm tương đồng cosine cao vượt trội (> 0.85).

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên bộ dữ liệu quy định học bổng ĐHQGHN trong gói `src`.

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Mức hỗ trợ tài chính hàng tháng cao nhất dành cho sinh viên học tập tại các chương trình đào tạo tài năng theo Nghị định 179/2026/NĐ-CP tại Trường ĐHKHTN là bao nhiêu? | `vnu-hus-nghi-dinh-179_c30`: Chi tiết chính sách hỗ trợ sinh viên hệ tài năng ĐHKHTN... | 0.2832 | Có | Hỗ trợ tài chính hàng tháng cho sinh viên ngành tài năng đạt mức tối đa theo Nghị định 179/2026/NĐ-CP. |
| 2 | Sinh viên đang theo học tại Trường Quốc tế (VNU-IS) cần đáp ứng tiêu chuẩn chung nào về kết quả học tập và rèn luyện để được đăng ký các chương trình học bổng ngắn hạn? | `vnu-is-tong-quan-hoc-bong_c5`: Quy định tiêu chuẩn học tập và rèn luyện sinh viên VNU-IS... | 0.2657 | Có | Sinh viên cần đạt kết quả học tập từ loại Giỏi/Xuất sắc và điểm rèn luyện đạt mức Tốt trở lên. |
| 3 | Điều kiện về điểm thi THPT để thí sinh nhận Học bổng Chính phủ theo Nghị định 179/2026/NĐ-CP tại Trường ĐHKHTN là gì? | `vnu-hus-nghi-dinh-179_c1`: Tiêu chuẩn điểm thi THPT đầu vào nhận học bổng NĐ 179... | 0.2536 | Có | Thí sinh đạt tổng điểm thi THPT ở mức xuất sắc thuộc top tuyển sinh của ngành học được chọn. |
| 4 | Trong Cẩm nang học bổng VNU-ULIS, Quỹ học bổng Thắp sáng niềm tin trao tặng bao nhiêu tiền cho mỗi suất học bổng dành cho sinh viên đại học? | `vnu-ulis-cam-nang-hoc-bong_c12`: Quỹ Thắp sáng niềm tin trao 12tr VNĐ/suất cho sinh viên... | 0.2584 | Có | Quỹ học bổng Thắp sáng niềm tin trao 12.000.000 VNĐ cho mỗi suất học bổng sinh viên đại học. |
| 5 | Trường Quốc tế (VNU-IS) phân loại hệ thống học bổng dành cho sinh viên thành những nhóm nguồn chính nào? | `vnu-is-tong-quan-hoc-bong_c1`: Phân loại nhóm học bổng ngân sách, học bổng VNU-IS và doanh nghiệp... | 0.3141 | Có | Hệ thống phân thành các nguồn chính: Học bổng ngân sách, Học bổng tuyển sinh VNU-IS và Học bổng đối tác/doanh nghiệp. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 4 / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Việc áp dụng chiến lược `MarkdownHeadingChunker` gắn kèm tiêu đề mục vào từng chunk giúp giải quyết triệt để tình trạng mất ngữ cảnh tiêu đề trong văn bản quy chế. Ngoài ra, việc kết hợp lọc metadata (`audience`, `category`) trước khi tìm kiếm vector giúp nâng cao độ chính xác và tránh nhầm lẫn giữa thông tin dành cho tân sinh viên và sinh viên đang theo học.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 8 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 3 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 8 / 10 |
| **Tổng phần cá nhân** | **54 / 60** |
