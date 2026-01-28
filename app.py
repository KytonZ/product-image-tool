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
        /* 全局字体和间距优化 */
        .stApp {
            font-family: 'Microsoft YaHei', 'Segoe UI', sans-serif !important;
        }
        
        /* 主标题样式 */
        .main-header {
            padding: 0.2rem 0;
            margin-bottom: 0.1rem !important;
        }
        
        /* 卡片式UI */
        .stCard {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 1.2rem;
            margin-bottom: 1rem;
            border-left: 4px solid #2196F3;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        /* 标签页样式优化 */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            padding: 0 10px;
        }
        /* 减少标签页内标题间距 */
        .stTabs [data-baseweb="tab-list"] {
            margin-bottom: 0.5rem !important;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 10px 20px;
            border-radius: 5px 5px 0 0;
            font-weight: 500;
        }
        
        /* 调整按钮样式，去掉emoji后的按钮样式 */
        .small-button {
            font-size: 0.8rem;
            padding: 0.2rem 0.5rem;
        }

        /* 按钮样式（全局通用，移除了原Unsplash专属按钮样式） */
        .stButton > button {
            border-radius: 32px;
            padding: 0.6rem 1.2rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        /* 调整搜索区域的行内对齐 */
        .search-row {
            align-items: center;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        
        /* 图片预览优化 */
        .image-container {
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 8px;
            background: white;
            transition: all 0.3s ease;
            text-align: center;
            margin-bottom: 10px;
        }
        
        .image-container:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 16px rgba(0,0,0,0.1);
            border-color: #2196F3;
        }
        
        /* 侧边栏优化 */
        section[data-testid="stSidebar"] {
            min-width: 280px !important;
            max-width: 320px !important;
        }
        
        section[data-testid="stSidebar"] > div:first-child {
            padding-top: 2rem;
        }
        
        /* 响应式调整 */
        @media (min-width: 1920px) {
            /* 2K屏幕优化 */
            .stTabs [data-baseweb="tab"] {
                padding: 12px 24px;
                font-size: 16px;
            }
            
            .stButton > button {
                padding: 0.7rem 1.4rem;
                font-size: 16px;
            }
            
            .stCard {
                padding: 1.5rem;
            }
        }
        
        /* 紧凑网格布局 */
        .compact-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
            gap: 16px;
            margin-top: 1rem;
        }
        
        /* 上传区域样式 */
        .upload-area {
            border: 2px dashed #ddd;
            border-radius: 10px;
            padding: 2rem;
            text-align: center;
            background: #fafafa;
            margin: 1rem 0;
            transition: border-color 0.3s;
        }
        
        .upload-area:hover {
            border-color: #2196F3;
        }
        
        /* 进度条美化 */
        .stProgress > div > div {
            background: linear-gradient(90deg, #2196F3, #21CBF3);
        }
        
        /* 状态消息样式 */
        .status-success {
            background-color: #d4edda;
            color: #155724;
            padding: 10px;
            border-radius: 5px;
            border-left: 4px solid #28a745;
        }
        
        .status-warning {
            background-color: #fff3cd;
            color: #856404;
            padding: 10px;
            border-radius: 5px;
            border-left: 4px solid #ffc107;
        }
        
        /* 预览图片标签 */
        .image-label {
            font-size: 12px;
            color: #666;
            margin-top: 5px;
            word-break: break-all;
            text-align: center;
        }
        
        /* 文件计数徽章 */
        .file-count {
            display: inline-block;
            background: #2196F3;
            color: white;
            border-radius: 12px;
            padding: 2px 8px;
            font-size: 12px;
            margin-left: 5px;
        }
        
        /* 设置组样式 */
        .settings-group {
            margin-bottom: 1.5rem;
        }
        
        .settings-title {
            font-weight: 600;
            color: #333;
            margin-bottom: 0.8rem;
            font-size: 1rem;
        }
        
        /* Unsplash图片样式 - 核心修改：图片可点击+红框选中 */
        .unsplash-image-card {
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            padding: 5px;
            margin-bottom: 10px;
            background: white;
            transition: all 0.3s ease;
            position: relative;
        }
        
        /* 调整按钮容器，使两个按钮并排且紧凑 */
        .button-container {
            display: flex;
            justify-content: space-between;
            margin-top: 5px;
        }

        .unsplash-image-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            border-color: #2196F3;
        }
        
        .unsplash-author {
            font-size: 12px;
            color: #666;
            margin-top: 5px;
            text-align: center;
        }
        
        .unsplash-badge {
            position: absolute;
            top: 10px;
            right: 10px;
            background: rgba(0,0,0,0.6);
            color: white;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 11px;
        }
        
        /* 紧凑布局 */
        .stTabs [data-baseweb="tab"] {
            padding: 8px 16px;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 5px;
        }
        
        /* 选项卡样式 */
        .bg-tab-container {
            margin-top: 20px;
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            padding: 15px;
            background: #f8f9fa;
        }
        
        /* 文案生成专用样式 */
        .copy-area {
            background-color: #f8f9fa;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 15px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            line-height: 1.5;
            white-space: pre-wrap;
            word-wrap: break-word;
            max-height: 400px;
            overflow-y: auto;
            margin-bottom: 15px;
        }
        
        .copy-button {
            margin-top: 10px;
            margin-bottom: 20px;
        }
        
        .section-title {
            color: #2196F3;
            border-bottom: 2px solid #2196F3;
            padding-bottom: 5px;
            margin-top: 25px;
            margin-bottom: 15px;
        }
        
        .highlight-box {
            background-color: #e8f4fd;
            border-left: 4px solid #2196F3;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        
        /* 上传列对齐样式 */
        .upload-column {
            min-height: 600px;
        }
        
        /* Unsplash图片网格布局 */
        .unsplash-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
            gap: 12px;
            margin-top: 1rem;
        }
        
        /* 视频信息卡片 */
        .video-info-card {
            background-color: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
            border-left: 4px solid #FF6B6B;
        }
        
        .video-info-title {
            font-weight: 600;
            color: #333;
            margin-bottom: 10px;
            font-size: 1rem;
        }
        
        .video-info-text {
            font-size: 14px;
            line-height: 1.6;
            color: #555;
        }
        
        /* Logo水印添加 */
        .logo-adder-container {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            border-left: 4px solid #4CAF50;
        }
        
        .logo-adder-preview {
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            padding: 15px;
            background: white;
            text-align: center;
            margin-top: 20px;
        }
        
        /* 去掉控制组的外框，简化设计 */
        .stSlider, .stRadio, .stSelectbox {
            margin-bottom: 1rem;
        }
        
        /* 优化预设位置按钮 */
        .preset-buttons-container {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 1rem;
        }
        
        .preset-button {
            flex: 1;
            min-width: 100px;
            padding: 8px 12px;
            border-radius: 6px;
            border: 2px solid #e0e0e0;
            background: white;
            color: #333;
            font-size: 14px;
            text-align: center;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .preset-button:hover {
            border-color: #4CAF50;
            background: #f0f9f0;
        }
        
        /* 原有样式保持不变 */
        
        /* Logo颜色选择按钮样式 */
        .logo-color-btn {
            border-radius: 32px !important;
            padding: 0.6rem 1.2rem !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
            width: 100% !important;
        }
        
        /* 黑色Logo按钮 */
        .logo-black-btn {
            background-color: #333333 !important;
            color: white !important;
            border: 1px solid #333333 !important;
        }
        
        .logo-black-btn:hover {
            background-color: #000000 !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
        }
        
        .logo-black-btn.active {
            border-color: #2196F3 !important;
            box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.3) !important;
        }
        
        /* 白色Logo按钮 */
        .logo-white-btn {
            background-color: white !important;
            color: #333333 !important;
            border: 1px solid #dddddd !important;
        }
        
        .logo-white-btn:hover {
            background-color: #f5f5f5 !important;
            border-color: #2196F3 !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
        }
        
        .logo-white-btn.active {
            border-color: #2196F3 !important;
            box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.3) !important;
        }
        /* 原有样式保持不变 */

        .preset-button.active {
            border-color: #4CAF50;
            background: #4CAF50;
            color: white;
        }
        
        /* 优化滑块样式 */
        .stSlider label {
            font-weight: 600;
            color: #333;
            margin-bottom: 0.5rem;
            display: block;
        }
        
        /* 优化实时预览 */
        .live-preview-container {
            margin-top: 1.5rem;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 15px;
            background: white;
        }
        
        .preview-title {
            font-weight: 600;
            color: #333;
            margin-bottom: 10px;
        }
        
        /* 下载按钮样式优化 */
        .download-section {
            margin-top: 2rem;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            border-left: 4px solid #2196F3;
        }
        
        /* 遮罩设置样式 */
        .mask-info {
            background-color: #e8f4fd;
            border-left: 4px solid #4CAF50;
            padding: 10px;
            border-radius: 5px;
            margin-top: 10px;
            font-size: 14px;
        }
        
        /* 颜色预览框 */
        .color-preview-box {
            width: 40px;
            height: 40px;
            border-radius: 6px;
            border: 2px solid #e0e0e0;
            margin: 0 auto;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: bold;
        }
        
        /* 颜色选项容器 */
        .color-options-container {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin: 10px 0;
        }
        
        .color-option {
            width: 40px;
            height: 40px;
            border-radius: 6px;
            border: 2px solid #e0e0e0;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: bold;
        }
        
        .color-option:hover {
            transform: scale(1.05);
            border-color: #2196F3;
        }
        
        .color-option.selected {
            border-color: #2196F3;
            border-width: 3px;
            box-shadow: 0 0 8px rgba(33, 150, 243, 0.4);
        }
        /* 修改按钮样式，确保未选中按钮为白色背景 */
        .stButton > button[kind="secondary"] {
            background-color: white !important;
            color: #333 !important;
            border: 1px solid #ddd !important;
        }

        .stButton > button[kind="secondary"]:hover {
            background-color: #f5f5f5 !important;
            border-color: #2196F3 !important;
        }

        /* ========== 上传组件中文提示样式（终极修复版） ========== */
        /* 适配Streamlit 1.20+所有版本的上传组件样式覆盖 */
        /* 1. 完全隐藏原生所有英文文本 */
        div[data-testid="stFileUploader"] * {
            font-family: 'Microsoft YaHei', sans-serif !important;
        }
        [data-testid="stFileUploaderDropzone"] p,
        [data-testid="stFileUploaderDropzone"] div,
        [data-testid="stFileUploaderDropzone"] span {
            visibility: hidden !important;
            position: relative !important;
        }
        /* 2. 全局默认中文提示 */
        [data-testid="stFileUploaderDropzone"]::before {
            content: "拖拽文件到此处或点击上传" !important;
            visibility: visible !important;
            position: absolute !important;
            top: 50% !important;
            left: 50% !important;
            transform: translate(-50%, -50%) !important;
            width: 100% !important;
            height: 100% !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            color: #666 !important;
            font-size: 14px !important;
            font-family: 'Microsoft YaHei', sans-serif !important;
            z-index: 9999 !important;
        }
        /* 3. 针对不同上传区域的精准中文提示 */
        #bg_upload [data-testid="stFileUploaderDropzone"]::before {
            content: "拖拽或上传背景图片" !important;
        }
        #product_upload [data-testid="stFileUploaderDropzone"]::before {
            content: "拖拽或上传产品图片（透明PNG最佳）" !important;
        }
        #video_uploader [data-testid="stFileUploaderDropzone"]::before {
            content: "拖拽或上传视频文件" !important;
        }
        #logo_adder_uploader [data-testid="stFileUploaderDropzone"]::before {
            content: "拖拽或上传需要添加Logo的图片" !important;
        }
        /* 4. 上传按钮文本替换 */
        [data-testid="stFileUploaderDropzone"] button {
            font-size: 14px !important;
            font-family: 'Microsoft YaHei', sans-serif !important;
            visibility: visible !important;
        }
        [data-testid="stFileUploaderDropzone"] button span {
            visibility: hidden !important;
            position: relative !important;
        }
        [data-testid="stFileUploaderDropzone"] button span::after {
            content: "选择文件" !important;
            visibility: visible !important;
            position: absolute !important;
            top: 0 !important;
            left: 50% !important;
            transform: translateX(-50%) !important;
            z-index: 9999 !important;
        }

        /* 选中按钮为绿色 */
        .stButton > button[kind="primary"] {
            background-color: #4CAF50 !important;
            color: white !important;
            border: 1px solid #4CAF50 !important;
        }

        .stButton > button[kind="primary"]:hover {
            background-color: #45a049 !important;
            border-color: #45a049 !important;
        }
        /* 替换原有对应的样式，新增/强化关键属性 */
        .unsplash-square-container {
            width: 100%;
            aspect-ratio: 1/1 !important; /* 强制1:1宽高比，!important提高优先级 */
            overflow: hidden !important; /* 确保超出容器的图片部分被裁剪，无残留 */
            border-radius: 6px;
            margin-bottom: 8px;
            border: 1px solid #e0e0e0;
            position: relative !important; /* 确保绝对定位图片的容器基准 */
            background-color: #f0f0f0; /* 图片加载前显示浅灰背景，替代纯白边，提升体验 */
        }

        /* 使用背景图片方式确保100%填充（比img标签更稳定，无白边） */
        .unsplash-square-bg-image {
            position: absolute;
            top: 0;
            left: 0;
            width: 100% !important;
            height: 100% !important;
            background-size: cover !important; /* 裁剪填充，无白边 */
            background-position: center center !important; /* 图片居中，保留核心内容 */
            background-repeat: no-repeat !important; /* 禁止重复，避免白边 */
        }

        /* 保留原有img标签样式（备选，优化后无白边） */
        .unsplash-square-image {
            position: absolute !important;
            top: 0 !important;
            left: 0 !important;
            width: 100% !important;
            height: 100% !important;
            object-fit: cover !important; /* 强制裁剪填充，覆盖默认样式 */
            object-position: center center !important; /* 居中裁剪，保留图片核心 */
            display: block !important; /* 消除img标签默认的行内元素间距 */
            margin: 0 !important; /* 清除默认边距 */
            padding: 0 !important; /* 清除默认内边距 */
            border: none !important; /* 清除可能的边框 */
        }
        
    </style>
    """

# 应用CSS样式
st.markdown(get_custom_css(), unsafe_allow_html=True)

# 页面标题
# 原代码：st.markdown('<h1 class="main-header">🎨 骏泰素材工作台</h1>', unsafe_allow_html=True)
st.markdown('<h1 class="main-header">🎨 骏泰素材工作台</h1>', unsafe_allow_html=True)  # 移除emoji，或替换为logo图片

# 初始化会话状态
if 'current_page' not in st.session_state:
    st.session_state.current_page = 0
if 'processed_images' not in st.session_state:
    st.session_state.processed_images = []
if 'last_zip_buffer' not in st.session_state:
    st.session_state.last_zip_buffer = None
if 'processed_video' not in st.session_state:
    st.session_state.processed_video = None
if 'video_info' not in st.session_state:
    st.session_state.video_info = None
if 'unsplash_photos' not in st.session_state:
    st.session_state.unsplash_photos = []
if 'unsplash_selected_bg' not in st.session_state:
    st.session_state.unsplash_selected_bg = None
if 'unsplash_search_query' not in st.session_state:
    st.session_state.unsplash_search_query = "white background"
if 'unsplash_search_trigger' not in st.session_state:
    st.session_state.unsplash_search_trigger = False
if 'unsplash_current_page' not in st.session_state:
    st.session_state.unsplash_current_page = 1
if 'unsplash_total_pages' not in st.session_state:
    st.session_state.unsplash_total_pages = 0
if 'unsplash_selected_page' not in st.session_state:
    st.session_state.unsplash_selected_page = 1  # 选中图片的页码
if 'unsplash_selected_idx' not in st.session_state:
    st.session_state.unsplash_selected_idx = -1  # 选中图片的索引（-1表示未选中）
if 'synthesize_zip_buffer' not in st.session_state:
    st.session_state.synthesize_zip_buffer = None
if 'synthesize_zip_info' not in st.session_state:
    st.session_state.synthesize_zip_info = {}
if 'persist_product_files' not in st.session_state:
    st.session_state.persist_product_files = []  # 用于持久化保存产品图上传数据
if 'unsplash_total_results' not in st.session_state:
    st.session_state.unsplash_total_results = 0

# Logo水印添加相关的会话状态
if 'logo_adder_images' not in st.session_state:
    st.session_state.logo_adder_images = []
if 'logo_adder_logo_color' not in st.session_state:
    st.session_state.logo_adder_logo_color = "黑色Logo"
if 'logo_adder_logo_opacity' not in st.session_state:
    st.session_state.logo_adder_logo_opacity = 180
if 'logo_adder_logo_size' not in st.session_state:
    st.session_state.logo_adder_logo_size = 100
if 'logo_adder_logo_x' not in st.session_state:
    st.session_state.logo_adder_logo_x = 50
if 'logo_adder_logo_y' not in st.session_state:
    st.session_state.logo_adder_logo_y = 50
if 'logo_adder_logo_image' not in st.session_state:
    st.session_state.logo_adder_logo_image = None
if 'logo_adder_processed_images' not in st.session_state:
    st.session_state.logo_adder_processed_images = []
if 'logo_adder_last_zip_buffer' not in st.session_state:
    st.session_state.logo_adder_last_zip_buffer = None
if 'logo_adder_preset_position' not in st.session_state:
    st.session_state.logo_adder_preset_position = "自定义"

# 背景遮罩相关的会话状态
if 'dark_mask_enabled' not in st.session_state:
    st.session_state.dark_mask_enabled = False
if 'mask_opacity' not in st.session_state:
    st.session_state.mask_opacity = 20
# 添加遮罩颜色相关的会话状态
if 'mask_color_type' not in st.session_state:
    st.session_state.mask_color_type = "预设颜色"  # 预设颜色或自定义颜色
if 'mask_preset_color' not in st.session_state:
    st.session_state.mask_preset_color = "白色"  # 默认从黑色改为白色
if 'mask_custom_color' not in st.session_state:
    st.session_state.mask_custom_color = "#FFFFFF"  # 默认白色
if 'mask_color_rgb' not in st.session_state:
    st.session_state.mask_color_rgb = (255, 255, 255)  # 默认白色RGB

# 预设颜色选项
PRESET_COLORS = {
    "白色": "#FFFFFF",
    "黑色": "#000000",
    "深灰": "#333333",
    "浅灰": "#CCCCCC",
    "深蓝": "#003366",
    "蓝色": "#0066CC",
    "深绿": "#006633",
    "浅绿": "#66CC99",
    "深红": "#990000",
    "红色": "#CC3333",
    "深紫": "#663366",
    "紫色": "#9966CC",
    "金色": "#FFD700",
    "橙色": "#FF9900",
    "棕色": "#996633"
}

# ==================== Unsplash API类 ====================
class UnsplashAPI:
    def __init__(self):
        # 自动从Streamlit Secrets读取API密钥
        try:
            self.access_key = st.secrets["UNSPLASH_ACCESS_KEY"]
        except:
            self.access_key = ""
            st.warning("⚠️ 未找到Unsplash API密钥，请在Streamlit Secrets中配置UNSPLASH_ACCESS_KEY")
        
        self.base_url = "https://api.unsplash.com"
    
    def search_photos(self, query, page=1, per_page=12):
        """搜索Unsplash图片"""
        if not self.access_key:
            return [], 0, 0  # 返回空列表和0页
        
        url = f"{self.base_url}/search/photos"
        headers = {"Authorization": f"Client-ID {self.access_key}"}
        params = {
            "query": query,
            "page": page,
            "per_page": per_page,
            "orientation": "squarish",
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # 从API响应中获取总页数
                total = data.get("total", 0)
                total_pages = data.get("total_pages", 0)

                # 如果API没有返回total_pages，我们计算一下
                if total_pages == 0 and total > 0:
                    total_pages = (total + per_page - 1) // per_page
                total_pages = min(total_pages, 1000)

                return data.get("results", []), total_pages, total
            elif response.status_code == 401:
                st.error("Unsplash API密钥无效，请检查您的密钥")
                return [], 0, 0
            else:
                st.error(f"Unsplash API错误: {response.status_code}")
                return [], 0, 0
        except Exception as e:
            st.error(f"Unsplash API请求失败: {e}")
            return [], 0, 0
    
    def download_photo(self, photo_url):
        """下载图片"""
        try:
            response = requests.get(photo_url, timeout=10)
            if response.status_code == 200:
                return Image.open(BytesIO(response.content))
        except Exception as e:
            st.error(f"下载图片失败: {e}")
        return None

# ==================== 颜色辅助函数 ====================
def hex_to_rgb(hex_color):
    """将十六进制颜色转换为RGB元组"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb):
    """将RGB元组转换为十六进制颜色"""
    return '#{:02x}{:02x}{:02x}'.format(*rgb)

def get_color_brightness(rgb):
    """计算颜色亮度（0-255）"""
    r, g, b = rgb
    return (r * 299 + g * 587 + b * 114) / 1000

def get_current_mask_color():
    """获取当前设置的遮罩颜色RGB"""
    if st.session_state.mask_color_type == "预设颜色":
        hex_color = PRESET_COLORS[st.session_state.mask_preset_color]
        return hex_to_rgb(hex_color)
    else:
        # 自定义颜色
        hex_color = st.session_state.mask_custom_color
        return hex_to_rgb(hex_color)

# ==================== 核心函数定义 ====================
def compose_image(bg_img, product_img, logo_img, product_size, output_size, output_format, 
                  mask_enabled=False, mask_color=(255, 255, 255), mask_opacity=20):
    """合成单张图片的核心函数
    mask_enabled: 是否启用遮罩
    mask_color: 遮罩颜色RGB元组
    mask_opacity: 遮罩层不透明度（0-100）
    """
    # 1. 处理背景：调整到输出尺寸（智能裁剪铺满）
    bg = bg_img.convert('RGBA')
    bg_ratio = output_size / min(bg.width, bg.height)
    new_width = int(bg.width * bg_ratio)
    new_height = int(bg.height * bg_ratio)
    bg = bg.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # 居中裁剪
    left = (bg.width - output_size) // 2
    top = (bg.height - output_size) // 2
    right = left + output_size
    bottom = top + output_size
    bg = bg.crop((left, top, right, bottom))
    
    # 2. 添加颜色遮罩层（如果启用）
    if mask_enabled and mask_opacity > 0:
        # 创建颜色遮罩层
        mask_opacity_int = int(mask_opacity * 255 / 100)  # 转换为0-255范围
        r, g, b = mask_color
        color_layer = Image.new('RGBA', bg.size, (r, g, b, mask_opacity_int))
        # 将颜色遮罩层与背景图叠加
        bg = Image.alpha_composite(bg, color_layer)
    
    # 3. 处理产品图：调整大小并居中放置
    product = product_img.convert('RGBA')
    product.thumbnail((product_size, product_size), Image.Resampling.LANCZOS)
    
    # 将产品图居中放置
    product_x = (output_size - product.width) // 2
    product_y = (output_size - product.height) // 2
    
    # 将产品图粘贴到背景上
    bg.paste(product, (product_x, product_y), product)
    
    # 4. 处理Logo图 - 直接全画布叠加
    if logo_img:
        logo = logo_img.convert('RGBA')
        # 确保Logo图尺寸与输出尺寸一致
        if logo.size != (output_size, output_size):
            logo = logo.resize((output_size, output_size), Image.Resampling.LANCZOS)
        # 直接以遮罩方式叠加整个Logo图层
        bg = Image.alpha_composite(bg, logo)
    
    # 5. 根据输出格式处理背景
    if output_format.upper() == 'JPG':
        bg_rgb = Image.new('RGB', bg.size, (255, 255, 255))
        bg_rgb.paste(bg, mask=bg.split()[3])
        final_image = bg_rgb
    else:
        final_image = bg
    
    return final_image

def remove_random_frames(input_video_path, output_video_path, progress_bar=None, status_text=None):
    """
    从视频中随机删除两帧并导出新视频 (保留音频)
    参数:
        input_video_path: 输入视频文件路径
        output_video_path: 输出视频文件路径
        progress_bar: Streamlit进度条对象
        status_text: Streamlit状态文本对象
    """
    # 检查输入文件是否存在
    if not os.path.exists(input_video_path):
        raise FileNotFoundError(f"找不到输入视频文件 '{input_video_path}'")
    
    # 使用OpenCV读取视频信息
    cap = cv2.VideoCapture(input_video_path)
    if not cap.isOpened():
        raise ValueError("无法打开视频文件，请检查格式是否支持（如MP4）。")
    
    # 获取视频基本信息
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = total_frames / fps
    
    video_info = {
        "total_frames": total_frames,
        "fps": fps,
        "width": width,
        "height": height,
        "duration": duration
    }
    
    # 检查视频长度是否足够
    if total_frames <= 2:
        cap.release()
        raise ValueError("视频太短，不足以移除两帧。")
    
    # 随机选择要删除的两帧（确保不重复且不在首尾关键帧）
    # 避免删除第0帧和最后一帧，以防编码问题
    available_frames = list(range(1, total_frames - 1))
    if len(available_frames) >= 2:
        frames_to_remove = sorted(random.sample(available_frames, 2))
    else:
        frames_to_remove = sorted(random.sample(range(total_frames), min(2, total_frames)))
    
    # 更新状态
    if status_text:
        status_text.text(f"将删除第 {frames_to_remove[0]} 帧和第 {frames_to_remove[1]} 帧")
    
    # 1. 首先提取并保存音频（使用moviepy）
    try:
        video_clip = VideoFileClip(input_video_path)
        audio = video_clip.audio
        has_audio = audio is not None
        
        # 创建临时音频文件
        temp_audio_path = "temp_audio.wav"
        if has_audio:
            audio.write_audiofile(temp_audio_path, verbose=False, logger=None)
        video_clip.close()
    except Exception as e:
        st.warning(f"音频处理出现异常，将继续处理视频（可能无音频）: {e}")
        has_audio = False
    
    # 2. 处理视频帧（移除指定帧）
    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')  # MP4编码
    out = cv2.VideoWriter('temp_video_noaudio.mp4', fourcc, fps, (width, height))
    
    frame_index = 0
    saved_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break  # 视频读取完毕
            
        # 如果当前帧不在删除列表中，则写入新视频
        if frame_index not in frames_to_remove:
            out.write(frame)
            saved_count += 1
            
        frame_index += 1
        
        # 更新进度条
        if progress_bar and total_frames > 0:
            progress = frame_index / total_frames
            progress_bar.progress(progress)
    
    # 释放资源
    cap.release()
    out.release()
    
    # 3. 重新合并音频（如果存在）
    if has_audio:
        if status_text:
            status_text.text("正在重新合并音频...")
        
        try:
            # 加载处理后的无音频视频
            video_no_audio = VideoFileClip('temp_video_noaudio.mp4')
            # 加载之前提取的音频
            final_clip = video_no_audio.set_audio(AudioFileClip(temp_audio_path))
            # 写入最终文件
            final_clip.write_videofile(
                output_video_path,
                codec='libx264',
                audio_codec='aac',
                verbose=False,
                logger=None
            )
            video_no_audio.close()
            final_clip.close()
            
            # 清理临时文件
            if os.path.exists('temp_video_noaudio.mp4'):
                os.remove('temp_video_noaudio.mp4')
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)
        except Exception as e:
            st.warning(f"音视频合并失败，将输出无音频视频: {e}")
            # 如果合并失败，则将无音频视频作为输出
            if os.path.exists('temp_video_noaudio.mp4'):
                os.rename('temp_video_noaudio.mp4', output_video_path)
    else:
        # 无音频，直接重命名临时文件
        if os.path.exists('temp_video_noaudio.mp4'):
            os.rename('temp_video_noaudio.mp4', output_video_path)
    
    return output_video_path, video_info, frames_to_remove, saved_count

# ==================== Logo水印添加核心函数 ====================
def add_logo_to_image(base_image, logo_image, x_percent, y_percent, size_percent, opacity):
    """将Logo添加到图片上的核心函数"""
    try:
        # 复制基础图片
        base_img = base_image.copy().convert('RGBA')
        logo_img = logo_image.copy().convert('RGBA')
        
        # 计算Logo的实际尺寸（基于图片宽高的百分比）
        base_width, base_height = base_img.size
        logo_size = int(min(base_width, base_height) * (size_percent / 100))
        
        # 调整Logo大小
        logo_img.thumbnail((logo_size, logo_size), Image.Resampling.LANCZOS)
        
        # 调整Logo透明度
        if opacity < 255:
            alpha = logo_img.split()[3]
            alpha = alpha.point(lambda p: p * opacity // 255)
            logo_img.putalpha(alpha)
        
        # 计算Logo位置（基于百分比）
        logo_width, logo_height = logo_img.size
        x_pos = int((base_width - logo_width) * (x_percent / 100))
        y_pos = int((base_height - logo_height) * (y_percent / 100))
        
        # 创建透明图层用于放置Logo
        logo_layer = Image.new('RGBA', base_img.size, (0, 0, 0, 0))
        logo_layer.paste(logo_img, (x_pos, y_pos), logo_img)
        
        # 合并图片
        result = Image.alpha_composite(base_img, logo_layer)
        
        return result
    
    except Exception as e:
        st.error(f"添加Logo时发生错误: {e}")
        return None

def apply_preset_position(preset_name, base_width, base_height, logo_width, logo_height):
    """应用预设位置"""
    presets = {
        "左上角": (5, 5),
        "右上角": (95, 5),
        "左下角": (5, 95),
        "右下角": (95, 95),
        "居中": (50, 50),
        "顶部居中": (50, 5),
        "底部居中": (50, 95),
        "左侧居中": (5, 50),
        "右侧居中": (95, 50)
    }
    
    if preset_name in presets:
        return presets[preset_name]
    else:
        # 自定义位置，返回当前值
        return (st.session_state.logo_adder_logo_x, st.session_state.logo_adder_logo_y)

def batch_add_logo_to_images(images, logo_img, x_percent, y_percent, size_percent, opacity):
    """批量添加Logo到多张图片"""
    processed_images = []
    
    for i, img in enumerate(images):
        result = add_logo_to_image(img, logo_img, x_percent, y_percent, size_percent, opacity)
        if result:
            processed_images.append(result)
    
    return processed_images

def create_zip_from_images(images, original_names, output_format='PNG'):
    """从图片创建ZIP文件"""
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for i, (img, original_name) in enumerate(zip(images, original_names)):
            img_buffer = BytesIO()
            
            if output_format.upper() == 'JPG':
                # 转换RGBA为RGB
                if img.mode == 'RGBA':
                    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                    rgb_img.paste(img, mask=img.split()[3])
                    img = rgb_img
                img.save(img_buffer, format='JPEG', quality=95)
                ext = '.jpg'
            else:
                img.save(img_buffer, format='PNG')
                ext = '.png'
            
            img_buffer.seek(0)
            
            # 生成文件名
            name_without_ext = os.path.splitext(original_name)[0]
            filename = f"{name_without_ext}_with_logo_{i+1:03d}{ext}"
            
            zip_file.writestr(filename, img_buffer.getvalue())
    
    zip_buffer.seek(0)
    return zip_buffer

# ==================== 侧边栏设置区域 ====================
with st.sidebar:
    st.markdown("### ⚙️ 合成设置")
    
    # 1. Logo设置
    st.markdown('<div class="settings-title">🖼️ LOGO选择</div>', unsafe_allow_html=True)
    logo_color = st.radio(
        "",
        ["黑色Logo", "白色Logo"],
        horizontal=True,
        key="logo_color_select"
    )
    st.session_state.logo_color = logo_color
    
    st.markdown("---")
    
    # 2. 产品图最大边长
    st.markdown('<div class="settings-title">📐 产品图最大边长</div>', unsafe_allow_html=True)
    # 用自定义div包裹滑块，添加专属类名
    st.markdown('<div class="compact-slider">', unsafe_allow_html=True)
    product_size = st.slider(
        "",
        min_value=500, 
        max_value=1000, 
        value=800, 
        step=50,
        key="product_size_slider",
    )
    st.markdown('</div>', unsafe_allow_html=True)
    st.session_state.product_size = product_size
    
    # 删除产品图位置设置
    # 产品图位置固定为居中
    
    st.markdown("---")
    
    # 3. 背景遮罩设置
    st.markdown('<div class="settings-title">🎨 背景遮罩（可选颜色）</div>', unsafe_allow_html=True)
    
    # 遮罩开关
    dark_mask_enabled = st.checkbox(
        '添加背景遮罩层',
        value=st.session_state.get('dark_mask_enabled', False),
        help='在背景图上层添加颜色遮罩层，使产品图更突出',
        key='dark_mask_enabled_checkbox'
    )
    
    st.session_state.dark_mask_enabled = dark_mask_enabled
    
    # 遮罩设置（如果启用）
    if dark_mask_enabled:
        # 遮罩不透明度滑块
        mask_opacity = st.slider(
            '遮罩层不透明度',
            min_value=0,
            max_value=100,
            value=st.session_state.get('mask_opacity', 20),
            step=5,
            help='遮罩层的不透明度，值越大颜色越明显',
            key='mask_opacity_slider'
        )
        st.session_state.mask_opacity = mask_opacity
        
        # 颜色选择类型
        mask_color_type = st.radio(
            "颜色选择方式",
            ["预设颜色", "自定义颜色"],
            horizontal=True,
            index=0 if st.session_state.get('mask_color_type', '预设颜色') == '预设颜色' else 1,
            key='mask_color_type_radio'
        )
        st.session_state.mask_color_type = mask_color_type
        
        if mask_color_type == "预设颜色":
            # 当前选择的预设颜色
            current_preset = st.session_state.get('mask_preset_color', '白色')
            
            # 显示颜色预览
            current_hex = PRESET_COLORS[current_preset]
            current_rgb = hex_to_rgb(current_hex)
            
            # 显示颜色预览和选择器
            col1, col2 = st.columns([1, 3])
            with col1:
                # 颜色预览框
                brightness = get_color_brightness(current_rgb)
                text_color = "white" if brightness < 128 else "black"
                st.markdown(f"""
                <div class="color-preview-box" style="background-color: {current_hex}; color: {text_color};">
                    {current_preset[0]}
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # 颜色选择下拉框
                preset_options = list(PRESET_COLORS.keys())
                selected_preset = st.selectbox(
                    "选择预设颜色",
                    preset_options,
                    index=preset_options.index(current_preset) if current_preset in preset_options else 0,
                    key='mask_preset_select'
                )
                
                if selected_preset != st.session_state.get('mask_preset_color', '白色'):
                    st.session_state.mask_preset_color = selected_preset
                    st.session_state.mask_color_rgb = hex_to_rgb(PRESET_COLORS[selected_preset])
                    st.rerun()
        
        else:  # 自定义颜色
            # 自定义颜色选择器
            custom_color = st.color_picker(
                "选择遮罩颜色",
                value=st.session_state.get('mask_custom_color', '#FFFFFF'),
                key='mask_custom_color_picker'
            )
            
            if custom_color != st.session_state.get('mask_custom_color', '#FFFFFF'):
                st.session_state.mask_custom_color = custom_color
                st.session_state.mask_color_rgb = hex_to_rgb(custom_color)
                st.rerun()
            
            # 显示颜色预览
            current_hex = custom_color
            current_rgb = hex_to_rgb(custom_color)
            
            col1, col2 = st.columns([1, 3])
            with col1:
                brightness = get_color_brightness(current_rgb)
                text_color = "white" if brightness < 128 else "black"
                st.markdown(f"""
                <div class="color-preview-box" style="background-color: {current_hex}; color: {text_color};">
                    自定
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.caption(f"颜色值: {current_hex}")
                st.caption(f"RGB: {current_rgb}")
        
        # 更新当前颜色
        current_color = get_current_mask_color()
        current_hex = rgb_to_hex(current_color)
        
        # 显示遮罩信息（删除预览）
        color_name = st.session_state.mask_preset_color if st.session_state.mask_color_type == '预设颜色' else '自定义颜色'
        st.markdown(f"""
        <div class="mask-info">
            <strong>当前设置:</strong><br>
            • 颜色: {color_name} ({current_hex})<br>
            • 不透明度: {mask_opacity}%<br>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 4. 输出设置
    st.markdown('<div class="settings-title">📦 输出设置</div>', unsafe_allow_html=True)
    
    col_size1, col_size2 = st.columns(2)
    with col_size1:
        output_size = st.selectbox(
            "输出尺寸", 
            [400, 600, 800, 1000, 1200, 1500, 2000],
            index=2,
            key="output_size_select"
        )
        st.session_state.output_size = output_size
    with col_size2:
        output_format = st.radio(
            "输出格式", 
            ['JPG', 'PNG'],
            horizontal=True,
            key="output_format_radio"
        )
        st.session_state.output_format = output_format
    
    st.markdown("---")
    
    # 5. 处理按钮
    process_button = st.button(
        "开始智能批量合成", 
        type="primary", 
        use_container_width=True,

        key="process_button"
    )

    # 侧边栏 - 下载所有合成图片按钮（替换原有代码）
    st.markdown("---")
    # 严谨判断：是否有有效ZIP缓冲区和有效数据
    if st.session_state.synthesize_zip_buffer is not None and \
    st.session_state.synthesize_zip_buffer.getvalue() and \
    st.session_state.synthesize_zip_info:
        
        # 提取zip信息（避免键不存在报错）
        zip_output_format = st.session_state.synthesize_zip_info.get("output_format", "PNG")
        zip_output_size = st.session_state.synthesize_zip_info.get("output_size", "800")
        
        st.download_button(
            label=f"下载所有合成图片",
            data=st.session_state.synthesize_zip_buffer,
            file_name=f"产品图合成_{zip_output_size}px_{zip_output_format.lower()}.zip",
            mime="application/zip",
            use_container_width=True,
            key="download_synthesize_zip"
        )

# ==================== 主区域：标签页 ====================
# 修改为3个标签页，删除了AI文案功能
tab1, tab2, tab3 = st.tabs(["📤 产品图合成", "🎬 视频抽帧", "🖼️ LOGO水印添加"])

# ========== tab1 中 Unsplash 部分完整修正代码 ==========
with tab1:
    # 减小标题间距
    st.header("📤 产品图合成")
    st.markdown(
    """<div class="highlight-box">
        <p>上传合适的背景图或unsplash图库中搜索，再上传透明产品图，左侧合成带LOGO产品图</p>
    </div>""", unsafe_allow_html=True)    

    # 使用两列布局
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown("#### 背景图上传")
        
        # 背景来源选择选项卡 - 隐藏标签文字
        bg_source = st.radio(
            "",  # 空标签
            ["上传图片", "Unsplash图库"],
            horizontal=True,
            key="bg_source_radio",
            label_visibility="collapsed"  # 完全隐藏标签
        )
        
        if bg_source == "上传图片":
            # 上传背景图逻辑（保持不变）
            bg_files = st.file_uploader(
                "拖拽或选择背景图片",
                type=['png', 'jpg', 'jpeg'],
                accept_multiple_files=True,
                key="bg_upload",
                help="支持JPG/PNG格式",
                label_visibility="collapsed"
            )
            
            if bg_files:
                bg_count = len(bg_files)
                st.success(f"已上传 {bg_count} 张背景图")
                
                st.markdown("预览（最多显示12张）")
                
                cols_per_row = min(4, bg_count) if bg_count > 0 else 4
                preview_count = min(12, bg_count)
                
                for i in range(0, preview_count, cols_per_row):
                    cols = st.columns(cols_per_row)
                    for j in range(cols_per_row):
                        idx = i + j
                        if idx < preview_count:
                            with cols[j]:
                                file = bg_files[idx]
                                img = Image.open(file)
                                display_width = 150
                                ratio = display_width / img.width
                                display_height = int(img.height * ratio)
                                
                                display_img = img.copy()
                                display_img.thumbnail((display_width, display_height * 2), Image.Resampling.LANCZOS)
                                
                                st.image(
                                    display_img, 
                                    caption=file.name[:12] + "..." if len(file.name) > 12 else file.name,
                                    width=display_width
                                )
        
        else:  # Unsplash图库
            # 初始化Unsplash API（提前初始化，避免重复定义）
            unsplash_api = UnsplashAPI()
            
            # ===================== 关键修改1：先执行搜索/分页逻辑（在按钮渲染前） =====================
            # 1.1 读取session_state中的最新状态
            current_page = st.session_state.get('unsplash_current_page', 1)
            total_pages = st.session_state.get('unsplash_total_pages', 0)
            has_photos = len(st.session_state.get('unsplash_photos', [])) > 0
            search_query = st.session_state.get('unsplash_search_query', "white background")
            need_search = False

            # 1.2 处理搜索框内容变化（提前更新状态）
            temp_search_query = search_query  # 临时存储旧值，用于判断变化
            # 这里先不渲染搜索框，先准备好逻辑

            # 1.3 处理按钮点击的前置逻辑（通过session_state标记，避免提前渲染按钮）
            # 搜索触发标志判断
            if st.session_state.get('unsplash_search_trigger', False):
                need_search = True

            # 1.4 执行搜索逻辑（核心：在按钮渲染前完成状态更新）
            if need_search:
                if not unsplash_api.access_key:
                    st.error("⚠️ 未找到Unsplash API密钥，请在Streamlit Secrets中配置UNSPLASH_ACCESS_KEY")
                else:
                    photos, new_total_pages, total_results = unsplash_api.search_photos(
                        search_query, 
                        page=current_page, 
                        per_page=12
                    )
                    if photos:
                        # 关键：立即更新session_state，让后续按钮渲染能读取到最新状态
                        st.session_state.unsplash_photos = photos
                        st.session_state.unsplash_total_pages = new_total_pages
                        st.session_state.unsplash_total_results = total_results
                        # 更新本地变量，用于计算按钮禁用状态
                        total_pages = new_total_pages
                        has_photos = True
                    else:
                        if total_results == 0:
                            st.warning(f"未找到与'{search_query}'相关的图片")
                        else:
                            st.error("搜索失败，请尝试其他关键词")
                    # 重置搜索触发标志
                    st.session_state.unsplash_search_trigger = False

            # ===================== 恢复你原有布局：渲染搜索框+按钮（无任何新增） =====================
            # 1. 先渲染搜索框和按钮（完全和你原有代码一致）
            st.markdown('<div class="search-container">', unsafe_allow_html=True)
            
            # 使用两列布局：搜索框和按钮
            search_col1, search_col2 = st.columns([3, 2])
            
            with search_col1:
                search_query = st.text_input(
                    label="",  # 空标签
                    value=search_query,
                    placeholder="例如：white background",
                    help="输入英文关键词",
                    label_visibility="collapsed",  # 隐藏标签
                    key="unsplash_search_input"
                )
            
            with search_col2:
                # 搜索和翻页按钮在同一行（完全和你原有代码一致）
                btn_col1, btn_col2, btn_col3 = st.columns(3)
                with btn_col1:
                    # 先定义搜索按钮
                    search_btn = st.button(
                        "搜索", 
                        type="primary", 
                        key="search_unsplash",
                        use_container_width=True
                    )
                
                with btn_col2:
                    # 关键修改2：基于最新状态计算禁用条件（搜索逻辑已执行，状态是最新的）
                    prev_disabled = not has_photos or current_page <= 1
                    prev_label = "◀上一页"
                    prev_btn = st.button(prev_label, key="unsplash_prev", use_container_width=True, disabled=prev_disabled)

                with btn_col3:
                    # 关键修改3：优化下一页禁用条件（基于最新的total_pages）
                    # 修复核心：搜索逻辑已执行，total_pages是最新的，不会再误判
                    next_disabled = False
                    if not has_photos:
                        next_disabled = True
                    elif total_pages == 0:
                        next_disabled = True
                    elif current_page >= total_pages:
                        next_disabled = True
                    
                    next_label = "下一页▶"
                    next_btn = st.button(next_label, key="unsplash_next", use_container_width=True, disabled=next_disabled)

            st.markdown('</div>', unsafe_allow_html=True)
            
            # ===================== 处理按钮点击事件（完全和你原有代码一致） =====================
            # 搜索按钮点击
            if search_btn:
                if not unsplash_api.access_key:
                    st.error("请先配置Unsplash API密钥")
                else:
                    # 重置到第一页
                    st.session_state.unsplash_current_page = 1
                    st.session_state.unsplash_search_query = search_query
                    st.session_state.unsplash_search_trigger = True
                    # 关键：强制重运行，让搜索逻辑立即执行
                    st.rerun()
            
            # 上一页按钮点击
            if prev_btn and not prev_disabled:
                st.session_state.unsplash_current_page -= 1
                st.session_state.unsplash_search_trigger = True
                st.rerun()
            
            # 下一页按钮点击
            if next_btn and not next_disabled:
                st.session_state.unsplash_current_page += 1
                st.session_state.unsplash_search_trigger = True
                st.rerun()
            
            # ===================== 显示搜索结果（完全和你原有代码一致，无修改） =====================
            if st.session_state.unsplash_photos:
                # 显示当前页信息
                total_pages = st.session_state.get('unsplash_total_pages', 0)
                current_page = st.session_state.get('unsplash_current_page', 1)
                total_results = st.session_state.get('unsplash_total_results', 0)

                photos = st.session_state.unsplash_photos
                
                # 每排6个，显示2排（共12个）
                rows = 2
                cols_per_row = 6

                for row in range(rows):
                    # 创建6列
                    columns = st.columns(cols_per_row)
                    
                    for col in range(cols_per_row):
                        idx = row * cols_per_row + col
                        if idx < len(photos):
                            with columns[col]:
                                photo = photos[idx]
                                img_url = photo.get("urls", {}).get("small")
                                
                                if img_url:
                                    # 判断当前图片是否为选中状态
                                    is_selected = (st.session_state.unsplash_selected_page == current_page) and \
                                                (st.session_state.unsplash_selected_idx == idx)
                                    
                                    # 1. 显示图片（无点击功能）使用CSS实现1:1裁剪
                                    st.markdown(f"""
                                    <div class="unsplash-square-container">
                                        <img src="{img_url}" alt="Unsplash图片" class="unsplash-square-image">
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    # 2. 显示选择按钮
                                    button_key = f"unsplash_select_{current_page}_{idx}"
                                    button_text = "已选择" if is_selected else "选择"
                                    
                                    # 3. 创建选择按钮（白色背景/绿色背景）
                                    if st.button(
                                        button_text,
                                        key=button_key,
                                        use_container_width=True,
                                        type="primary" if is_selected else "secondary"
                                    ):
                                        # 1. 静默更新选中状态（无任何页面输出）
                                        st.session_state.unsplash_selected_page = current_page
                                        st.session_state.unsplash_selected_idx = idx
                                        
                                        # 2. 静默下载图片（无spinner提示）
                                        img = unsplash_api.download_photo(img_url)
                                        if img:
                                            class MockFile:
                                                def __init__(self, img, idx, page):
                                                    self.name = f"unsplash_bg_{page}_{idx}.jpg"
                                                    self.type = "image/jpeg"
                                                    self.image = img
                                                    self.idx = idx
                                                    self.page = page
                                            
                                            mock_file = MockFile(img, idx, current_page)
                                            st.session_state.unsplash_selected_bg = mock_file
                                        
                                        # 3. 静默刷新页面（无成功提示）
                                        st.rerun()

    with col2:
        # 产品图上传逻辑（完整补全，解决 uploaded_products 未定义错误）
        st.markdown("#### 产品图上传")
        
        # 占位单选按钮（保持你的原有布局，无需修改）
        with st.container():
            st.radio(
                "",
                ["上传图片"],
                horizontal=True,
                key="product_source_radio",
                disabled=True,
                label_visibility="collapsed"
            )
        
        # ✅ 核心：先定义并赋值 uploaded_products（这行是你缺失的，解决 NameError）
        uploaded_products = st.file_uploader(
            "拖拽或选择产品图片",
            type=['png', 'jpg', 'jpeg'],
            accept_multiple_files=True,
            key="product_upload",
            help="建议使用透明背景的PNG图片",
            label_visibility="collapsed"
        )
        
        # ✅ 后续的判断和持久化逻辑（保持不变，现在变量已定义，不会报错）
        # 1. 初始化产品图持久化 session_state（若未初始化）
        if 'persist_product_files' not in st.session_state:
            st.session_state.persist_product_files = []
        
        # 2. 若有新的上传数据，更新到 session_state 持久化
        if uploaded_products is not None and len(uploaded_products) > 0:
            st.session_state.persist_product_files = uploaded_products
        
        # 3. 从 session_state 读取持久化的产品图数据
        product_files = st.session_state.persist_product_files
        
        # 4. 产品图预览（保持你的1行6列紧凑布局，无需修改）
        if product_files:
            product_count = len(product_files)
            st.success(f"已上传 {product_count} 张产品图（仅显示前6张）")
            
            preview_count = min(6, product_count)
            cols = st.columns(preview_count, gap="small")
            
            for idx in range(preview_count):
                with cols[idx]:
                    file = product_files[idx]
                    img = Image.open(file)
                    
                    display_width = 120
                    display_img = img.copy()
                    display_img.thumbnail((display_width, display_width), Image.Resampling.LANCZOS)
                    
                    st.image(
                        display_img,
                        caption=file.name[:10] + "..." if len(file.name) > 10 else file.name,
                        width=display_width
                    )
            
            if product_count > 6:
                st.caption(f"")

    # 上传状态汇总
    bg_files_combined = []
    
    if 'bg_files' in locals() and bg_files:
        bg_files_combined.extend(bg_files)
    
    if 'unsplash_selected_bg' in st.session_state and st.session_state.unsplash_selected_bg:
        bg_files_combined.append(st.session_state.unsplash_selected_bg)
    
    if bg_files_combined and product_files:
        total_combinations = len(bg_files_combined) * len(product_files)
        st.info(f"准备合成 {len(bg_files_combined)} 张背景图 × {len(product_files)} 张产品图 = {total_combinations} 张合成图")

    # ==================== 合成结果预览区域（仅在tab1显示） ====================
    if "synthesize_preview_images" in st.session_state and st.session_state.synthesize_preview_images:
        st.markdown("---")
        st.subheader("合成结果预览")
        preview_images = st.session_state.synthesize_preview_images
        total_previews = len(preview_images)
        
        # 核心修改：最多显示10张，1行10列，紧凑布局
        preview_count = min(10, total_previews)  # 数量限制改为10
        cols = st.columns(preview_count, gap="small")  # 列数对应10列，保持小间距
        
        st.write(f"共生成 {len(preview_images)} 张图片，仅显示前 {preview_count} 张")
        
        for idx in range(preview_count):
            with cols[idx]:
                preview_data = preview_images[idx]
                img = Image.open(preview_data["data"])
                
                # 优化：缩小图片宽度到110px，保证10张图不超出页面，紧凑显示
                display_width = 110
                display_img = img.copy()
                display_img.thumbnail((display_width, display_width), Image.Resampling.LANCZOS)
                
                st.image(
                    display_img,
                    caption=preview_data["filename"][:10] + "..." if len(preview_data["filename"]) > 10 else preview_data["filename"],
                    width=display_width
                )
        
        # 修改提示：超出10张时的提示
        if total_previews > 10:
            st.caption(f"📌 可下载ZIP包查看全部{total_previews}张图片")
    elif st.session_state.synthesize_zip_buffer is not None:
        st.markdown("---")
        st.subheader("合成结果预览")
        st.info("✅ 合成完成！可下载ZIP包查看全部图片")

# 标签页2：视频抽帧
with tab2:
    st.header("🎬 视频抽帧")
    st.markdown(
    """<div class="highlight-box">
        <p>通过随机删除视频中的两帧，生成内容相似但数据不同的新视频，可用于应对平台的重复检测。</p>
    </div>""", unsafe_allow_html=True)
    
    # 使用两列布局
    col_left_video, col_right_video = st.columns([1, 1], gap="large")
    
    with col_left_video:
        st.markdown("#### 1. 上传视频")
        video_file = st.file_uploader(
            "选择需要处理的视频", 
            type=['mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv'], 
            key="video_uploader",
            help="支持MP4、AVI、MOV、MKV等常见视频格式",
            label_visibility="collapsed"
        )
        
        if video_file:
            # 保存上传的视频到临时文件
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
                tmp_file.write(video_file.getvalue())
                temp_video_path = tmp_file.name
            
            # 显示视频信息
            try:
                cap = cv2.VideoCapture(temp_video_path)
                if cap.isOpened():
                    fps = cap.get(cv2.CAP_PROP_FPS)
                    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    duration = total_frames / fps if fps > 0 else 0
                    cap.release()
                    
                    st.markdown("视频信息")
                    st.markdown(f"""
                    <div class="video-info-card">
                        <div class="video-info-title">📊 视频详情</div>
                        <div class="video-info-text">
                            • 文件名: {video_file.name}<br>
                            • 分辨率: {width} × {height}<br>
                            • 帧率: {fps:.2f} FPS<br>
                            • 总帧数: {total_frames} 帧<br>
                            • 时长: {duration:.2f} 秒<br>
                            • 文件大小: {video_file.size / (1024*1024):.2f} MB
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 预览视频
                    st.markdown("视频预览")
                    st.video(video_file)
                else:
                    st.warning("无法读取视频信息，请检查视频格式是否支持。")
            except Exception as e:
                st.error(f"读取视频信息时出错: {e}")
    
    with col_right_video:
        if video_file:
            st.markdown("#### 2. 处理设置")
            
            # 显示处理说明
            st.info(
            """处理说明：
            - 工具将随机删除视频中的两帧
            - 保留原始音频和画质
            - 输出视频时长几乎不变
            - 适合用于应对平台重复检测"""
            )
            
            # 处理按钮
            if st.button("🎬 开始视频抽帧处理", type="primary", use_container_width=True, key="process_video"):
                with st.spinner('正在处理视频...'):
                    # 创建进度条和状态文本
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # 生成输出文件名
                    output_filename = f"{os.path.splitext(video_file.name)[0]}_抽帧版.mp4"
                    
                    try:
                        # 调用视频处理函数
                        output_path, video_info, frames_removed, saved_frames = remove_random_frames(
                            temp_video_path, output_filename, progress_bar, status_text
                        )
                        
                        # 更新进度条
                        progress_bar.progress(1.0)
                        status_text.empty()
                        
                        # 读取处理后的视频文件
                        with open(output_path, 'rb') as f:
                            video_data = f.read()
                        
                        # 保存到session_state
                        st.session_state.processed_video = video_data
                        st.session_state.video_info = {
                            "original_info": video_info,
                            "frames_removed": frames_removed,
                            "saved_frames": saved_frames,
                            "output_filename": output_filename
                        }
                        
                        st.success(f"✅ 视频处理完成！")
                        
                        # 显示处理结果信息
                        st.markdown("#### 处理结果")
                        st.markdown(f"""
                        <div class="video-info-card">
                            <div class="video-info-title">✅ 处理成功</div>
                            <div class="video-info-text">
                                • 删除的帧: 第 {frames_removed[0]} 帧和第 {frames_removed[1]} 帧<br>
                                • 原视频帧数: {video_info['total_frames']} 帧<br>
                                • 新视频帧数: {saved_frames} 帧<br>
                                • 删除帧数: {video_info['total_frames'] - saved_frames} 帧<br>
                                • 分辨率: {video_info['width']} × {video_info['height']}<br>
                                • 帧率: {video_info['fps']:.2f} FPS<br>
                                • 时长: {video_info['duration']:.2f} 秒
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # 预览处理后的视频
                        st.markdown("处理后的视频预览")
                        st.video(video_data)
                        
                    except Exception as e:
                        progress_bar.empty()
                        status_text.empty()
                        st.error(f"处理视频时出错: {e}")
                    finally:
                        # 清理临时文件
                        if os.path.exists(temp_video_path):
                            os.unlink(temp_video_path)
                        if os.path.exists(output_filename):
                            os.unlink(output_filename)
            
            # 显示下载按钮（如果已处理）
            if st.session_state.processed_video and st.session_state.video_info:
                st.markdown("#### 3. 下载结果")
                
                # 获取信息
                video_info = st.session_state.video_info
                output_filename = video_info["output_filename"]
                
                # 下载按钮
                st.download_button(
                    label=f"📥 下载处理后的视频 ({output_filename})",
                    data=st.session_state.processed_video,
                    file_name=output_filename,
                    mime="video/mp4",
                    use_container_width=True,
                    key="download_video"
                )
                
                # 批量处理选项
                st.markdown("---")
                st.markdown("#### 🔄 批量处理")
                
                if st.button("🔄 使用相同设置处理另一个视频", key="process_another"):
                    # 重置状态
                    st.session_state.processed_video = None
                    st.session_state.video_info = None
                    st.rerun()

# 标签页3：Logo水印添加
with tab3:
    # 预设位置映射表
    preset_map = {
        "左上角": (5, 5),
        "右上角": (95, 5),
        "左下角": (5, 95),
        "右下角": (95, 95),
        "居中": (50, 50),
        "顶部居中": (50, 5),
        "底部居中": (50, 95),
        "左侧居中": (5, 50),
        "右侧居中": (95, 50)
    }
    
    st.header("🖼️ Logo水印添加")
    st.markdown(
    """<div class="highlight-box">
        <p>为单张图片添加LOGO水印，支持自定义LOGO位置、大小和透明度。</p>
    </div>""", unsafe_allow_html=True)
    
    # 使用三列布局
    col_left, col_middle, col_right = st.columns([1, 1, 2], gap="medium")
    
    with col_left:
        st.markdown("### 1. 上传图片")
        
        # 上传图片 - 单张模式
        uploaded_image = st.file_uploader(
            "选择需要添加Logo的图片",
            type=['png', 'jpg', 'jpeg'],
            accept_multiple_files=False,
            key="logo_adder_uploader",
            help="支持JPG和PNG格式，单张处理模式",
            label_visibility="collapsed"
        )
        
        if uploaded_image:
            # 保存到session_state
            st.session_state.logo_adder_image = uploaded_image
            
            # 显示上传状态
            st.success("已上传图片")
            
            # 显示原图信息
            img = Image.open(uploaded_image)
            st.markdown("原图信息")
            st.caption(f"文件名: {uploaded_image.name}")
            st.caption(f"尺寸: {img.width} × {img.height} 像素")
            st.caption(f"格式: {uploaded_image.type}")
    
    with col_middle:
        st.markdown("### 2. Logo设置")
        
        # Logo颜色选择
        st.markdown("Logo颜色")
        logo_color = st.radio(
            "",
            ["黑色Logo", "白色Logo"],
            index=0 if st.session_state.logo_adder_logo_color == "黑色Logo" else 1,
            horizontal=True,
            key="logo_adder_color_radio",
            label_visibility="collapsed"
        )
        st.session_state.logo_adder_logo_color = logo_color
        
        # Logo透明度设置
        st.markdown("Logo透明度")
        opacity = st.slider(
            "",
            min_value=0,
            max_value=255,
            value=st.session_state.logo_adder_logo_opacity,
            step=5,
            help="0为完全透明，255为完全不透明",
            key="logo_adder_opacity_slider",
            label_visibility="collapsed"
        )
        st.session_state.logo_adder_logo_opacity = opacity
        st.markdown(f"当前值: {int(opacity/255*100)}%")
        
        # Logo大小设置
        st.markdown("Logo大小")
        size = st.slider(
            "",
            min_value=5,
            max_value=200,
            value=st.session_state.logo_adder_logo_size,
            step=5,
            help="Logo相对于图片宽高的百分比",
            key="logo_adder_size_slider",
            label_visibility="collapsed"
        )
        st.session_state.logo_adder_logo_size = size
        st.markdown(f"当前值: {size}%")
    
    with col_right:
        st.markdown("### 3. 位置设置")
        
        # 预设位置
        st.markdown("预设位置")
        
        preset_options = ["自定义", "左上角", "右上角", "左下角", "右下角", "居中", "顶部居中", "底部居中", "左侧居中", "右侧居中"]
        
        # 预设选择框
        selected_preset = st.selectbox(
            "选择预设位置",
            preset_options,
            index=preset_options.index(st.session_state.logo_adder_preset_position) if st.session_state.logo_adder_preset_position in preset_options else 0,
            key="preset_selectbox",
            help="选择预设位置或使用自定义位置"
        )
        
        # 当预设位置改变时更新坐标
        if selected_preset != st.session_state.logo_adder_preset_position:
            st.session_state.logo_adder_preset_position = selected_preset
            
            if selected_preset in preset_map and selected_preset != "自定义":
                x, y = preset_map[selected_preset]
                st.session_state.logo_adder_logo_x = x
                st.session_state.logo_adder_logo_y = y
                # 强制重新运行以更新滑块
                st.rerun()
        
        # 自定义位置
        st.markdown("自定义位置")
        
        col_x, col_y = st.columns(2)
        with col_x:
            x_pos = st.slider(
                "X轴位置 (%)",
                min_value=0,
                max_value=100,
                value=st.session_state.logo_adder_logo_x,
                step=1,
                key="logo_adder_x_slider"
            )
            st.session_state.logo_adder_logo_x = x_pos
        
        with col_y:
            y_pos = st.slider(
                "Y轴位置 (%)",
                min_value=0,
                max_value=100,
                value=st.session_state.logo_adder_logo_y,
                step=1,
                key="logo_adder_y_slider"
            )
            st.session_state.logo_adder_logo_y = y_pos
        
        # 显示当前位置和预设状态
        current_preset = "自定义"
        for preset, (preset_x, preset_y) in preset_map.items():
            if x_pos == preset_x and y_pos == preset_y:
                current_preset = preset
                break
        
        st.info(f"📍 当前位置: X={x_pos}%, Y={y_pos}% | 预设: {current_preset}")
        
        # 处理按钮和下载逻辑
        if uploaded_image:
            # 加载Logo图片
            logo_path = None
            if st.session_state.logo_adder_logo_color == "黑色Logo":
                logo_path = "logos/b_logo.png"
            else:
                logo_path = "logos/w_logo.png"
            
            # 检查Logo文件是否存在
            logo_exists = os.path.exists(logo_path)
            
            if not logo_exists:
                st.warning(f"⚠️ 未找到Logo文件: {logo_path}")
                st.warning("请在 logos 文件夹中提供 b_logo.png 和 w_logo.png 文件")
            else:
                # 加载Logo
                logo_img = Image.open(logo_path)
                st.session_state.logo_adder_logo_image = logo_img
                
                # 处理图片
                original_img = Image.open(uploaded_image)
                processed_result = add_logo_to_image(
                    original_img,
                    logo_img,
                    st.session_state.logo_adder_logo_x,
                    st.session_state.logo_adder_logo_y,
                    st.session_state.logo_adder_logo_size,
                    st.session_state.logo_adder_logo_opacity
                )
                
                if processed_result:
                    # 保存处理后的结果到session_state
                    st.session_state.logo_adder_processed_result = processed_result
                    
                    # 实时预览区域 - 放大预览
                    st.markdown("### 4. 实时预览")
                    
                    # 计算显示尺寸 - 放大预览
                    display_width = 600  # 放大预览尺寸
                    
                    # 获取原始图片尺寸
                    original_width, original_height = processed_result.size
                    
                    # 计算按比例缩放的高度
                    display_height = int(original_height * (display_width / original_width))
                    
                    # 创建高质量的预览图
                    preview_img = processed_result.copy()
                    preview_img.thumbnail((display_width, display_height), Image.Resampling.LANCZOS)
                    
                    # 显示放大预览
                    st.image(preview_img, caption="添加Logo后的效果预览", use_column_width=True)
                    
                    # 添加Logo位置标记
                    logo_width = int(min(original_width, original_height) * (st.session_state.logo_adder_logo_size / 100))
                    logo_x = int((original_width - logo_width) * (st.session_state.logo_adder_logo_x / 100))
                    logo_y = int((original_height - logo_width) * (st.session_state.logo_adder_logo_y / 100))
                    
                    # 显示Logo位置信息
                    st.caption(f"原图尺寸: {original_width} × {original_height} 像素")
                    st.caption(f"Logo位置: X={logo_x}px, Y={logo_y}px | 大小: {logo_width}px × {logo_width}px | 透明度: {int(st.session_state.logo_adder_logo_opacity/255*100)}%")
                    
                    # 下载按钮 - 直接下载单张JPG
                    st.markdown("### 5. 下载结果")
                    
                    # 将处理结果转换为JPG格式
                    jpg_buffer = BytesIO()
                    
                    # 如果是RGBA模式，转换为RGB
                    if processed_result.mode == 'RGBA':
                        rgb_img = Image.new('RGB', processed_result.size, (255, 255, 255))
                        rgb_img.paste(processed_result, mask=processed_result.split()[3])
                        result_to_save = rgb_img
                    else:
                        result_to_save = processed_result
                    
                    # 保存为JPG，高质量
                    result_to_save.save(jpg_buffer, format='JPEG', quality=95)
                    jpg_buffer.seek(0)
                    
                    # 生成下载文件名
                    original_name = os.path.splitext(uploaded_image.name)[0]
                    download_filename = f"{original_name}_with_logo.jpg"
                    
                    # 显示文件大小信息
                    file_size_kb = len(jpg_buffer.getvalue()) / 1024
                    st.info(f"文件大小: {file_size_kb:.1f} KB | 格式: JPG | 质量: 95%")
                    
                    # 下载按钮
                    st.download_button(
                        label="📥 下载处理后的图片 (JPG格式)",
                        data=jpg_buffer,
                        file_name=download_filename,
                        mime="image/jpeg",
                        use_container_width=True,
                        key="download_logo_adder"
                    )
                    
                    # 添加快捷提示
                    st.markdown("---")
                    col_tip1, col_tip2, col_tip3 = st.columns(3)
                    with col_tip1:
                        st.markdown("💡 小贴士")
                        st.caption("• 调整设置后实时预览")
                    with col_tip2:
                        st.markdown("⚡ 快速操作")
                        st.caption("• 使用预设位置快速定位")
                    with col_tip3:
                        st.markdown("🔧 高级设置")
                        st.caption("• 自定义位置精确定位")
        
        else:
            # 未上传图片时的提示
            st.markdown("### 4. 预览区域")
            st.markdown('<div class="logo-adder-preview">', unsafe_allow_html=True)
            st.markdown(
            """<div style="text-align: center; padding: 2rem; color: #666;">
                <h4>👈 请先在左侧上传图片</h4>
                <p>上传图片后，可以调整Logo设置并实时预览效果</p>
                <p>支持单张图片处理，直接下载JPG格式</p>
            </div>""", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

# ==================== 执行批处理 ====================
if process_button:
    # 检查必要文件
    # 获取所有背景文件（包括上传的和Unsplash的）
    bg_files_combined = []
    
    # 获取上传的背景文件
    if 'bg_files' in locals() and bg_files:
        bg_files_combined.extend(bg_files)
    
    # 获取Unsplash选择的背景文件
    if 'unsplash_selected_bg' in st.session_state and st.session_state.unsplash_selected_bg:
        bg_files_combined.append(st.session_state.unsplash_selected_bg)
    
    # ✅ 核心修改：从session_state中读取持久化的产品图
    product_files = st.session_state.persist_product_files

    if not bg_files_combined:
        st.error("请至少上传一张背景图或从Unsplash图库选择一张背景。")
        st.stop()
    if not product_files:
        st.error("请至少上传一张产品图。")
        st.stop()
    
    # 获取Logo图像对象
    logo_to_use = None
    logo_path = None
    
    # 从session_state获取设置值
    logo_color = st.session_state.get('logo_color', '黑色Logo')
    product_size = st.session_state.get('product_size', 600)
    output_size = st.session_state.get('output_size', 800)
    output_format = st.session_state.get('output_format', 'JPG')
    
    # 获取遮罩设置
    dark_mask_enabled = st.session_state.get('dark_mask_enabled', False)
    mask_opacity = st.session_state.get('mask_opacity', 20)
    mask_color_rgb = st.session_state.get('mask_color_rgb', (255, 255, 255))  # 默认白色
    
    if logo_color == '黑色Logo':
        logo_path = "logos/black_logo.png"
    else:
        logo_path = "logos/white_logo.png"
    
    if os.path.exists(logo_path):
        logo_to_use = Image.open(logo_path)
    else:
        st.warning(f"⚠️ 未找到{logo_color}文件：{logo_path}")
        st.warning("请在 logos 文件夹中提供 black_logo.png 和 white_logo.png 文件")
        logo_to_use = None
    
    # 显示遮罩状态
    if dark_mask_enabled:
        mask_hex = rgb_to_hex(mask_color_rgb)
        mask_color_name = st.session_state.get('mask_preset_color', '自定义颜色')
        st.info(f"🖌️ 背景遮罩已启用 | 颜色: {mask_color_name} ({mask_hex}) | 不透明度: {mask_opacity}%")
    
    # 创建临时目录存放结果
    with tempfile.TemporaryDirectory() as tmpdir:
        output_files = []
        # ✅ 关键修正：在使用前初始化 preview_images 为空列表（必须在循环外层）
        preview_images = []  # 这一行是解决 NameError 的核心，不能缺失

        total = len(bg_files_combined) * len(product_files)
        
        # 进度条
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        processed = 0
        for i, bg_file in enumerate(bg_files_combined):
            # 处理背景文件（可能是上传的文件或Unsplash文件）
            if hasattr(bg_file, 'read'):  # 上传的文件
                bg_image = Image.open(bg_file)
            elif hasattr(bg_file, 'image'):  # Unsplash文件
                bg_image = bg_file.image
            else:
                continue
            
            for j, product_file in enumerate(product_files):
                product_image = Image.open(product_file)
                
                # 更新进度
                processed += 1
                progress = processed / total
                progress_bar.progress(progress)
                status_text.text(f"正在处理 {processed}/{total} ({progress*100:.1f}%)")
                
                # 调用合成函数（添加遮罩参数，产品图位置固定为居中）
                result = compose_image(
                    bg_image, product_image, logo_to_use,
                    product_size, output_size, output_format,
                    mask_enabled=dark_mask_enabled,
                    mask_color=mask_color_rgb,
                    mask_opacity=mask_opacity
                )
                
                # 保存结果
                if hasattr(bg_file, 'name'):
                    bg_name = os.path.splitext(bg_file.name)[0]
                else:
                    bg_name = f"unsplash_bg_{i}"
                
                output_filename = f"{bg_name}_{os.path.splitext(product_file.name)[0]}.{output_format.lower()}"
                output_path = os.path.join(tmpdir, output_filename)
                
                if output_format.upper() == 'JPG':
                    result.save(output_path, format='JPEG', quality=95)
                else:
                    result.save(output_path, format='PNG')
                
                output_files.append(output_path)

                # ✅ 关键：保存前24张图片到预览列表
                if len(preview_images) < 24:
                    img_buffer = BytesIO()
                    if output_format.upper() == 'JPG':
                        # RGBA转RGB避免黑底
                        if result.mode == 'RGBA':
                            rgb_img = Image.new('RGB', result.size, (255, 255, 255))
                            rgb_img.paste(result, mask=result.split()[3])
                            rgb_img.save(img_buffer, format='JPEG', quality=90)
                        else:
                            result.save(img_buffer, format='JPEG', quality=90)
                    else:
                        result.save(img_buffer, format='PNG')
                    img_buffer.seek(0)
                    preview_images.append({
                        "data": img_buffer,
                        "filename": output_filename
                    })
        
        # ✅ 保存预览数据到session_state
        st.session_state.synthesize_preview_images = preview_images

        progress_bar.empty()
        status_text.empty()
        
        # 打包所有文件为ZIP
        st.toast(
            f"✅ 合成完成！共生成 {len(output_files)} 张图片。",
            icon="✅",  # 可选，添加图标更美观
            duration=1  # 显示3秒后自动消失，可调整（如2/4秒）
        )
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file_path in output_files:
                zip_file.write(file_path, os.path.basename(file_path))
        
        zip_buffer.seek(0)
        # 打包所有文件为ZIP之后，添加这行保存到session_state
        st.session_state.synthesize_zip_buffer = zip_buffer
        st.session_state.synthesize_zip_info = {
            "output_size": output_size,
            "output_format": output_format
        }
        st.rerun()

# ==================== 页脚信息 ====================

st.markdown("---")
st.caption("© 2026 骏泰素材工作台")
