# app.py - 骏泰素材工作台
import zipfile
from io import BytesIO
import streamlit as st
import os
import math
from PIL import Image, ImageDraw
import tempfile
import random
import base64
import cv2
import numpy as np
from moviepy.editor import VideoFileClip, AudioFileClip
import requests

# 设置页面配置
st.set_page_config(
    page_title="骏泰素材工作台",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

def get_custom_css():
    return """
    <style>
        /* ===== 设计系统变量 ===== */
        :root {
            --primary: #2563EB;
            --primary-light: #3B82F6;
            --primary-dark: #1D4ED8;
            --primary-muted: #EFF6FF;
            --accent: #06B6D4;
            --success: #10B981;
            --warning: #F59E0B;
            --danger: #EF4444;
            --surface: #FFFFFF;
            --surface-2: #F8FAFC;
            --surface-3: #F1F5F9;
            --border: #E2E8F0;
            --border-strong: #CBD5E1;
            --text-primary: #0F172A;
            --text-secondary: #475569;
            --text-muted: #94A3B8;
            --sidebar-bg: #0F172A;
            --sidebar-text: #CBD5E1;
            --sidebar-accent: #3B82F6;
            --radius-sm: 6px;
            --radius-md: 10px;
            --radius-lg: 16px;
            --shadow-sm: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.04);
            --shadow-md: 0 4px 12px rgba(0,0,0,0.08), 0 2px 4px rgba(0,0,0,0.04);
            --shadow-lg: 0 10px 30px rgba(0,0,0,0.1), 0 4px 8px rgba(0,0,0,0.04);
        }

        /* ===== 全局字体 ===== */
        * { font-family: 'PingFang SC', 'Microsoft YaHei', 'Segoe UI', sans-serif !important; }
        .stApp { background: var(--surface-2) !important; }

        /* ===== 主标题 ===== */
        .main-header {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--text-primary);
            letter-spacing: -0.02em;
            padding: 0.25rem 0 0.5rem 0;
            margin: 0 !important;
        }

        /* ===== 侧边栏 ===== */
        section[data-testid="stSidebar"] {
            min-width: 260px !important;
            max-width: 280px !important;
            background: var(--sidebar-bg) !important;
        }
        section[data-testid="stSidebar"] > div:first-child {
            padding: 1.5rem 1rem !important;
        }
        section[data-testid="stSidebar"] * {
            color: var(--sidebar-text) !important;
        }
        section[data-testid="stSidebar"] h3 {
            color: #F8FAFC !important;
            font-size: 0.8rem !important;
            font-weight: 700 !important;
            letter-spacing: 0.1em !important;
            text-transform: uppercase !important;
            margin-bottom: 1rem !important;
        }
        section[data-testid="stSidebar"] hr {
            border-color: #1E293B !important;
            margin: 1.25rem 0 !important;
        }
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] .stRadio label,
        section[data-testid="stSidebar"] .stSlider label,
        section[data-testid="stSidebar"] .stSelectbox label {
            color: #94A3B8 !important;
            font-size: 0.78rem !important;
            font-weight: 600 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.05em !important;
        }
        section[data-testid="stSidebar"] .stSlider > div > div > div {
            background: var(--sidebar-accent) !important;
        }
        /* 侧边栏复选框 */
        section[data-testid="stSidebar"] .stCheckbox label {
            color: var(--sidebar-text) !important;
            text-transform: none !important;
            letter-spacing: 0 !important;
            font-size: 0.9rem !important;
            font-weight: 500 !important;
        }

        /* ===== 侧边栏按钮 ===== */
        section[data-testid="stSidebar"] .stButton > button {
            background: var(--primary) !important;
            color: white !important;
            border: none !important;
            border-radius: var(--radius-md) !important;
            font-weight: 600 !important;
            font-size: 0.9rem !important;
            padding: 0.65rem 1rem !important;
            width: 100% !important;
            transition: all 0.2s !important;
            letter-spacing: 0.01em !important;
        }
        section[data-testid="stSidebar"] .stButton > button:hover {
            background: var(--primary-dark) !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.35) !important;
        }
        section[data-testid="stSidebar"] .stDownloadButton > button {
            background: #1E293B !important;
            color: var(--sidebar-text) !important;
            border: 1px solid #334155 !important;
            border-radius: var(--radius-md) !important;
            font-weight: 500 !important;
            font-size: 0.85rem !important;
            padding: 0.6rem 1rem !important;
            width: 100% !important;
            transition: all 0.2s !important;
        }
        section[data-testid="stSidebar"] .stDownloadButton > button:hover {
            background: #263548 !important;
            border-color: var(--sidebar-accent) !important;
        }

        /* ===== 标签页 ===== */
        .stTabs [data-baseweb="tab-list"] {
            gap: 4px !important;
            background: var(--surface-3) !important;
            padding: 4px !important;
            border-radius: var(--radius-md) !important;
            border: none !important;
            margin-bottom: 1.5rem !important;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 8px 18px !important;
            border-radius: var(--radius-sm) !important;
            font-weight: 600 !important;
            font-size: 0.875rem !important;
            color: var(--text-secondary) !important;
            background: transparent !important;
            border: none !important;
            transition: all 0.15s !important;
        }
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background: white !important;
            color: var(--primary) !important;
            box-shadow: var(--shadow-sm) !important;
        }
        .stTabs [data-baseweb="tab-highlight"] { display: none !important; }
        .stTabs [data-baseweb="tab-border"] { display: none !important; }

        /* ===== 主区域按钮 ===== */
        .stButton > button {
            border-radius: var(--radius-md) !important;
            font-weight: 600 !important;
            font-size: 0.875rem !important;
            padding: 0.55rem 1.1rem !important;
            transition: all 0.2s !important;
            border: 1px solid var(--border-strong) !important;
            background: white !important;
            color: var(--text-primary) !important;
        }
        .stButton > button:hover {
            border-color: var(--primary) !important;
            color: var(--primary) !important;
            box-shadow: var(--shadow-sm) !important;
            transform: translateY(-1px) !important;
        }
        .stButton > button[kind="primary"] {
            background: var(--primary) !important;
            color: white !important;
            border-color: var(--primary) !important;
        }
        .stButton > button[kind="primary"]:hover {
            background: var(--primary-dark) !important;
            border-color: var(--primary-dark) !important;
            color: white !important;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
        }
        .stButton > button[kind="secondary"] {
            background: white !important;
            color: var(--text-secondary) !important;
            border-color: var(--border) !important;
        }
        .stButton > button[kind="secondary"]:hover {
            border-color: var(--primary) !important;
            color: var(--primary) !important;
        }
        .stButton > button:disabled {
            opacity: 0.4 !important;
            cursor: not-allowed !important;
            transform: none !important;
        }

        /* ===== 下载按钮 ===== */
        .stDownloadButton > button {
            border-radius: var(--radius-md) !important;
            font-weight: 600 !important;
            background: var(--success) !important;
            color: white !important;
            border: none !important;
            padding: 0.6rem 1.2rem !important;
            transition: all 0.2s !important;
        }
        .stDownloadButton > button:hover {
            background: #059669 !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3) !important;
        }

        /* ===== 提示框重设计 ===== */
        .stSuccess, .stAlert [data-testid="stNotification"][data-type="success"] {
            background: #ECFDF5 !important;
            border: 1px solid #A7F3D0 !important;
            border-radius: var(--radius-md) !important;
            color: #065F46 !important;
        }
        .stInfo, .stAlert [data-testid="stNotification"][data-type="info"] {
            background: var(--primary-muted) !important;
            border: 1px solid #BFDBFE !important;
            border-radius: var(--radius-md) !important;
            color: #1E40AF !important;
        }
        .stWarning {
            background: #FFFBEB !important;
            border: 1px solid #FDE68A !important;
            border-radius: var(--radius-md) !important;
        }
        .stError {
            background: #FEF2F2 !important;
            border: 1px solid #FECACA !important;
            border-radius: var(--radius-md) !important;
        }

        /* ===== 表单元素 ===== */
        .stTextInput > div > div > input,
        .stSelectbox > div > div {
            border-radius: var(--radius-sm) !important;
            border: 1px solid var(--border) !important;
            font-size: 0.9rem !important;
            background: white !important;
        }
        .stTextInput > div > div > input:focus {
            border-color: var(--primary) !important;
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
        }
        .stSelectbox > div > div:hover {
            border-color: var(--primary-light) !important;
        }

        /* ===== 文件上传组件 ===== */
        [data-testid="stFileUploader"] {
            border: 2px dashed var(--border-strong) !important;
            border-radius: var(--radius-md) !important;
            background: var(--surface-2) !important;
            transition: border-color 0.2s !important;
        }
        [data-testid="stFileUploader"]:hover {
            border-color: var(--primary) !important;
            background: var(--primary-muted) !important;
        }
        /* ===== 中文化上传提示 ===== */
        [data-testid="stFileUploaderDropzone"] {
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;
            min-height: 90px !important;
            padding: 1.25rem !important;
        }
        [data-testid="stFileUploaderDropzone"] > div {
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            gap: 6px !important;
            width: 100% !important;
        }
        [data-testid="stFileUploaderDropzone"] span,
        [data-testid="stFileUploaderDropzone"] p,
        [data-testid="stFileUploaderDropzone"] small {
            display: none !important;
        }
        [data-testid="stFileUploaderDropzone"] button {
            font-size: 0 !important;
            margin: 0 auto !important;
        }
        [data-testid="stFileUploaderDropzone"] button span {
            font-size: 0 !important;
        }
        [data-testid="stFileUploaderDropzone"] button::after {
            content: "选择文件" !important;
            font-size: 14px !important;
            font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif !important;
        }

        /* ===== 进度条 ===== */
        .stProgress > div > div {
            background: linear-gradient(90deg, var(--primary), var(--accent)) !important;
            border-radius: 99px !important;
        }

        /* ===== 自定义组件：页面标题卡片 ===== */
        .page-section-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 1rem;
        }
        .page-section-header h2 {
            font-size: 1.2rem;
            font-weight: 700;
            color: var(--text-primary);
            margin: 0;
        }

        /* ===== 信息横幅 ===== */
        .info-banner {
            background: var(--primary-muted);
            border: 1px solid #BFDBFE;
            border-radius: var(--radius-md);
            padding: 0.85rem 1.1rem;
            font-size: 0.875rem;
            color: #1E40AF;
            margin-bottom: 1.25rem;
            line-height: 1.5;
        }

        /* ===== 视频信息卡片 ===== */
        .info-card {
            background: white;
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            padding: 1rem 1.1rem;
            margin-bottom: 1rem;
            box-shadow: var(--shadow-sm);
        }
        .info-card-title {
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            color: var(--text-muted);
            margin-bottom: 0.6rem;
        }
        .info-card-body {
            font-size: 0.875rem;
            color: var(--text-secondary);
            line-height: 1.75;
        }
        .info-card-body strong {
            color: var(--text-primary);
            font-weight: 600;
        }

        /* ===== 遮罩信息 ===== */
        .mask-info {
            background: #F0FDF4;
            border: 1px solid #BBF7D0;
            border-radius: var(--radius-sm);
            padding: 0.7rem 0.9rem;
            font-size: 0.82rem;
            color: #166534;
            margin-top: 0.75rem;
            line-height: 1.6;
        }

        /* ===== 颜色预览框 ===== */
        .color-preview-box {
            width: 36px;
            height: 36px;
            border-radius: var(--radius-sm);
            border: 1px solid var(--border);
            margin: 0 auto;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 11px;
            font-weight: 700;
        }

        /* ===== Unsplash 图片网格 ===== */
        .unsplash-square-container {
            width: 100%;
            aspect-ratio: 1/1;
            overflow: hidden;
            border-radius: var(--radius-sm);
            margin-bottom: 6px;
            border: 2px solid transparent;
            background: var(--surface-3);
            transition: border-color 0.15s;
        }
        .unsplash-square-container:hover {
            border-color: var(--primary-light);
        }
        .unsplash-square-image {
            position: absolute;
            top: 0; left: 0;
            width: 100%; height: 100%;
            object-fit: cover;
            object-position: center;
            display: block;
            margin: 0; padding: 0; border: none;
        }
        .unsplash-square-container { position: relative; }

        /* ===== Logo水印容器 ===== */
        .logo-adder-preview-placeholder {
            background: var(--surface-3);
            border: 2px dashed var(--border-strong);
            border-radius: var(--radius-lg);
            padding: 3rem;
            text-align: center;
            color: var(--text-muted);
        }
        .logo-adder-preview-placeholder h4 {
            color: var(--text-secondary);
            margin-bottom: 0.5rem;
        }

        /* ===== 合成状态统计 ===== */
        .synth-stat {
            background: white;
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            padding: 0.9rem 1.1rem;
            text-align: center;
            box-shadow: var(--shadow-sm);
        }
        .synth-stat-num {
            font-size: 1.6rem;
            font-weight: 800;
            color: var(--primary);
            line-height: 1.2;
        }
        .synth-stat-label {
            font-size: 0.78rem;
            color: var(--text-muted);
            margin-top: 2px;
        }

        /* ===== 侧边栏设置小标题 ===== */
        .sidebar-section-title {
            font-size: 0.72rem !important;
            font-weight: 700 !important;
            letter-spacing: 0.08em !important;
            text-transform: uppercase !important;
            color: #64748B !important;
            margin: 0 0 0.5rem 0 !important;
            display: block;
        }

        /* ===== 选择状态徽标 ===== */
        .selected-badge {
            display: inline-block;
            background: var(--success);
            color: white;
            border-radius: 99px;
            padding: 2px 8px;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.03em;
        }

        /* ===== 响应式 ===== */
        @media (min-width: 1920px) {
            .stTabs [data-baseweb="tab"] { padding: 10px 22px !important; font-size: 0.95rem !important; }
            .main-header { font-size: 1.75rem; }
        }
    </style>
    """

st.markdown(get_custom_css(), unsafe_allow_html=True)

# 页面标题
st.markdown('<h1 class="main-header">🎨 骏泰素材工作台</h1>', unsafe_allow_html=True)

# ==================== 初始化会话状态 ====================
_defaults = {
    'current_page': 0,
    'processed_images': [],
    'last_zip_buffer': None,
    'processed_video': None,
    'video_info': None,
    'unsplash_photos': [],
    'unsplash_selected_bg': None,
    'unsplash_search_query': "white background",
    'unsplash_search_trigger': False,
    'unsplash_current_page': 1,
    'unsplash_total_pages': 0,
    'unsplash_selected_page': 1,
    'unsplash_selected_idx': -1,
    'synthesize_zip_buffer': None,
    'synthesize_zip_info': {},
    'persist_product_files': [],
    'unsplash_total_results': 0,
    'logo_adder_images': [],
    'logo_adder_logo_color': "黑色Logo",
    'logo_adder_logo_opacity': 180,
    'logo_adder_logo_size': 100,
    'logo_adder_logo_x': 50,
    'logo_adder_logo_y': 50,
    'logo_adder_logo_image': None,
    'logo_adder_processed_images': [],
    'logo_adder_last_zip_buffer': None,
    'logo_adder_preset_position': "自定义",
    'dark_mask_enabled': False,
    'mask_opacity': 20,
    'mask_color_type': "预设颜色",
    'mask_preset_color': "白色",
    'mask_custom_color': "#FFFFFF",
    'mask_color_rgb': (255, 255, 255),
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# 预设颜色选项
PRESET_COLORS = {
    "白色": "#FFFFFF", "黑色": "#000000", "深灰": "#333333", "浅灰": "#CCCCCC",
    "深蓝": "#003366", "蓝色": "#0066CC", "深绿": "#006633", "浅绿": "#66CC99",
    "深红": "#990000", "红色": "#CC3333", "深紫": "#663366", "紫色": "#9966CC",
    "金色": "#FFD700", "橙色": "#FF9900", "棕色": "#996633"
}

# ==================== Unsplash API ====================
class UnsplashAPI:
    def __init__(self):
        try:
            self.access_key = st.secrets["UNSPLASH_ACCESS_KEY"]
        except:
            self.access_key = ""
        self.base_url = "https://api.unsplash.com"

    def search_photos(self, query, page=1, per_page=12):
        if not self.access_key:
            return [], 0, 0
        url = f"{self.base_url}/search/photos"
        headers = {"Authorization": f"Client-ID {self.access_key}"}
        params = {"query": query, "page": page, "per_page": per_page, "orientation": "squarish"}
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                total = data.get("total", 0)
                total_pages = data.get("total_pages", 0)
                if total_pages == 0 and total > 0:
                    total_pages = (total + per_page - 1) // per_page
                total_pages = min(total_pages, 1000)
                return data.get("results", []), total_pages, total
            elif response.status_code == 401:
                st.error("Unsplash API 密钥无效")
                return [], 0, 0
            else:
                st.error(f"Unsplash API 错误: {response.status_code}")
                return [], 0, 0
        except Exception as e:
            st.error(f"请求失败: {e}")
            return [], 0, 0

    def download_photo(self, photo_url):
        try:
            response = requests.get(photo_url, timeout=10)
            if response.status_code == 200:
                return Image.open(BytesIO(response.content))
        except Exception as e:
            st.error(f"下载失败: {e}")
        return None

# ==================== 颜色辅助函数 ====================
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(*rgb)

def get_color_brightness(rgb):
    r, g, b = rgb
    return (r * 299 + g * 587 + b * 114) / 1000

def get_current_mask_color():
    if st.session_state.mask_color_type == "预设颜色":
        return hex_to_rgb(PRESET_COLORS[st.session_state.mask_preset_color])
    else:
        return hex_to_rgb(st.session_state.mask_custom_color)

# ==================== 核心图像处理函数 ====================
def compose_image(bg_img, product_img, logo_img, product_size, output_size, output_format,
                  mask_enabled=False, mask_color=(255, 255, 255), mask_opacity=20):
    bg = bg_img.convert('RGBA')
    bg_ratio = output_size / min(bg.width, bg.height)
    new_w = int(bg.width * bg_ratio)
    new_h = int(bg.height * bg_ratio)
    bg = bg.resize((new_w, new_h), Image.Resampling.LANCZOS)
    left = (bg.width - output_size) // 2
    top = (bg.height - output_size) // 2
    bg = bg.crop((left, top, left + output_size, top + output_size))

    if mask_enabled and mask_opacity > 0:
        r, g, b = mask_color
        color_layer = Image.new('RGBA', bg.size, (r, g, b, int(mask_opacity * 255 / 100)))
        bg = Image.alpha_composite(bg, color_layer)

    product = product_img.convert('RGBA')
    product.thumbnail((product_size, product_size), Image.Resampling.LANCZOS)
    px = (output_size - product.width) // 2
    py = (output_size - product.height) // 2
    bg.paste(product, (px, py), product)

    if logo_img:
        logo = logo_img.convert('RGBA')
        if logo.size != (output_size, output_size):
            logo = logo.resize((output_size, output_size), Image.Resampling.LANCZOS)
        bg = Image.alpha_composite(bg, logo)

    if output_format.upper() == 'JPG':
        rgb = Image.new('RGB', bg.size, (255, 255, 255))
        rgb.paste(bg, mask=bg.split()[3])
        return rgb
    return bg

def remove_random_frames(input_video_path, output_video_path, progress_bar=None, status_text=None):
    if not os.path.exists(input_video_path):
        raise FileNotFoundError(f"找不到视频文件")
    cap = cv2.VideoCapture(input_video_path)
    if not cap.isOpened():
        raise ValueError("无法打开视频文件")
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = total_frames / fps
    video_info = {"total_frames": total_frames, "fps": fps, "width": width, "height": height, "duration": duration}
    if total_frames <= 2:
        cap.release()
        raise ValueError("视频太短，不足以移除两帧")
    available = list(range(1, total_frames - 1))
    frames_to_remove = sorted(random.sample(available, 2) if len(available) >= 2 else random.sample(range(total_frames), min(2, total_frames)))
    if status_text:
        status_text.text(f"将删除第 {frames_to_remove[0]} 帧和第 {frames_to_remove[1]} 帧")
    try:
        video_clip = VideoFileClip(input_video_path)
        audio = video_clip.audio
        has_audio = audio is not None
        temp_audio_path = "temp_audio.wav"
        if has_audio:
            audio.write_audiofile(temp_audio_path, verbose=False, logger=None)
        video_clip.close()
    except Exception as e:
        has_audio = False
    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    out = cv2.VideoWriter('temp_video_noaudio.mp4', fourcc, fps, (width, height))
    frame_index = 0
    saved_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_index not in frames_to_remove:
            out.write(frame)
            saved_count += 1
        frame_index += 1
        if progress_bar and total_frames > 0:
            progress_bar.progress(frame_index / total_frames)
    cap.release()
    out.release()
    if has_audio:
        if status_text:
            status_text.text("正在合并音频...")
        try:
            vnoa = VideoFileClip('temp_video_noaudio.mp4')
            final_clip = vnoa.set_audio(AudioFileClip(temp_audio_path))
            final_clip.write_videofile(output_video_path, codec='libx264', audio_codec='aac', verbose=False, logger=None)
            vnoa.close(); final_clip.close()
            for f in ['temp_video_noaudio.mp4', temp_audio_path]:
                if os.path.exists(f): os.remove(f)
        except Exception as e:
            if os.path.exists('temp_video_noaudio.mp4'):
                os.rename('temp_video_noaudio.mp4', output_video_path)
    else:
        if os.path.exists('temp_video_noaudio.mp4'):
            os.rename('temp_video_noaudio.mp4', output_video_path)
    return output_video_path, video_info, frames_to_remove, saved_count

def add_logo_to_image(base_image, logo_image, x_percent, y_percent, size_percent, opacity):
    try:
        base_img = base_image.copy().convert('RGBA')
        logo_img = logo_image.copy().convert('RGBA')
        bw, bh = base_img.size
        logo_size = int(min(bw, bh) * (size_percent / 100))
        logo_img.thumbnail((logo_size, logo_size), Image.Resampling.LANCZOS)
        if opacity < 255:
            alpha = logo_img.split()[3].point(lambda p: p * opacity // 255)
            logo_img.putalpha(alpha)
        lw, lh = logo_img.size
        x_pos = int((bw - lw) * (x_percent / 100))
        y_pos = int((bh - lh) * (y_percent / 100))
        layer = Image.new('RGBA', base_img.size, (0, 0, 0, 0))
        layer.paste(logo_img, (x_pos, y_pos), logo_img)
        return Image.alpha_composite(base_img, layer)
    except Exception as e:
        st.error(f"添加Logo时发生错误: {e}")
        return None

def create_zip_from_images(images, original_names, output_format='PNG'):
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for i, (img, name) in enumerate(zip(images, original_names)):
            buf = BytesIO()
            if output_format.upper() == 'JPG':
                if img.mode == 'RGBA':
                    rgb = Image.new('RGB', img.size, (255, 255, 255))
                    rgb.paste(img, mask=img.split()[3])
                    img = rgb
                img.save(buf, format='JPEG', quality=95)
                ext = '.jpg'
            else:
                img.save(buf, format='PNG')
                ext = '.png'
            buf.seek(0)
            stem = os.path.splitext(name)[0]
            zf.writestr(f"{stem}_with_logo_{i+1:03d}{ext}", buf.getvalue())
    zip_buffer.seek(0)
    return zip_buffer

# ==================== 侧边栏 ====================
with st.sidebar:
    st.markdown("### ⚙️ 合成设置")

    # Logo 选择
    st.markdown('<span class="sidebar-section-title">🖼 Logo 选择</span>', unsafe_allow_html=True)
    logo_color = st.radio("", ["黑色LOGO", "白色LOGO"], horizontal=True, key="logo_color_select")
    st.session_state.logo_color = logo_color

    st.markdown("---")

    # 产品图尺寸
    st.markdown('<span class="sidebar-section-title">📐 产品图最大边长</span>', unsafe_allow_html=True)
    product_size = st.slider("", min_value=500, max_value=1000, value=800, step=50, key="product_size_slider")
    st.session_state.product_size = product_size

    st.markdown("---")

    # 背景遮罩
    st.markdown('<span class="sidebar-section-title">🎨 背景遮罩</span>', unsafe_allow_html=True)
    dark_mask_enabled = st.checkbox("添加背景遮罩层", value=st.session_state.dark_mask_enabled, key='dark_mask_enabled_checkbox')
    st.session_state.dark_mask_enabled = dark_mask_enabled

    if dark_mask_enabled:
        mask_opacity = st.slider("不透明度", min_value=0, max_value=100,
                                  value=st.session_state.mask_opacity, step=5, key='mask_opacity_slider')
        st.session_state.mask_opacity = mask_opacity

        mask_color_type = st.radio("颜色来源", ["预设颜色", "自定义颜色"], horizontal=True,
                                    index=0 if st.session_state.mask_color_type == '预设颜色' else 1,
                                    key='mask_color_type_radio')
        st.session_state.mask_color_type = mask_color_type

        if mask_color_type == "预设颜色":
            current_preset = st.session_state.mask_preset_color
            current_hex = PRESET_COLORS[current_preset]
            current_rgb = hex_to_rgb(current_hex)
            brightness = get_color_brightness(current_rgb)
            text_color = "white" if brightness < 128 else "black"
            col1, col2 = st.columns([1, 3])
            with col1:
                st.markdown(f'<div class="color-preview-box" style="background:{current_hex};color:{text_color};">{current_preset[0]}</div>', unsafe_allow_html=True)
            with col2:
                options = list(PRESET_COLORS.keys())
                sel = st.selectbox("", options, index=options.index(current_preset), key='mask_preset_select')
                if sel != current_preset:
                    st.session_state.mask_preset_color = sel
                    st.session_state.mask_color_rgb = hex_to_rgb(PRESET_COLORS[sel])
                    st.rerun()
        else:
            custom_color = st.color_picker("遮罩颜色", value=st.session_state.mask_custom_color, key='mask_custom_color_picker')
            if custom_color != st.session_state.mask_custom_color:
                st.session_state.mask_custom_color = custom_color
                st.session_state.mask_color_rgb = hex_to_rgb(custom_color)
                st.rerun()

        cur_rgb = get_current_mask_color()
        cur_hex = rgb_to_hex(cur_rgb)
        color_name = st.session_state.mask_preset_color if st.session_state.mask_color_type == '预设颜色' else '自定义'
        st.markdown(f'<div class="mask-info">颜色：{color_name} {cur_hex}<br>不透明度：{mask_opacity}%</div>', unsafe_allow_html=True)

    st.markdown("---")

    # 输出设置
    st.markdown('<span class="sidebar-section-title">📦 输出设置</span>', unsafe_allow_html=True)
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        output_size = st.selectbox("尺寸(px)", [400, 600, 800, 1000, 1200, 1500, 2000], index=2, key="output_size_select")
        st.session_state.output_size = output_size
    with col_s2:
        output_format = st.radio("格式", ['JPG', 'PNG'], horizontal=True, key="output_format_radio")
        st.session_state.output_format = output_format

    st.markdown("---")

    # 处理按钮
    process_button = st.button("🚀 开始批量合成", type="primary", use_container_width=True, key="process_button")

    # 下载按钮
    if (st.session_state.synthesize_zip_buffer is not None
            and st.session_state.synthesize_zip_buffer.getvalue()
            and st.session_state.synthesize_zip_info):
        zfmt = st.session_state.synthesize_zip_info.get("output_format", "PNG")
        zsz = st.session_state.synthesize_zip_info.get("output_size", "800")
        st.download_button(
            label="⬇ 下载合成结果 ZIP",
            data=st.session_state.synthesize_zip_buffer,
            file_name=f"合成结果_{zsz}px_{zfmt.lower()}.zip",
            mime="application/zip",
            use_container_width=True,
            key="download_synthesize_zip"
        )

# ==================== 标签页 ====================
tab1, tab2, tab3 = st.tabs(["📤  产品图合成", "🎬  视频抽帧", "🖼  Logo水印添加"])

# ========== Tab 1：产品图合成 ==========
with tab1:
    st.markdown("""
    <div class="info-banner">
      上传背景图（或从 Unsplash 搜索），再上传产品透明图，点击左侧 <strong>开始批量合成</strong>，即可批量生成带 Logo 的产品图。
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown("#### 背景图")
        bg_source = st.radio("", ["上传图片", "Unsplash 图库"], horizontal=True,
                              key="bg_source_radio", label_visibility="collapsed")

        if bg_source == "上传图片":
            bg_files = st.file_uploader(
                "背景图片", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True,
                key="bg_upload", label_visibility="collapsed"
            )
            if bg_files:
                st.success(f"已上传 {len(bg_files)} 张背景图")
                cols_per_row = min(4, len(bg_files))
                preview_count = min(12, len(bg_files))
                for i in range(0, preview_count, cols_per_row):
                    cols = st.columns(cols_per_row)
                    for j in range(cols_per_row):
                        idx = i + j
                        if idx < preview_count:
                            with cols[j]:
                                f = bg_files[idx]
                                img = Image.open(f)
                                st.image(img, caption=f.name[:12] + ("…" if len(f.name) > 12 else ""), width=140)

        else:  # Unsplash 图库
            unsplash_api = UnsplashAPI()
            current_page = st.session_state.unsplash_current_page
            total_pages = st.session_state.unsplash_total_pages
            has_photos = len(st.session_state.unsplash_photos) > 0
            search_query = st.session_state.unsplash_search_query

            if st.session_state.unsplash_search_trigger:
                if unsplash_api.access_key:
                    photos, new_total, total_results = unsplash_api.search_photos(search_query, page=current_page, per_page=12)
                    if photos:
                        st.session_state.unsplash_photos = photos
                        st.session_state.unsplash_total_pages = new_total
                        st.session_state.unsplash_total_results = total_results
                        total_pages = new_total
                        has_photos = True
                    elif total_results == 0:
                        st.warning(f'未找到与「{search_query}」相关的图片')
                    st.session_state.unsplash_search_trigger = False

            # 搜索栏
            sc1, sc2 = st.columns([3, 2])
            with sc1:
                search_query = st.text_input("", value=search_query, placeholder="英文关键词，如 white background",
                                              label_visibility="collapsed", key="unsplash_search_input")
            with sc2:
                b1, b2, b3 = st.columns(3)
                with b1:
                    search_btn = st.button("搜索", type="primary", key="search_unsplash", use_container_width=True)
                with b2:
                    prev_btn = st.button("◀ 上页", key="unsplash_prev", use_container_width=True,
                                         disabled=not has_photos or current_page <= 1)
                with b3:
                    next_btn = st.button("下页 ▶", key="unsplash_next", use_container_width=True,
                                         disabled=not has_photos or total_pages == 0 or current_page >= total_pages)

            if search_btn:
                st.session_state.unsplash_current_page = 1
                st.session_state.unsplash_search_query = search_query
                st.session_state.unsplash_search_trigger = True
                st.rerun()
            if prev_btn and has_photos and current_page > 1:
                st.session_state.unsplash_current_page -= 1
                st.session_state.unsplash_search_trigger = True
                st.rerun()
            if next_btn and has_photos and current_page < total_pages:
                st.session_state.unsplash_current_page += 1
                st.session_state.unsplash_search_trigger = True
                st.rerun()

            if not unsplash_api.access_key:
                st.warning("未配置 Unsplash API 密钥，请在 Streamlit Secrets 中设置 UNSPLASH_ACCESS_KEY")

            if st.session_state.unsplash_photos:
                total_res = st.session_state.unsplash_total_results
                st.caption(f"第 {current_page} / {total_pages} 页 · 共约 {total_res} 张")
                photos = st.session_state.unsplash_photos
                for row in range(2):
                    cols = st.columns(6)
                    for col in range(6):
                        idx = row * 6 + col
                        if idx < len(photos):
                            with cols[col]:
                                photo = photos[idx]
                                img_url = photo.get("urls", {}).get("small")
                                if img_url:
                                    is_sel = (st.session_state.unsplash_selected_page == current_page and
                                              st.session_state.unsplash_selected_idx == idx)
                                    st.markdown(f"""
                                    <div class="unsplash-square-container" style="{'border-color:#2563EB;' if is_sel else ''}">
                                        <img src="{img_url}" class="unsplash-square-image">
                                    </div>
                                    """, unsafe_allow_html=True)
                                    if st.button("✓ 已选" if is_sel else "选择", key=f"sel_{current_page}_{idx}",
                                                  use_container_width=True,
                                                  type="primary" if is_sel else "secondary"):
                                        st.session_state.unsplash_selected_page = current_page
                                        st.session_state.unsplash_selected_idx = idx
                                        img = unsplash_api.download_photo(img_url)
                                        if img:
                                            class MockFile:
                                                def __init__(self, img, idx, page):
                                                    self.name = f"unsplash_{page}_{idx}.jpg"
                                                    self.image = img
                                            st.session_state.unsplash_selected_bg = MockFile(img, idx, current_page)
                                        st.rerun()

    with col2:
        st.markdown("#### 产品图")
        st.radio("", ["上传图片"], horizontal=True, key="product_source_radio",
                  disabled=True, label_visibility="collapsed")
        uploaded_products = st.file_uploader(
            "产品图", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True,
            key="product_upload", label_visibility="collapsed"
        )
        if 'persist_product_files' not in st.session_state:
            st.session_state.persist_product_files = []
        if uploaded_products:
            st.session_state.persist_product_files = uploaded_products
        product_files = st.session_state.persist_product_files

        if product_files:
            cnt = len(product_files)
            st.success(f"已上传 {cnt} 张产品图")
            preview_n = min(6, cnt)
            cols = st.columns(preview_n, gap="small")
            for idx in range(preview_n):
                with cols[idx]:
                    f = product_files[idx]
                    img = Image.open(f)
                    st.image(img, caption=f.name[:10] + ("…" if len(f.name) > 10 else ""), width=110)

    # 合成统计提示
    bg_combined = []
    if 'bg_files' in locals() and bg_files:
        bg_combined.extend(bg_files)
    if st.session_state.unsplash_selected_bg:
        bg_combined.append(st.session_state.unsplash_selected_bg)

    if bg_combined and product_files:
        total_comb = len(bg_combined) * len(product_files)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f'<div class="synth-stat"><div class="synth-stat-num">{len(bg_combined)}</div><div class="synth-stat-label">背景图</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="synth-stat"><div class="synth-stat-num">{len(product_files)}</div><div class="synth-stat-label">产品图</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="synth-stat"><div class="synth-stat-num">{total_comb}</div><div class="synth-stat-label">将合成张数</div></div>', unsafe_allow_html=True)

    # 合成预览
    if "synthesize_preview_images" in st.session_state and st.session_state.synthesize_preview_images:
        st.markdown("---")
        st.markdown("#### 合成预览")
        preview_imgs = st.session_state.synthesize_preview_images
        total_p = len(preview_imgs)
        show_n = min(10, total_p)
        if total_p > show_n:
            st.caption(f"共生成 {total_p} 张，显示前 {show_n} 张 · 完整结果请下载 ZIP")
        cols = st.columns(show_n, gap="small")
        for idx in range(show_n):
            with cols[idx]:
                d = preview_imgs[idx]
                img = Image.open(d["data"])
                st.image(img, caption=d["filename"][:10] + "…", width=110)
    elif st.session_state.synthesize_zip_buffer is not None:
        st.success("✅ 合成完成！请在左侧点击下载 ZIP 包。")

# ========== Tab 2：视频抽帧 ==========
with tab2:
    st.markdown("""
    <div class="info-banner">
      随机删除视频中的两帧，生成内容相似但数据不同的新视频，可用于规避平台重复检测。
    </div>
    """, unsafe_allow_html=True)

    col_l, col_r = st.columns([1, 1], gap="large")

    with col_l:
        st.markdown("#### 上传视频")
        video_file = st.file_uploader(
            "视频文件", type=['mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv'],
            key="video_uploader", label_visibility="collapsed"
        )
        if video_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp:
                tmp.write(video_file.getvalue())
                temp_video_path = tmp.name
            try:
                cap = cv2.VideoCapture(temp_video_path)
                if cap.isOpened():
                    fps = cap.get(cv2.CAP_PROP_FPS)
                    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    duration = total_frames / fps if fps > 0 else 0
                    cap.release()
                    st.markdown(f"""
                    <div class="info-card">
                        <div class="info-card-title">📊 视频信息</div>
                        <div class="info-card-body">
                            <strong>{video_file.name}</strong><br>
                            分辨率 {width} × {height} &nbsp;·&nbsp; {fps:.1f} FPS<br>
                            共 {total_frames} 帧 &nbsp;·&nbsp; 时长 {duration:.1f}s<br>
                            大小 {video_file.size / (1024*1024):.1f} MB
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.video(video_file)
            except Exception as e:
                st.error(f"读取视频信息失败: {e}")

    with col_r:
        if video_file:
            st.markdown("#### 处理")
            st.info("将随机删除视频内两帧，保留原始音频和画质，时长几乎不变。")

            if st.button("🎬 开始抽帧处理", type="primary", use_container_width=True, key="process_video"):
                with st.spinner("处理中…"):
                    pb = st.progress(0)
                    st_txt = st.empty()
                    out_name = f"{os.path.splitext(video_file.name)[0]}_抽帧版.mp4"
                    try:
                        op, vinfo, frames_rm, saved = remove_random_frames(temp_video_path, out_name, pb, st_txt)
                        pb.progress(1.0); st_txt.empty()
                        with open(op, 'rb') as f:
                            vdata = f.read()
                        st.session_state.processed_video = vdata
                        st.session_state.video_info = {"original_info": vinfo, "frames_removed": frames_rm,
                                                        "saved_frames": saved, "output_filename": out_name}
                        st.success("✅ 处理完成")
                        st.markdown(f"""
                        <div class="info-card">
                            <div class="info-card-title">✅ 处理结果</div>
                            <div class="info-card-body">
                                删除第 <strong>{frames_rm[0]}</strong> 帧和第 <strong>{frames_rm[1]}</strong> 帧<br>
                                原帧数 {vinfo['total_frames']} → 新帧数 {saved}<br>
                                分辨率 {vinfo['width']} × {vinfo['height']} &nbsp;·&nbsp; {vinfo['fps']:.1f} FPS
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        st.video(vdata)
                    except Exception as e:
                        pb.empty(); st_txt.empty()
                        st.error(f"处理失败: {e}")
                    finally:
                        for p in [temp_video_path, out_name]:
                            if os.path.exists(p): os.unlink(p)

            if st.session_state.processed_video and st.session_state.video_info:
                st.markdown("#### 下载")
                vinfo = st.session_state.video_info
                st.download_button(
                    label=f"⬇ 下载处理后视频",
                    data=st.session_state.processed_video,
                    file_name=vinfo["output_filename"],
                    mime="video/mp4",
                    use_container_width=True,
                    key="download_video"
                )
                if st.button("🔄 处理另一个视频", key="process_another"):
                    st.session_state.processed_video = None
                    st.session_state.video_info = None
                    st.rerun()

# ========== Tab 3：Logo水印添加 ==========
with tab3:
    preset_map = {
        "左上角": (5, 5), "右上角": (95, 5), "左下角": (5, 95), "右下角": (95, 95),
        "居中": (50, 50), "顶部居中": (50, 5), "底部居中": (50, 95),
        "左侧居中": (5, 50), "右侧居中": (95, 50)
    }

    st.markdown("""
    <div class="info-banner">
      为单张图片添加 Logo 水印，实时预览效果后一键下载。
    </div>
    """, unsafe_allow_html=True)

    col_l, col_m, col_r = st.columns([1, 1, 2], gap="medium")

    with col_l:
        st.markdown("#### 上传图片")
        uploaded_image = st.file_uploader(
            "图片", type=['png', 'jpg', 'jpeg'], accept_multiple_files=False,
            key="logo_adder_uploader", label_visibility="collapsed"
        )
        if uploaded_image:
            img = Image.open(uploaded_image)
            st.success("图片已上传")
            st.markdown(f"""
            <div class="info-card">
                <div class="info-card-title">图片信息</div>
                <div class="info-card-body">
                    <strong>{uploaded_image.name}</strong><br>
                    {img.width} × {img.height} px
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col_m:
        st.markdown("#### Logo 设置")
        logo_color_la = st.radio("颜色", ["黑色Logo", "白色Logo"],
                                   index=0 if st.session_state.logo_adder_logo_color == "黑色Logo" else 1,
                                   horizontal=True, key="logo_adder_color_radio")
        st.session_state.logo_adder_logo_color = logo_color_la

        opacity = st.slider("透明度", min_value=0, max_value=255,
                             value=st.session_state.logo_adder_logo_opacity, step=5,
                             key="logo_adder_opacity_slider",
                             help="0 = 完全透明，255 = 完全不透明")
        st.session_state.logo_adder_logo_opacity = opacity
        st.caption(f"当前：{int(opacity/255*100)}%")

        size = st.slider("大小（%）", min_value=5, max_value=200,
                          value=st.session_state.logo_adder_logo_size, step=5,
                          key="logo_adder_size_slider")
        st.session_state.logo_adder_logo_size = size

        st.markdown("#### 位置")
        preset_opts = ["自定义"] + list(preset_map.keys())
        sel_preset = st.selectbox("预设位置", preset_opts,
                                    index=preset_opts.index(st.session_state.logo_adder_preset_position)
                                    if st.session_state.logo_adder_preset_position in preset_opts else 0,
                                    key="preset_selectbox")
        if sel_preset != st.session_state.logo_adder_preset_position:
            st.session_state.logo_adder_preset_position = sel_preset
            if sel_preset in preset_map:
                x, y = preset_map[sel_preset]
                st.session_state.logo_adder_logo_x = x
                st.session_state.logo_adder_logo_y = y
                st.rerun()

        cx, cy = st.columns(2)
        with cx:
            x_pos = st.slider("X (%)", 0, 100, st.session_state.logo_adder_logo_x, key="logo_adder_x_slider")
            st.session_state.logo_adder_logo_x = x_pos
        with cy:
            y_pos = st.slider("Y (%)", 0, 100, st.session_state.logo_adder_logo_y, key="logo_adder_y_slider")
            st.session_state.logo_adder_logo_y = y_pos

        cur_preset_name = next((k for k, v in preset_map.items() if v == (x_pos, y_pos)), "自定义")
        st.caption(f"📍 X={x_pos}%  Y={y_pos}%  ·  {cur_preset_name}")

    with col_r:
        st.markdown("#### 预览 & 下载")
        if uploaded_image:
            logo_path = f"logos/{'b' if logo_color_la == '黑色Logo' else 'w'}_logo.png"
            if not os.path.exists(logo_path):
                st.warning(f"未找到 Logo 文件：{logo_path}")
                st.caption("请在 logos/ 目录中放置 b_logo.png 和 w_logo.png")
            else:
                logo_img = Image.open(logo_path)
                original_img = Image.open(uploaded_image)
                result = add_logo_to_image(original_img, logo_img, x_pos, y_pos, size, opacity)
                if result:
                    st.image(result, caption="实时预览", use_column_width=True)
                    ow, oh = result.size
                    st.caption(f"原图 {ow}×{oh}px · 透明度 {int(opacity/255*100)}% · 大小 {size}%")

                    # 下载
                    buf = BytesIO()
                    save_img = result
                    if result.mode == 'RGBA':
                        rgb = Image.new('RGB', result.size, (255, 255, 255))
                        rgb.paste(result, mask=result.split()[3])
                        save_img = rgb
                    save_img.save(buf, format='JPEG', quality=95)
                    buf.seek(0)
                    fsize = len(buf.getvalue()) / 1024
                    stem = os.path.splitext(uploaded_image.name)[0]
                    st.info(f"文件大小：{fsize:.1f} KB · JPG 格式 · 质量 95%")
                    st.download_button(
                        label="⬇ 下载图片（JPG）",
                        data=buf,
                        file_name=f"{stem}_with_logo.jpg",
                        mime="image/jpeg",
                        use_container_width=True,
                        key="download_logo_adder"
                    )
        else:
            st.markdown("""
            <div class="logo-adder-preview-placeholder">
                <h4>👈 请先上传图片</h4>
                <p>上传后可调整 Logo 设置并实时预览</p>
            </div>
            """, unsafe_allow_html=True)

# ==================== 批量合成执行 ====================
if process_button:
    bg_files_combined = []
    if 'bg_files' in locals() and bg_files:
        bg_files_combined.extend(bg_files)
    if st.session_state.unsplash_selected_bg:
        bg_files_combined.append(st.session_state.unsplash_selected_bg)
    product_files = st.session_state.persist_product_files

    if not bg_files_combined:
        st.error("请至少上传一张背景图或从 Unsplash 选择背景。")
        st.stop()
    if not product_files:
        st.error("请至少上传一张产品图。")
        st.stop()

    logo_color_val = st.session_state.get('logo_color', '黑色Logo')
    product_size_val = st.session_state.get('product_size', 800)
    output_size_val = st.session_state.get('output_size', 800)
    output_format_val = st.session_state.get('output_format', 'JPG')
    dark_mask_val = st.session_state.get('dark_mask_enabled', False)
    mask_opacity_val = st.session_state.get('mask_opacity', 20)
    mask_color_val = st.session_state.get('mask_color_rgb', (255, 255, 255))

    logo_path = "logos/black_logo.png" if logo_color_val == '黑色LOGO' else "logos/white_logo.png"
    logo_to_use = Image.open(logo_path) if os.path.exists(logo_path) else None
    if not logo_to_use:
        st.warning(f"未找到 Logo 文件：{logo_path}")

    with tempfile.TemporaryDirectory() as tmpdir:
        output_files = []
        preview_images = []
        total = len(bg_files_combined) * len(product_files)
        pb = st.progress(0)
        st_txt = st.empty()
        processed = 0

        for i, bg_file in enumerate(bg_files_combined):
            bg_image = Image.open(bg_file) if hasattr(bg_file, 'read') else bg_file.image if hasattr(bg_file, 'image') else None
            if not bg_image:
                continue
            for j, pf in enumerate(product_files):
                product_image = Image.open(pf)
                processed += 1
                pb.progress(processed / total)
                st_txt.text(f"处理中 {processed}/{total}")
                result = compose_image(bg_image, product_image, logo_to_use,
                                       product_size_val, output_size_val, output_format_val,
                                       mask_enabled=dark_mask_val, mask_color=mask_color_val, mask_opacity=mask_opacity_val)
                bg_name = os.path.splitext(bg_file.name)[0] if hasattr(bg_file, 'name') else f"bg_{i}"
                out_name = f"{bg_name}_{os.path.splitext(pf.name)[0]}.{output_format_val.lower()}"
                out_path = os.path.join(tmpdir, out_name)
                if output_format_val.upper() == 'JPG':
                    result.save(out_path, format='JPEG', quality=95)
                else:
                    result.save(out_path, format='PNG')
                output_files.append(out_path)
                if len(preview_images) < 24:
                    buf = BytesIO()
                    if output_format_val.upper() == 'JPG':
                        if result.mode == 'RGBA':
                            rgb = Image.new('RGB', result.size, (255, 255, 255))
                            rgb.paste(result, mask=result.split()[3])
                            rgb.save(buf, format='JPEG', quality=90)
                        else:
                            result.save(buf, format='JPEG', quality=90)
                    else:
                        result.save(buf, format='PNG')
                    buf.seek(0)
                    preview_images.append({"data": buf, "filename": out_name})

        st.session_state.synthesize_preview_images = preview_images
        pb.empty(); st_txt.empty()

        zip_buf = BytesIO()
        with zipfile.ZipFile(zip_buf, 'w', zipfile.ZIP_DEFLATED) as zf:
            for fp in output_files:
                zf.write(fp, os.path.basename(fp))
        zip_buf.seek(0)
        st.session_state.synthesize_zip_buffer = zip_buf
        st.session_state.synthesize_zip_info = {"output_size": output_size_val, "output_format": output_format_val}

        st.toast(f"✅ 合成完成！共生成 {len(output_files)} 张图片", icon="✅")
        st.rerun()

# ==================== 页脚 ====================
st.markdown("---")
st.caption("© 2026 骏泰素材工作台")
