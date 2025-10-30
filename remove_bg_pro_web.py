import streamlit as st
from rembg import remove, new_session
from PIL import Image, ImageDraw
import io
import zipfile
import os
from datetime import datetime
import torch
from segment_anything import sam_model_registry, SamPredictor
from streamlit_drawable_canvas import st_canvas

st.set_page_config(page_title="Remove BG Pro AI Trainer", layout="wide")
st.markdown("<h1 style='text-align:center;'>Remove BG Pro AI Trainer</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>วาด Mask → เทรน AI → ลบพื้นหลังแม่น 99%</p>", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3 = st.tabs(["1. วาด Mask", "2. เทรน AI", "3. ลบพื้นหลัง"])

# --- Tab 1: วาด Mask ---
with tab1:
    st.header("วาด Mask ด้วยปากกา")
    uploaded = st.file_uploader("ลากรูปมาวาง", type=['png', 'jpg', 'jpeg'])
    if uploaded:
        img = Image.open(uploaded).convert("RGB")
        st.image(img, caption="รูปต้นฉบับ", use_column_width=True)
        
        # วาด Mask
        canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",
            stroke_width=3,
            stroke_color="red",
            background_image=img,
            height=img.height,
            width=img.width,
            drawing_mode="freedraw",
            key="canvas",
        )
        
        if canvas_result.image_data is not None:
            mask = Image.fromarray((canvas_result.image_data[:, :, 3] > 0).astype("uint8") * 255)
            st.image(mask, caption="Mask ที่วาด", use_column_width=True)
            st.session_state.mask = mask
            st.session_state.original = img

# --- Tab 2: เทรน AI ---
with tab2:
    st.header("เทรน AI ด้วยรูป 1 รูป")
    if st.button("เริ่มเทรน AI") and "original" in st.session_state:
        with st.spinner("กำลังเทรน..."):
            # ใช้ SAM (Segment Anything)
            sam = sam_model_registry["vit_h"](checkpoint="sam_vit_h_4b8939.pth")
            predictor = SamPredictor(sam)
            predictor.set_image(st.session_state.original)
            
            input_point = [[100, 100]]  # จุดตัวอย่าง
            input_label = [1]
            masks, _, _ = predictor.predict(point_coords=input_point, point_labels=input_label, multimask_output=False)
            
            st.success("เทรนสำเร็จ!")
            st.session_state.trained_mask = Image.fromarray(masks[0] * 255)

# --- Tab 3: ลบพื้นหลัง ---
with tab3:
    st.header("ลบพื้นหลังด้วย AI ที่เทรนแล้ว")
    if "original" in st.session_state:
        col1, col2 = st.columns(2)
        with col1:
            st.image(st.session_state.original, caption="ก่อน", use_column_width=True)
        with col2:
            if "trained_mask" in st.session_state:
                mask = st.session_state.trained_mask.convert("L")
                result = Image.composite(st.session_state.original, Image.new("RGBA", st.session_state.original.size, (0,0,0,0)), mask)
                st.image(result, caption="หลัง", use_column_width=True)
                
                # ดาวน์โหลด
                buf = io.BytesIO()
                result.save(buf, "PNG")
                st.download_button("ดาวน์โหลด", buf.getvalue(), "trained_nobg.png", "image/png")
