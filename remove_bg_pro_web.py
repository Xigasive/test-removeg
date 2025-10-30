import streamlit as st
from rembg import remove
from PIL import Image, ImageOps
import io
import zipfile
import os
from datetime import datetime

st.set_page_config(page_title="ลบพื้นหลังโดย ไมค์โค้ดเถื่อน", layout="wide")
st.markdown("<h1 style='text-align:center;'>Remove BG Pro+</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>ลบพื้นหลัง + เลือกพื้นหลังใหม่</p>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("พื้นหลัง")
    bg_option = st.radio("เลือกพื้นหลัง", ["โปร่งใส", "สี", "รูปภาพ"])
    
    bg_color = "#FFFFFF"
    if bg_option == "สี":
        bg_color = st.color_picker("เลือกสี", "#FFFFFF")
    
    bg_image = None
    if bg_option == "รูปภาพ":
        bg_upload = st.file_uploader("ลากรูปพื้นหลัง", type=['png', 'jpg', 'jpeg'])
        if bg_upload:
            bg_image = Image.open(bg_upload).convert("RGBA")

# อัปโหลดภาพ
uploaded_files = st.file_uploader("ลากรูปมาวางที่นี่ (หลายไฟล์)", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

if uploaded_files:
    total = len(uploaded_files)
    progress = st.progress(0)
    results = []

    for i, file in enumerate(uploaded_files):
        with st.container():
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**ก่อน:** {file.name}")
                original = Image.open(file).convert("RGBA")
                st.image(original, use_column_width=True)
            
            # ลบพื้นหลัง
            no_bg = remove(original)
            
            # สร้างพื้นหลังใหม่
            if bg_option == "โปร่งใส":
                final = no_bg
            elif bg_option == "สี":
                bg = Image.new("RGBA", no_bg.size, bg_color + "FF")
                final = Image.alpha_composite(bg, no_bg)
            else:  # รูปภาพ
                if bg_image:
                    bg_resized = bg_image.resize(no_bg.size)
                    final = Image.alpha_composite(bg_resized, no_bg)
                else:
                    final = no_bg
            
            with col2:
                st.write(f"**หลัง:** {file.name}")
                st.image(final, use_column_width=True)
            
            # บันทึก
            buf = io.BytesIO()
            final.save(buf, "PNG")
            results.append((f"{os.path.splitext(file.name)[0]}_final.png", buf.getvalue()))
        
        progress.progress((i + 1) / total)

    # ดาวน์โหลด
    if results:
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w") as z:
            for name, data in results:
                z.writestr(name, data)
        zip_buf.seek(0)
        
        st.success("เสร็จสิ้น!")
        st.download_button(
            "ดาวน์โหลดทั้งหมด (ZIP)",
            zip_buf,
            f"bg_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
            "application/zip"
        )
else:
    st.info("ลากรูปมาวางที่นี่")
