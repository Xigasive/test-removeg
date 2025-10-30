# remove_bg_pro_web.py
import streamlit as st
from rembg import remove, new_session
from PIL import Image
import io
import zipfile
import os
from datetime import datetime

# ตั้งค่า
st.set_page_config(page_title="Remove BG Pro", page_icon="✂️", layout="wide")
st.markdown(
    """
    <style>
    .main {background-color: #0e1117; color: white;}
    .stButton>button {background-color: #ff4b4b; color: white; border-radius: 12px; height: 3em; width: 100%;}
    .stProgress > div > div > div > div {background-color: #ff4b4b;}
    .uploaded-file {background-color: #1f1f1f; padding: 10px; border-radius: 10px; margin: 5px 0;}
    </style>
    """, unsafe_allow_html=True
)

# โหลด session
@st.cache_resource
def load_session():
    return new_session("u2netp")

session = load_session()

# Header
col1, col2 = st.columns([1, 4])
with col1:
    st.image("https://img.icons8.com/fluency/48/000000/scissors.png")
with col2:
    st.markdown("<h1 style='margin:0;'>✂️ Remove BG Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p style='margin:0; color:#888;'>ลบพื้นหลังภาพ AI – เร็ว แม่น งานหนักได้</p>", unsafe_allow_html=True)

st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("การตั้งค่า")
    model = st.selectbox("โมเดล AI", ["u2netp (เร็ว)", "u2net (แม่น)", "u2net_human_seg (คน)"], index=0)
    if model != "u2netp":
        session = new_session(model.split()[0])
    st.info("**รองรับ:** PNG, JPG, JPEG\n**ผลลัพธ์:** PNG โปร่งใส")

# อัปโหลด
uploaded_files = st.file_uploader(
    "ลากรูปมาวางที่นี่ (หลายไฟล์ได้)",
    type=['png', 'jpg', 'jpeg'],
    accept_multiple_files=True,
    help="กด Ctrl/Cmd + A เพื่อเลือกทั้งหมด"
)

if uploaded_files:
    total = len(uploaded_files)
    progress_bar = st.progress(0)
    status_text = st.empty()
    results = []

    # ตัวอย่างก่อน-หลัง
    preview_cols = st.columns(min(4, total))
    for i, uploaded_file in enumerate(uploaded_files[:4]):
        with preview_cols[i]:
            image = Image.open(uploaded_file)
            st.image(image, caption=f"ก่อน: {uploaded_file.name[:15]}...", use_column_width=True)

    st.markdown("---")

    # ประมวลผล
    for idx, uploaded_file in enumerate(uploaded_files):
        status_text.text(f"กำลังประมวลผล: {uploaded_file.name} ({idx+1}/{total})")
        
        try:
            input_image = Image.open(uploaded_file).convert("RGBA")
            output_image = remove(input_image, session=session)

            # บันทึกในหน่วยความจำ
            buf = io.BytesIO()
            output_image.save(buf, format='PNG')
            results.append({
                'name': f"{os.path.splitext(uploaded_file.name)[0]}_nobg.png",
                'data': buf.getvalue()
            })

            # ตัวอย่างหลัง (แสดง 4 อันแรก)
            if idx < 4:
                with preview_cols[idx]:
                    st.image(output_image, caption=f"หลัง", use_column_width=True)

        except Exception as e:
            st.error(f"ผิดพลาด: {uploaded_file.name} → {str(e)}")

        progress_bar.progress((idx + 1) / total)

    # ดาวน์โหลดทั้งหมด
    if results:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for result in results:
                zip_file.writestr(result['name'], result['data'])
        zip_buffer.seek(0)

        st.success(f"เสร็จสิ้น! ประมวลผล {len(results)} ภาพ")
        st.download_button(
            label="ดาวน์โหลดทั้งหมด (ZIP)",
            data=zip_buffer,
            file_name=f"remove_bg_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
            mime="application/zip"
        )
        status_text.text("พร้อมดาวน์โหลด!")

else:
    st.info("ลากรูปมาวางที่นี่ หรือกดเพื่อเลือกไฟล์")
    st.markdown(
        """
        <div style='text-align:center; padding:50px; background:#1f1f1f; border-radius:15px; margin:20px 0;'>
            <h2>ลากรูปมาวางที่นี่</h2>
            <p>รองรับหลายไฟล์ • ดาวน์โหลดเป็น ZIP • ฟรี 100%</p>
        </div>
        """, unsafe_allow_html=True
    )

# Footer
st.markdown("---")
st.caption("AI ฟรี | ทำด้วย Streamlit + rembg | รองรับงานหนัก 100+ ภาพ")
