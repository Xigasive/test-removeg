import streamlit as st
import requests
from PIL import Image
import io
import zipfile
from datetime import datetime

# API Keys จาก Secrets
REMOVE_BG_API_KEY = st.secrets.get("REMOVE_BG_API_KEY", "H9Q5FFUH7euSM5xs5QBSneVM")
DEEP_AI_API_KEY = st.secrets.get("DEEP_AI_API_KEY", "")

st.set_page_config(page_title="Remove And Gen by ไมค์โค้ดเถื่อน", layout="wide")
st.markdown("<h1 style='text-align:center;'>✂️ Remove BG Pro+ | AI Gen</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>ลบพื้นหลังแม่นยำ + สร้างภาพจาก Prompt ฟรี</p>", unsafe_allow_html=True)

# Tabs
tab1, tab2 = st.tabs(["ลบพื้นหลัง", "สร้างภาพ AI"])

with tab1:
    st.header("ลบพื้นหลังด้วย remove.bg API")
    
    # อัปโหลด
    uploaded_files = st.file_uploader("ลากรูปมาวาง (หลายไฟล์)", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
    
    if uploaded_files and REMOVE_BG_API_KEY:
        total = len(uploaded_files)
        progress = st.progress(0)
        results = []
        
        for i, file in enumerate(uploaded_files):
            # Preview ก่อน
            col1, col2 = st.columns(2)
            with col1:
                original = Image.open(file)
                st.image(original, caption=f"ก่อน: {file.name}", use_column_width=True)
            
            # ลบ BG ด้วย API
            with st.spinner(f"กำลังลบพื้นหลัง {file.name}..."):
                response = requests.post(
                    'https://api.remove.bg/v1.0/removebg',
                    files={'image_file': file},
                    data={'size': 'auto'},
                    headers={'X-Api-Key': REMOVE_BG_API_KEY},
                )
            
            if response.status_code == 200:
                output = Image.open(io.BytesIO(response.content))
                with col2:
                    st.image(output, caption=f"หลัง: {file.name}", use_column_width=True)
                
                # บันทึก
                buf = io.BytesIO()
                output.save(buf, "PNG")
                results.append((f"{os.path.splitext(file.name)[0]}_nobg.png", buf.getvalue()))
            else:
                st.error(f"Error: {response.status_code} - เช็ค API Key")
            
            progress.progress((i + 1) / total)
        
        # ดาวน์โหลด
        if results:
            zip_buf = io.BytesIO()
            with zipfile.ZipFile(zip_buf, "w") as z:
                for name, data in results:
                    z.writestr(name, data)
            zip_buf.seek(0)
            st.success("เสร็จสิ้น!")
            st.download_button("ดาวน์โหลด ZIP", zip_buf, f"nobg_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip", "application/zip")
    elif not REMOVE_BG_API_KEY:
        st.warning("กรุณาใส่ REMOVE_BG_API_KEY ใน Secrets (สมัครฟรีที่ remove.bg/api)")
    else:
        st.info("ลากรูปมาวางที่นี่")

with tab2:
    st.header("สร้างภาพจาก Prompt ด้วย DeepAI API")
    
    prompt = st.text_input("พิมพ์ Prompt (เช่น 'กลองชุดไฟฟ้าสีแดงในสตูดิโอ')", placeholder="อธิบายภาพที่ต้องการ...")
    num_images = st.slider("จำนวนภาพ", 1, 5, 1)
    
    if st.button("สร้างภาพ") and prompt and DEEP_AI_API_KEY:
        with st.spinner("กำลังสร้างภาพ..."):
            response = requests.post(
                'https://api.deepai.org/api/text2img',
                data={'text': prompt},
                headers={'api-key': DEEP_AI_API_KEY},
            )
        
        if response.status_code == 200:
            result = response.json()
            image_url = result['output_url']
            
            # แสดงภาพ
            st.image(image_url, caption=f"ภาพจาก Prompt: {prompt}")
            
            # ดาวน์โหลด
            img_response = requests.get(image_url)
            buf = io.BytesIO(img_response.content)
            st.download_button("ดาวน์โหลดภาพ", buf.getvalue(), f"gen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg", "image/jpeg")
        else:
            st.error(f"Error: {response.status_code} - เช็ค API Key")
    elif not DEEP_AI_API_KEY:
        st.warning("กรุณาใส่ DEEP_AI_API_KEY ใน Secrets (สมัครฟรีที่ deepai.org)")
    else:
        st.info("พิมพ์ Prompt แล้วกดสร้างภาพ")

st.markdown("---")
st.caption("API ฟรี: remove.bg (50 ภาพ/เดือน) | DeepAI (5 ภาพ/วัน) | ทำด้วย Streamlit")
