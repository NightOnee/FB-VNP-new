# vietnam_post_bot.py
import streamlit as st
import google.generativeai as genai
import os
import random
import streamlit.components.v1 as components
from dotenv import load_dotenv

# --- PHẦN 1: CẤU HÌNH VÀ KHỞI TẠO CHUNG ---

def setup_page_and_load_keys():
    """
    Cấu hình trang, tải API keys, và chèn mã Google Analytics.
    Hàm này chỉ chạy một lần ở đầu.
    """
    st.set_page_config(page_title="Bộ công cụ Sáng tạo Nội dung", page_icon="🚀", layout="wide")
    
    # Tải các biến môi trường từ file .env
    load_dotenv()

    # Tìm và tải tất cả các API key
    api_keys = [
        os.getenv(key) for key in os.environ if key.startswith("GEMMA_API_KEY_")
    ]
    
    if not api_keys:
        st.error("LỖI: Không tìm thấy API key nào có dạng 'GEMMA_API_KEY_...' trong file .env hoặc cấu hình Secrets.")
        st.stop()
    
    # --- MÃ GOOGLE ANALYTICS ---
    st.html("""
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-85N4WR4EB7"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());

      gtag('config', 'G-85N4WR4EB7');
    </script>
    """)
    return api_keys

def get_gemma_model(api_keys):
    """
    Chọn ngẫu nhiên một API key, cấu hình và trả về đối tượng model.
    Hàm này được gọi mỗi khi cần tương tác với API.
    """
    try:
        selected_key = random.choice(api_keys)
        genai.configure(api_key=selected_key)
        model = genai.GenerativeModel('models/gemma-3-27b-it')
        return model
    except (ValueError, TypeError, IndexError) as e:
        st.error(f"LỖI: Không thể cấu hình mô hình Gemma. Lỗi: {e}")
        st.stop()
    return None

# --- PHẦN 2: CHỨC NĂNG 1 - SÁNG TẠO NỘI DUNG MỚI ---

def render_content_creation_tool(api_keys):
    """Hiển thị giao diện và xử lý logic cho việc tạo nội dung mới."""
    st.title("📮 Trợ lý Sáng tạo Nội dung Vietnam Post")
    st.caption("Chỉ cần điền 3 thông tin dưới đây, AI sẽ giúp bạn tạo ra một bài viết Facebook hoàn chỉnh!")

    # Khởi tạo session_state cho chức năng này nếu chưa có
    if 'generated_text_creator' not in st.session_state:
        st.session_state['generated_text_creator'] = ""
    if 'show_result_creator' not in st.session_state:
        st.session_state['show_result_creator'] = False

    # Vùng nhập liệu
    with st.container(border=True):
        st.subheader("1. Cung cấp thông tin cần thiết")
        san_pham_input = st.text_input("**Sản phẩm/Dịch vụ cốt lõi:**", placeholder="Ví dụ: Bảo hiểm xe máy PTI...")
        diem_nhan_input = st.text_area("**Các điểm nhấn hoặc thông tin quan trọng khác:**", placeholder="Ví dụ: Giảm giá 20%...")
        lien_he_input = st.text_input("**Thông tin liên hệ:**", placeholder="Ví dụ: 0988.888.888 - Bưu cục ABC")
        
        if st.button("Tạo bài viết ✨", type="primary", use_container_width=True):
            if not san_pham_input or not lien_he_input:
                st.warning("Vui lòng điền đầy đủ thông tin 'Sản phẩm/Dịch vụ' và 'Thông tin liên hệ'.")
            else:
                with st.spinner("Chuyên gia đang sáng tạo... ✍️"):
                    # Lấy model ngay trước khi gọi API
                    model = get_gemma_model(api_keys)
                    if model:
                        final_prompt = get_creator_prompt(san_pham_input, diem_nhan_input, lien_he_input)
                        try:
                            response = model.generate_content(final_prompt)
                            st.session_state['generated_text_creator'] = response.text
                            st.session_state['show_result_creator'] = True
                        except Exception as e:
                            st.error(f"Đã có lỗi xảy ra: {e}")
                            st.session_state['show_result_creator'] = False
    
    # Vùng hiển thị kết quả
    if st.session_state['show_result_creator'] and st.session_state['generated_text_creator']:
        display_results(st.session_state['generated_text_creator'])

def get_creator_prompt(san_pham, diem_nhan, lien_he):
    """Tạo prompt cho chức năng sáng tạo nội dung."""
    MUC_DICH_OPTIONS = {
        1: "Giới thiệu và làm rõ lợi ích của dịch vụ.",
        2: "Tăng cường tương tác (like, comment, share).",
        3: "Kêu gọi hành động cụ thể.",
    }
    GIONG_VAN_OPTIONS = {
        1: "Chuyên nghiệp & Đáng tin cậy.",
        2: "Thân thiện & Gần gũi.",
        3: "Vui vẻ & Bắt trend.",
    }
    random_muc_dich = random.choice(list(MUC_DICH_OPTIONS.values()))
    random_giong_van = random.choice(list(GIONG_VAN_OPTIONS.values()))
    
    return f"""
    # BỐI CẢNH VÀ VAI TRÒ
    BẠN LÀ: Một chuyên gia sáng tạo nội dung Social Media, am hiểu sâu sắc về thị trường Việt Nam và có chuyên môn về các sản phẩm, dịch vụ của Bưu điện Việt Nam (Vietnam Post).
    MỤC TIÊU CỦA BẠN: Giúp tôi, một nhân viên Bưu điện, tạo ra một bài viết đăng trên Facebook thật hấp dẫn, chuyên nghiệp và hiệu quả dựa trên các thông tin tôi cung cấp dưới đây.
    # NHIỆM VỤ
    Tạo một bài viết Facebook hấp dẫn dựa trên thông tin sau:
    - **Sản phẩm/Dịch vụ:** {san_pham}
    - **Mục đích:** {random_muc_dich}
    - **Giọng văn:** {random_giong_van}
    - **Điểm nhấn:** {diem_nhan or "Không có"}
    
    # YÊU CẦU ĐẦU RA
    - **Kết quả cuối cùng:** Phải là MỘT bài viết hoàn chỉnh, liền mạch, sẵn sàng để sao chép và đăng trực tiếp lên Facebook.
    - **Cấu trúc:** Bài viết phải có 3 phần rõ ràng:
        1.  **Câu Mở Đầu (Hook):** Phải thật ấn tượng, thu hút sự chú ý trong 3 giây đầu tiên (có thể là câu hỏi, một sự thật gây ngạc nhiên, hoặc một vấn đề mà khách hàng đang gặp).
        2.  **Nội dung chính:** Diễn giải các lợi ích một cách rõ ràng, dễ hiểu. Sử dụng icon (biểu tượng cảm xúc) một cách tinh tế để tăng tính sinh động và phân tách các ý. Có thể dùng gạch đầu dòng/đánh số để liệt kê.
        3.  **Kêu Gọi Hành Động (Call-to-Action):** Phải thật rõ ràng và thôi thúc.
    - **TUYỆT ĐỐI KHÔNG** được chứa các tiêu đề phân mục như "Câu Mở Đầu (Hook):", "Nội dung chính:", "Kêu gọi hành động:".
    - **Hashtag:** **BẮT BUỘC** có hashtag #VNPNA, đề xuất thêm 3-4 hashtag phù hợp, bao gồm hashtag thương hiệu, hashtag dịch vụ và hashtag xu hướng (nếu có).
    - **BẮT BUỘC** trong phần "3. **Kêu Gọi Hành Động (Call-to-Action):**" phải kết hợp thêm thông tin liên hệ sau: {lien_he}
    """

# --- PHẦN 3: CHỨC NĂNG 2 - VIẾT LẠI NỘI DUNG ---

def render_rewriter_tool(api_keys):
    """Hiển thị giao diện và xử lý logic cho việc viết lại nội dung."""
    st.title("✍️ Trợ lý Viết lại & Làm mới Nội dung")
    st.caption("Dán nội dung cũ vào đây, AI sẽ giúp bạn viết lại với một văn phong mới mẻ hơn nhưng vẫn giữ nguyên ý chính.")

    # Khởi tạo session_state cho chức năng này nếu chưa có
    if 'generated_text_rewriter' not in st.session_state:
        st.session_state['generated_text_rewriter'] = ""
    if 'show_result_rewriter' not in st.session_state:
        st.session_state['show_result_rewriter'] = False

    # Vùng nhập liệu
    with st.container(border=True):
        st.subheader("1. Dán nội dung gốc")
        original_text = st.text_area("Nội dung cần viết lại:", height=200, placeholder="Dán văn bản của bạn vào đây...")
        
        if st.button("Làm mới nội dung 🪄", type="primary", use_container_width=True):
            if not original_text.strip():
                st.warning("Vui lòng nhập nội dung cần viết lại.")
            else:
                with st.spinner("Đang tư duy lại câu chữ... 🧠"):
                    # Lấy model ngay trước khi gọi API
                    model = get_gemma_model(api_keys)
                    if model:
                        final_prompt = get_rewriter_prompt(original_text)
                        try:
                            response = model.generate_content(final_prompt)
                            st.session_state['generated_text_rewriter'] = response.text
                            st.session_state['show_result_rewriter'] = True
                        except Exception as e:
                            st.error(f"Đã có lỗi xảy ra: {e}")
                            st.session_state['show_result_rewriter'] = False

    # Vùng hiển thị kết quả
    if st.session_state['show_result_rewriter'] and st.session_state['generated_text_rewriter']:
        display_results(st.session_state['generated_text_rewriter'])

def get_rewriter_prompt(original_text):
    """Tạo prompt cho chức năng viết lại nội dung."""
    return f"""
    # VAI TRÒ
    Bạn là một biên tập viên chuyên nghiệp, bậc thầy về ngôn ngữ tiếng Việt.
    
    # NHIỆM VỤ
    Hãy đọc kỹ văn bản gốc dưới đây và viết lại nó theo một văn phong hơi khác đi một chút.
    
    # YÊU CẦU
    - **GIỮ NGUYÊN** tất cả các ý chính, thông điệp cốt lõi, và các dữ kiện quan trọng của văn bản gốc.
    - Sử dụng từ ngữ, cấu trúc câu đa dạng hơn để làm mới nội dung.
    - Không thêm thông tin mới không có trong văn bản gốc.
    - Kết quả phải là một đoạn văn bản hoàn chỉnh, tự nhiên và trôi chảy.
    - **Hashtag:** **BẮT BUỘC** có hashtag #VNPNA, đề xuất thêm 3-4 hashtag phù hợp, bao gồm hashtag thương hiệu, hashtag dịch vụ và hashtag xu hướng (nếu có).
    # VĂN BẢN GỐC
    ---
    {original_text}
    ---
    """

# --- PHẦN 4: HÀM TIỆN ÍCH CHUNG (HIỂN THỊ KẾT QUẢ) ---

def display_results(text):
    """Hàm chung để hiển thị kết quả và các nút thao tác."""
    with st.container(border=True):
        st.subheader("2. Kết quả")
        st.markdown(text)
        
        st.divider()
        
        st.subheader("3. Sao chép nội dung")
        
        st.info("💡 **Hướng dẫn:** Để sao chép, hãy nhấn vào **biểu tượng sao chép** 📋 ở góc trên bên phải của khung nội dung dưới đây.")
        
        # Sử dụng st.code để hiển thị văn bản với nút copy tích hợp, đáng tin cậy.
        st.code(text, language=None)

# --- PHẦN 5: CHƯƠNG TRÌNH CHÍNH ---

def main():
    """Hàm chính điều phối toàn bộ ứng dụng."""
    api_keys = setup_page_and_load_keys()

    # Thanh điều hướng bên trái (Sidebar)
    with st.sidebar:
        st.header("🚀 Chọn chức năng")
        st.write("Vui lòng chọn tác vụ bạn muốn thực hiện:")
        
        app_mode = st.selectbox(
            label="Chức năng",
            options=["--Chọn--", "1. Sáng tạo nội dung mới", "2. Viết lại nội dung cũ"],
            label_visibility="collapsed"
        )
    
    # Dựa vào lựa chọn để hiển thị giao diện tương ứng
    if app_mode == "1. Sáng tạo nội dung mới":
        render_content_creation_tool(api_keys)
    elif app_mode == "2. Viết lại nội dung cũ":
        render_rewriter_tool(api_keys)
    else:
        st.info("👋 **Đây là ứng dụng hỗ trợ 2 tác vụ:** sáng tạo nội dung mới và viết lại nội dung cũ theo văn phong mới.")
        st.subheader("Vui lòng chọn một chức năng từ thanh công cụ bên trái để bắt đầu.")

if __name__ == "__main__":
    main()

