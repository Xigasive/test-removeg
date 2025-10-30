import streamlit as st
from rembg import remove
from PIL import Image
import io
import zipfile
import os
from datetime import datetime

st.set_page_config(page_title="Remove BG Pro", layout="wide")
st.markdown("<h1 style='text-align:center;'>Remove BG Pro</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>ลบพื้นหลังฟรี – เร็ว แม่น งานหนักได้</p>", unsafe_allow_html=True)

uploaded_files = st.file_uploader("ลากรูปมาวางที่นี่", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

if uploaded_files:
    total = len(uploaded_files)
    progress = st.progress(0)
    results = []

    for i, file in enumerate(uploaded_files):
        st.write(f"กำลังประมวลผล: {file.name}")
        img = Image.open(file).convert("RGBA")
        output = remove(img)  # ใช้ remove ธรรมดา
        
        buf = io.BytesIO()
        output.save(buf, "PNG")
        results.append((f"{os.path.splitext(file.name)[0]}_nobg.png", buf.getvalue()))
        
        progress.progress((i + 1) / total)

    if results:
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w") as z:
            for name, data in results:
                z.writestr(name, data)
        zip_buf.seek(0)
        
        st.success("เสร็จสิ้น!")
        st.download_button("ดาวน์โหลดทั้งหมด (ZIP)", zip_buf, f"nobg_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip", "application/zip")
else:
    st.info("ลากรูปมาวางที่นี่")
