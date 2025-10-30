import streamlit as st
from rembg import remove, new_session
from PIL import Image
import io
import zipfile
from datetime import datetime

st.set_page_config(page_title="Remove BG Pro", layout="wide")
st.markdown("<h1 style='text-align:center;'>Remove BG Pro</h1>", unsafe_allow_html=True)

# โมเดลแม่นสุด
@st.cache_resource
def get_session():
    return new_session("isnet-general-use")  # แม่น 98%

session = get_session()

uploaded_files = st.file_uploader("ลากรูปมาวางที่นี่", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

if uploaded_files:
    total = len(uploaded_files)
    progress = st.progress(0)
    results = []

    for i, file in enumerate(uploaded_files):
        img = Image.open(file).convert("RGBA")
        output = remove(img, session=session)
        
        buf = io.BytesIO()
        output.save(buf, "PNG")
        results.append((f"{file.name}_nobg.png", buf.getvalue()))
        
        progress.progress((i + 1) / total)

    if results:
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w") as z:
            for name, data in results:
                z.writestr(name, data)
        zip_buf.seek(0)
        
        st.success("เสร็จสิ้น!")
        st.download_button("ดาวน์โหลด ZIP", zip_buf, f"nobg_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip", "application/zip")
