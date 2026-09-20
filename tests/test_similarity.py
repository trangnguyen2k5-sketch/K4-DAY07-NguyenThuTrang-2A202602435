import os
from dotenv import load_dotenv

from src.chunking import compute_similarity
from src.embeddings import GeminiEmbedder

def run_similarity_predictions():
    load_dotenv()
    
    print("Đang khởi tạo GeminiEmbedder (Gọi API để lấy vector)...")
    try:
        embedder = GeminiEmbedder()
    except Exception as e:
        print(f"Lỗi khởi tạo Embedder: {e}")
        return

    # 5 cặp câu từ Báo cáo cá nhân (đã bỏ markdown in đậm để nhúng vector chính xác)
    pairs = [
        (
            "GPA tối thiểu để duy trì học bổng toàn phần là 3.6/4.0.",
            "Để không bị cắt học bổng 100%, sinh viên phải giữ điểm tổng kết từ 3.6 trở lên.",
            "Cao"
        ),
        (
            "Mức hỗ trợ của học bổng Vượt Khó là 2.000.000 VNĐ mỗi tháng.",
            "Hạn chót nộp hồ sơ xin xác nhận vay vốn ngân hàng là ngày 15/10.",
            "Thấp"
        ),
        (
            "Học bổng Khuyến khích học tập dành cho sinh viên năm nhất.",
            "Học bổng Khuyến khích học tập không dành cho sinh viên năm nhất.",
            "Thấp"
        ),
        (
            "Sinh viên thuộc diện hộ nghèo sẽ được hỗ trợ toàn bộ học phí.",
            "Nhà trường miễn 100% học phí cho các bạn có hoàn cảnh đặc biệt khó khăn.",
            "Cao"
        ),
        (
            "Sinh viên vi phạm kỷ luật sẽ bị tước quyền xét học bổng.",
            "Quyền xét học bổng của sinh viên sẽ bị tước nếu vi phạm kỷ luật.",
            "Cao"
        )
    ]

    print("\nKết quả (Copy phần bảng dưới đây vào file REPORT_CANHAN.md):\n")
    print("| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |")
    print("|---|---|---|---|---|---|")
    
    for i, (text_a, text_b, prediction) in enumerate(pairs, 1):
        # Biến text thành vector
        vec_a = embedder(text_a)
        vec_b = embedder(text_b)
        
        # Tính điểm tương đồng Cosine
        score = compute_similarity(vec_a, vec_b)
        
        # Đánh giá xem dự đoán đúng hay sai (ngưỡng phân biệt Cao/Thấp quy ước khoảng 0.5)
        is_high = score > 0.5
        predicted_high = prediction == "Cao"
        is_correct = "✅ Có" if is_high == predicted_high else "❌ Không"
        
        # In ra định dạng dòng bảng Markdown
        print(f"| {i} | {text_a} | {text_b} | {prediction} | **{score:.2f}** | {is_correct} |")

if __name__ == "__main__":
    run_similarity_predictions()