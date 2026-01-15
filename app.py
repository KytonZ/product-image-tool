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
import time
import logging

# 设置页面配置
st.set_page_config(
    page_title="骏泰素材工作台", 
    page_icon="🎨", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 自定义CSS优化UI
def get_custom_css():
    return """
    <style>
        /* 全局字体和间距优化 */
        .stApp {
            font-family: 'Microsoft YaHei', 'Segoe UI', sans-serif;
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
        
        /* Unsplash图片卡片样式 */
        .unsplash-card {
            position: relative;
            width: 100%;
            margin-bottom: 12px;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            overflow: hidden;
            background: white;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .unsplash-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            border-color: #2196F3;
        }
        
        .unsplash-img-container {
            width: 100%;
            height: 140px;
            overflow: hidden;
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }
        
        /* 统一的按钮样式 */
        .stButton > button {
            border-radius: 6px;
            padding: 6px 12px;
            font-size: 12px;
            transition: all 0.2s;
            border: 1px solid #d1d5db;
        }
        
        .stButton > button:hover {
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        /* 侧边栏优化 */
        section[data-testid="stSidebar"] {
            min-width: 280px !important;
            max-width: 320px !important;
        }
        
        /* 紧凑网格布局 */
        .compact-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 12px;
            margin-top: 1rem;
        }
        
        /* 加载状态 */
        .loading-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(255, 255, 255, 0.9);
            z-index: 9999;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            color: #666;
        }
        
        .spinner {
            width: 40px;
            height: 40px;
            border: 4px solid #f3f3f3;
            border-top: 4px solid #2196F3;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 10px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* 状态消息 */
        .status-success {
            background-color: #d4edda;
            color: #155724;
            padding: 8px;
            border-radius: 4px;
            border-left: 4px solid #28a745;
            margin: 8px 0;
        }
        
        /* 图片标签 */
        .image-label {
            font-size: 11px;
            color: #666;
            margin-top: 4px;
            text-align: center;
            word-break: break-all;
            line-height: 1.2;
        }
        
        /* 分隔线 */
        .divider {
            margin: 16px 0;
            border-top: 1px solid #e0e0e0;
        }
        
        /* 提示框 */
        .hint-box {
            background-color: #e8f4fd;
            border-left: 4px solid #2196F3;
            padding: 12px;
            border-radius: 6px;
            margin-bottom: 16px;
        }
    </style>
    """

# 应用CSS样式
st.markdown(get_custom_css(), unsafe_allow_html=True)

# 页面标题
st.markdown('<h1 class="main-header">🎨 骏泰素材工作台</h1>', unsafe_allow_html=True)
st.markdown("---")

# ==================== 会话状态初始化 ====================
def init_session_state():
    """初始化所有会话状态"""
    # 基础状态
    defaults = {
        'current_page': 0,
        'processed_images': [],
        'last_zip_buffer': None,
        'processed_video': None,
        'video_info': None,
        
        # 产品图合成相关
        'logo_color': '黑色Logo',  # 添加这个！
        'product_size': 800,
        'output_size': 800,
        'output_format': 'JPG',
        'dark_mask_enabled': False,
        'mask_opacity': 20,
        'mask_color_type': "预设颜色",
        'mask_preset_color': "白色",
        'mask_custom_color': "#FFFFFF",
        'mask_color_rgb': (255, 255, 255),
        
        # Unsplash相关
        'unsplash_photos': [],
        'unsplash_selected_bg': None,
        'unsplash_search_query': "white background",
        'unsplash_search_trigger': False,
        'unsplash_current_page': 1,
        'unsplash_total_pages': 0,
        'unsplash_total_results': 0,
        
        # Logo水印添加相关
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
        
        # 加载状态
        'is_loading': False,
        'selected_photo_index': None,
        'selected_photo_page': None,
        'background_download_task': None,
        'unsplash_selected_bg_file': None,
        'last_action_time': 0,
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

# 初始化会话状态
init_session_state()

# ==================== 辅助函数 ====================
def safe_update_state(key, value):
    """安全更新状态，避免频繁更新"""
    current_time = time.time()
    last_update_key = f'last_update_{key}'
    
    # 防止0.5秒内多次更新
    if current_time - st.session_state.get(last_update_key, 0) > 0.5:
        st.session_state[key] = value
        st.session_state[last_update_key] = current_time
        return True
    return False

def show_loading(message="正在处理..."):
    """显示加载状态"""
    st.session_state.is_loading = True
    loading_html = f"""
    <div class="loading-overlay">
        <div style="text-align: center;">
            <div class="spinner"></div>
            <div>{message}</div>
        </div>
    </div>
    """
    return loading_html

def hide_loading():
    """隐藏加载状态"""
    st.session_state.is_loading = False

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
        hex_color = st.session_state.mask_custom_color
        return hex_to_rgb(hex_color)

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

# ==================== Unsplash API类 - 优化版 ====================
class UnsplashAPI:
    def __init__(self):
        try:
            self.access_key = st.secrets["UNSPLASH_ACCESS_KEY"]
        except:
            self.access_key = ""
            st.warning("⚠️ 未找到Unsplash API密钥，请在Streamlit Secrets中配置UNSPLASH_ACCESS_KEY")
        
        self.base_url = "https://api.unsplash.com"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        if self.access_key:
            self.session.headers.update({
                "Authorization": f"Client-ID {self.access_key}"
            })
    
    def search_photos(self, query, page=1, per_page=12):
        """搜索Unsplash图片 - 增强版本"""
        if not self.access_key:
            return [], 0, 0
        
        url = f"{self.base_url}/search/photos"
        params = {
            "query": query,
            "page": page,
            "per_page": per_page,
            "orientation": "squarish",
        }
        
        try:
            response = self.session.get(url, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                total = data.get("total", 0)
                total_pages = data.get("total_pages", 0)
                
                # 计算总页数
                if total_pages == 0 and total > 0:
                    total_pages = (total + per_page - 1) // per_page
                
                logger.info(f"Unsplash搜索成功: {len(results)}张图片, 总{total}张, {total_pages}页")
                return results, total_pages, total
            else:
                logger.error(f"Unsplash API错误: {response.status_code}")
                return [], 0, 0
        except Exception as e:
            logger.error(f"Unsplash搜索失败: {e}")
            return [], 0, 0
    
    def download_photo(self, photo_url, max_retries=2):
        """下载图片 - 增强版本"""
        for attempt in range(max_retries):
            try:
                response = self.session.get(
                    photo_url, 
                    timeout=(5, 15),  # 连接5秒，读取15秒
                    stream=True
                )
                if response.status_code == 200:
                    img_data = BytesIO(response.content)
                    img = Image.open(img_data)
                    return img
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    time.sleep(1)  # 重试前等待1秒
                    continue
                logger.warning("图片下载超时")
            except Exception as e:
                logger.warning(f"图片下载失败: {e}")
                break
        
        return None

# ==================== 核心函数定义 ====================
def compose_image(bg_img, product_img, logo_img, product_size, output_size, output_format, 
                  mask_enabled=False, mask_color=(255, 255, 255), mask_opacity=20):
    """合成单张图片的核心函数"""
    try:
        # 1. 处理背景：调整到输出尺寸
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
        
        # 2. 添加颜色遮罩层
        if mask_enabled and mask_opacity > 0:
            mask_opacity_int = int(mask_opacity * 255 / 100)
            r, g, b = mask_color
            color_layer = Image.new('RGBA', bg.size, (r, g, b, mask_opacity_int))
            bg = Image.alpha_composite(bg, color_layer)
        
        # 3. 处理产品图
        product = product_img.convert('RGBA')
        product.thumbnail((product_size, product_size), Image.Resampling.LANCZOS)
        
        # 将产品图居中放置
        product_x = (output_size - product.width) // 2
        product_y = (output_size - product.height) // 2
        bg.paste(product, (product_x, product_y), product)
        
        # 4. 处理Logo图
        if logo_img:
            logo = logo_img.convert('RGBA')
            if logo.size != (output_size, output_size):
                logo = logo.resize((output_size, output_size), Image.Resampling.LANCZOS)
            bg = Image.alpha_composite(bg, logo)
        
        # 5. 根据输出格式处理背景
        if output_format.upper() == 'JPG':
            bg_rgb = Image.new('RGB', bg.size, (255, 255, 255))
            bg_rgb.paste(bg, mask=bg.split()[3])
            final_image = bg_rgb
        else:
            final_image = bg
        
        return final_image
    except Exception as e:
        logger.error(f"图片合成失败: {e}")
        return None

# ==================== 侧边栏设置区域 ====================
with st.sidebar:
    st.markdown("### ⚙️ 合成设置")
    
    # Logo颜色选择
    st.markdown("🖼️ Logo颜色")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("黑色", use_container_width=True, 
                    type="primary" if st.session_state.logo_color == "黑色Logo" else "secondary",
                    key="black_logo_btn"):
            st.session_state.logo_color = "黑色Logo"
            st.rerun()
    with col2:
        if st.button("白色", use_container_width=True,
                    type="primary" if st.session_state.logo_color == "白色Logo" else "secondary",
                    key="white_logo_btn"):
            st.session_state.logo_color = "白色Logo"
            st.rerun()
    
    st.markdown("---")
    
    # 产品图大小设置
    st.markdown("📏 产品图尺寸")
    product_size = st.slider(
        "最大边长 (像素)", 
        min_value=500, 
        max_value=1000, 
        value=st.session_state.product_size, 
        step=50,
        key="product_size_slider"
    )
    st.session_state.product_size = product_size
    
    st.markdown("---")
    
    # 背景遮罩设置
    st.markdown("🎨 背景遮罩")
    dark_mask_enabled = st.checkbox(
        '启用遮罩',
        value=st.session_state.dark_mask_enabled,
        key='dark_mask_enabled_checkbox'
    )
    st.session_state.dark_mask_enabled = dark_mask_enabled
    
    if dark_mask_enabled:
        mask_opacity = st.slider(
            '不透明度 (%)',
            min_value=0,
            max_value=100,
            value=st.session_state.mask_opacity,
            step=5,
            key='mask_opacity_slider'
        )
        st.session_state.mask_opacity = mask_opacity
        
        # 颜色选择类型
        col_type1, col_type2 = st.columns(2)
        with col_type1:
            mask_color_type = st.session_state.mask_color_type
            if st.button("预设颜色", use_container_width=True,
                        type="primary" if mask_color_type == '预设颜色' else "secondary",
                        key="preset_color_btn"):
                st.session_state.mask_color_type = "预设颜色"
                st.rerun()
        
        with col_type2:
            if st.button("自定义", use_container_width=True,
                        type="primary" if mask_color_type == '自定义颜色' else "secondary",
                        key="custom_color_btn"):
                st.session_state.mask_color_type = "自定义颜色"
                st.rerun()
        
        if st.session_state.mask_color_type == "预设颜色":
            # 预设颜色选择
            selected_color = st.selectbox(
                "选择颜色",
                list(PRESET_COLORS.keys()),
                index=list(PRESET_COLORS.keys()).index(st.session_state.mask_preset_color),
                key="preset_color_select"
            )
            st.session_state.mask_preset_color = selected_color
            hex_color = PRESET_COLORS[selected_color]
            st.session_state.mask_color_rgb = hex_to_rgb(hex_color)
            
            # 显示颜色预览
            st.markdown(f"""
            <div style="display: flex; align-items: center; margin-top: 10px;">
                <div style="width: 30px; height: 30px; background-color: {hex_color}; 
                     border-radius: 4px; border: 1px solid #ddd; margin-right: 10px;"></div>
                <div>当前颜色: {st.session_state.mask_preset_color}</div>
            </div>
            """, unsafe_allow_html=True)
        
        else:  # 自定义颜色
            custom_color = st.color_picker(
                "选择颜色",
                value=st.session_state.mask_custom_color,
                key='mask_custom_color_picker'
            )
            st.session_state.mask_custom_color = custom_color
            st.session_state.mask_color_rgb = hex_to_rgb(custom_color)
    
    st.markdown("---")
    
    # 输出设置
    st.markdown("📦 输出设置")
    output_size = st.selectbox(
        "输出尺寸", 
        [400, 600, 800, 1000, 1200, 1500, 2000],
        index=2,
        key="output_size_select"
    )
    st.session_state.output_size = output_size
    
    output_format = st.radio(
        "输出格式", 
        ['JPG', 'PNG'],
        horizontal=True,
        index=0 if st.session_state.output_format == 'JPG' else 1,
        key="output_format_radio"
    )
    st.session_state.output_format = output_format
    
    st.markdown("---")
    
    # 处理按钮
    process_button = st.button(
        "🚀 开始智能批量合成", 
        type="primary", 
        use_container_width=True,
        key="process_button"
    )

# ==================== 主区域：标签页 ====================
tab1, tab2, tab3 = st.tabs(["📤 产品图合成", "🎬 视频抽帧", "🖼️ Logo水印添加"])

# ========== tab1：产品图合成 - 简化版 ==========
with tab1:
    st.header("📤 产品图合成")
    st.markdown('<div class="hint-box">上传合适的背景图或unsplash图库中搜索，再上传透明产品图，左侧合成带LOGO产品图</div>', unsafe_allow_html=True)
    
    # 显示加载状态
    if st.session_state.get('is_loading', False):
        st.markdown(show_loading(), unsafe_allow_html=True)
    
    # 使用两列布局
    col1, col2 = st.columns([1, 1], gap="large")
    
    # 背景图上传区域
    with col1:
        st.markdown("#### 背景图上传")
        
        # 背景来源选择
        bg_source = st.radio(
            "",
            ["上传图片", "Unsplash图库"],
            horizontal=True,
            index=0,
            key="bg_source_radio"
        )
        
        if bg_source == "上传图片":
            # 上传背景图
            bg_files = st.file_uploader(
                "拖拽或选择背景图片",
                type=['png', 'jpg', 'jpeg'],
                accept_multiple_files=True,
                key="bg_upload",
                help="支持JPG/PNG格式",
                label_visibility="collapsed"
            )
            
            if bg_files:
                st.success(f"已上传 {len(bg_files)} 张背景图")
                
                # 显示预览
                st.markdown("预览（最多显示12张）")
                for i in range(0, min(len(bg_files), 12), 3):
                    cols = st.columns(3)
                    for j in range(3):
                        idx = i + j
                        if idx < min(len(bg_files), 12):
                            with cols[j]:
                                file = bg_files[idx]
                                img = Image.open(file)
                                img.thumbnail((120, 120), Image.Resampling.LANCZOS)
                                st.image(img, caption=file.name[:10] + "...", use_column_width=True)
        
        else:  # Unsplash图库 - 简化版本
            unsplash_api = UnsplashAPI()
            
            # 搜索框
            search_col1, search_col2 = st.columns([3, 1])
            with search_col1:
                search_query = st.text_input(
                    "",
                    value=st.session_state.unsplash_search_query,
                    placeholder="输入关键词...",
                    key="unsplash_search_input"
                )
            
            with search_col2:
                search_btn = st.button("搜索", type="primary", use_container_width=True, key="search_unsplash")
            
            # 处理搜索
            if search_btn:
                st.session_state.unsplash_search_query = search_query
                st.session_state.unsplash_current_page = 1
                st.session_state.unsplash_search_trigger = True
            
            # 分页按钮
            if st.session_state.unsplash_photos:
                col_prev, col_page, col_next = st.columns([1, 2, 1])
                with col_prev:
                    if st.session_state.unsplash_current_page > 1:
                        if st.button("◀️ 上一页", use_container_width=True, key="prev_page"):
                            st.session_state.unsplash_current_page -= 1
                            st.session_state.unsplash_search_trigger = True
                
                with col_page:
                    total_pages = st.session_state.get('unsplash_total_pages', 0)
                    current_page = st.session_state.unsplash_current_page
                    st.markdown(f"<div style='text-align: center; padding: 8px;'>第 {current_page} / {total_pages} 页</div>", 
                              unsafe_allow_html=True)
                
                with col_next:
                    if st.session_state.unsplash_current_page < st.session_state.get('unsplash_total_pages', 1):
                        if st.button("下一页 ▶️", use_container_width=True, key="next_page"):
                            st.session_state.unsplash_current_page += 1
                            st.session_state.unsplash_search_trigger = True
            
            # 执行搜索
            if st.session_state.unsplash_search_trigger and unsplash_api.access_key:
                with st.spinner(f"搜索中: {st.session_state.unsplash_search_query}..."):
                    photos, total_pages, total_results = unsplash_api.search_photos(
                        st.session_state.unsplash_search_query, 
                        page=st.session_state.unsplash_current_page, 
                        per_page=12
                    )
                    
                    if photos:
                        st.session_state.unsplash_photos = photos
                        st.session_state.unsplash_total_pages = total_pages
                        st.session_state.unsplash_total_results = total_results
                    else:
                        if total_results == 0:
                            st.warning(f"未找到相关图片")
                    
                    st.session_state.unsplash_search_trigger = False
            
            # 显示搜索结果
            if st.session_state.unsplash_photos:
                total_results = st.session_state.get('unsplash_total_results', 0)
                if total_results > 0:
                    st.info(f"📊 找到 {total_results} 张图片")
                
                photos = st.session_state.unsplash_photos
                
                # 每行3列显示图片
                for i in range(0, len(photos), 3):
                    cols = st.columns(3)
                    for j in range(3):
                        idx = i + j
                        if idx < len(photos):
                            with cols[j]:
                                photo = photos[idx]
                                img_url = photo.get("urls", {}).get("thumb") or photo.get("urls", {}).get("small")
                                
                                if img_url:
                                    # 显示图片
                                    st.image(img_url, use_column_width=True)
                                    
                                    # 判断是否选中
                                    is_selected = False
                                    selected_bg = st.session_state.get('unsplash_selected_bg_file')
                                    if selected_bg and hasattr(selected_bg, 'idx'):
                                        is_selected = (selected_bg.idx == idx and 
                                                      getattr(selected_bg, 'page', -1) == st.session_state.unsplash_current_page)
                                    
                                    # 选择按钮
                                    if st.button(
                                        "选择背景图",
                                        key=f"select_bg_{st.session_state.unsplash_current_page}_{idx}",
                                        type="primary" if is_selected else "secondary",
                                        use_container_width=True
                                    ):
                                        # 下载图片
                                        with st.spinner("下载背景图中..."):
                                            regular_url = photo.get("urls", {}).get("regular") or img_url
                                            img = unsplash_api.download_photo(regular_url)
                                            if img:
                                                # 创建模拟文件对象
                                                class MockFile:
                                                    def __init__(self, img, page, idx):
                                                        self.name = f"unsplash_bg_{page}_{idx}.jpg"
                                                        self.type = "image/jpeg"
                                                        self.image = img
                                                        self.page = page
                                                        self.idx = idx
                                                
                                                mock_file = MockFile(img, st.session_state.unsplash_current_page, idx)
                                                st.session_state.unsplash_selected_bg_file = mock_file
                                                st.success("背景图已选择！")
                                            else:
                                                st.error("背景图下载失败")
    
    # 产品图上传区域
    with col2:
        st.markdown("#### 产品图上传")
        
        product_files = st.file_uploader(
            "拖拽或选择产品图片",
            type=['png', 'jpg', 'jpeg'],
            accept_multiple_files=True,
            key="product_upload",
            help="建议使用透明背景的PNG图片",
            label_visibility="collapsed"
        )
        
        if product_files:
            st.success(f"已上传 {len(product_files)} 张产品图")
            
            # 显示预览
            st.markdown("预览（最多显示12张）")
            for i in range(0, min(len(product_files), 12), 3):
                cols = st.columns(3)
                for j in range(3):
                    idx = i + j
                    if idx < min(len(product_files), 12):
                        with cols[j]:
                            file = product_files[idx]
                            img = Image.open(file)
                            img.thumbnail((120, 120), Image.Resampling.LANCZOS)
                            st.image(img, caption=file.name[:10] + "...", use_column_width=True)

# ==================== 执行批处理 ====================
if process_button:
    # 检查必要文件
    bg_files_combined = []
    
    # 获取上传的背景文件
    if 'bg_files' in locals() and bg_files:
        bg_files_combined.extend(bg_files)
    
    # 获取Unsplash选择的背景文件
    if 'unsplash_selected_bg_file' in st.session_state and st.session_state.unsplash_selected_bg_file:
        bg_files_combined.append(st.session_state.unsplash_selected_bg_file)
    
    if not bg_files_combined:
        st.error("❌ 请至少上传一张背景图或从Unsplash图库选择一张背景。")
        st.stop()
    
    if not product_files:
        st.error("❌ 请至少上传一张产品图。")
        st.stop()
    
    # 获取Logo图像对象
    logo_path = None
    if st.session_state.logo_color == "黑色Logo":
        logo_path = "logos/black_logo.png"
    else:
        logo_path = "logos/white_logo.png"
    
    logo_to_use = None
    if os.path.exists(logo_path):
        logo_to_use = Image.open(logo_path)
        st.info(f"🎨 使用{st.session_state.logo_color}进行合成")
    else:
        st.warning(f"⚠️ 未找到Logo文件：{logo_path}")
        st.warning("请在 logos 文件夹中提供 black_logo.png 和 white_logo.png 文件")
    
    # 显示遮罩状态
    if st.session_state.dark_mask_enabled:
        mask_hex = rgb_to_hex(st.session_state.mask_color_rgb)
        st.info(f"🖌️ 背景遮罩已启用 | 颜色: {st.session_state.mask_preset_color} ({mask_hex}) | 不透明度: {st.session_state.mask_opacity}%")
    
    # 创建临时目录存放结果
    with tempfile.TemporaryDirectory() as tmpdir:
        output_files = []
        total = len(bg_files_combined) * len(product_files)
        
        # 进度条
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        processed = 0
        for i, bg_file in enumerate(bg_files_combined):
            # 处理背景文件
            try:
                if hasattr(bg_file, 'read'):  # 上传的文件
                    bg_file.seek(0)  # 重置文件指针
                    bg_image = Image.open(bg_file)
                elif hasattr(bg_file, 'image'):  # Unsplash文件或模拟文件
                    bg_image = bg_file.image
                else:
                    continue
            except Exception as e:
                st.warning(f"背景图{i+1}加载失败: {e}")
                continue
            
            for j, product_file in enumerate(product_files):
                try:
                    product_file.seek(0)  # 重置文件指针
                    product_image = Image.open(product_file)
                except Exception as e:
                    st.warning(f"产品图{j+1}加载失败: {e}")
                    continue
                
                # 更新进度
                processed += 1
                progress = processed / total
                progress_bar.progress(progress)
                status_text.text(f"正在处理 {processed}/{total} ({progress*100:.1f}%)")
                
                # 调用合成函数
                result = compose_image(
                    bg_image, product_image, logo_to_use,
                    st.session_state.product_size, st.session_state.output_size, st.session_state.output_format,
                    mask_enabled=st.session_state.dark_mask_enabled,
                    mask_color=st.session_state.mask_color_rgb,
                    mask_opacity=st.session_state.mask_opacity
                )
                
                if result:
                    # 保存结果
                    if hasattr(bg_file, 'name'):
                        bg_name = os.path.splitext(bg_file.name)[0]
                    else:
                        bg_name = f"unsplash_bg_{i}"
                    
                    product_name = os.path.splitext(product_file.name)[0]
                    output_filename = f"{bg_name}_{product_name}.{st.session_state.output_format.lower()}"
                    output_path = os.path.join(tmpdir, output_filename)
                    
                    try:
                        if st.session_state.output_format.upper() == 'JPG':
                            result.save(output_path, format='JPEG', quality=95)
                        else:
                            result.save(output_path, format='PNG')
                        
                        output_files.append(output_path)
                    except Exception as e:
                        st.warning(f"保存图片失败 {output_filename}: {e}")
        
        progress_bar.empty()
        status_text.empty()
        
        if output_files:
            # 打包所有文件为ZIP
            zip_buffer = BytesIO()
            try:
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for file_path in output_files:
                        zip_file.write(file_path, os.path.basename(file_path))
                
                zip_buffer.seek(0)
                
                # 提供下载按钮
                st.success(f"✅ 合成完成！共生成 {len(output_files)} 张图片。")
                
                st.download_button(
                    label=f"📥 下载所有合成图片 ({st.session_state.output_format.upper()}格式ZIP包)",
                    data=zip_buffer,
                    file_name=f"产品图合成_{st.session_state.output_size}px_{st.session_state.output_format.lower()}.zip",
                    mime="application/zip",
                    use_container_width=True
                )
                
                # 显示预览
                st.subheader("合成结果预览")
                st.write(f"共 {len(output_files)} 张合成图片，显示前 12 张预览")
                
                # 显示前12张图片
                preview_files = output_files[:12]
                cols = st.columns(4)
                
                for idx, file_path in enumerate(preview_files):
                    with cols[idx % 4]:
                        try:
                            img = Image.open(file_path)
                            img.thumbnail((180, 180), Image.Resampling.LANCZOS)
                            st.image(img, use_column_width=True)
                            st.caption(os.path.basename(file_path)[:15] + "...")
                        except Exception as e:
                            st.error(f"预览失败: {e}")
            except Exception as e:
                st.error(f"打包ZIP文件失败: {e}")
        else:
            st.error("❌ 合成失败，未生成任何图片")

# ==================== tab2和tab3保持不变 ====================
# 标签页2：视频抽帧
with tab2:
    st.header("🎬 视频抽帧")
    st.markdown(
    """<div class="hint-box">
        <p>通过随机删除视频中的两帧，生成内容相似但数据不同的新视频，可用于应对平台的重复检测。</p>
    </div>""", unsafe_allow_html=True)
    
    # 这里可以添加视频抽帧的功能代码
    st.info("视频抽帧功能正在开发中...")

# 标签页3：Logo水印添加
with tab3:
    st.header("🖼️ Logo水印添加")
    st.markdown(
    """<div class="hint-box">
        <p>为单张图片添加Logo水印，支持自定义Logo位置、大小和透明度。</p>
    </div>""", unsafe_allow_html=True)
    
    # 这里可以添加Logo水印添加的功能代码
    st.info("Logo水印添加功能正在开发中...")

# ==================== 页脚信息 ====================
st.markdown("---")
st.markdown("### 💡 使用说明")

# 使用三列布局显示说明
info_col1, info_col2, info_col3 = st.columns(3)

with info_col1:
    st.markdown(
    """<div style="background-color: #f8f9fa; border-radius: 10px; padding: 1.2rem; border-left: 4px solid #2196F3;">
        <h4>📝 图片合成</h4>
        <ul>
            <li>背景图：上传或Unsplash</li>
            <li>产品图：PNG透明背景最佳</li>
            <li>Logo：系统已预置黑白Logo</li>
            <li>遮罩：可选颜色和透明度</li>
        </ul>
    </div>""", unsafe_allow_html=True)

with info_col2:
    st.markdown(
    """<div style="background-color: #f8f9fa; border-radius: 10px; padding: 1.2rem; border-left: 4px solid #2196F3;">
        <h4>🎬 视频抽帧</h4>
        <ul>
            <li>随机删除视频中的两帧</li>
            <li>保留原始音频和画质</li>
            <li>改变视频哈希值</li>
        </ul>
    </div>""", unsafe_allow_html=True)

with info_col3:
    st.markdown(
    """<div style="background-color: #f8f9fa; border-radius: 10px; padding: 1.2rem; border-left: 4px solid #2196F3;">
        <h4>🖼️ Logo水印添加</h4>
        <ul>
            <li>批量添加Logo水印</li>
            <li>自定义位置大小</li>
            <li>实时预览效果</li>
        </ul>
    </div>""", unsafe_allow_html=True)

st.markdown("---")
st.caption("© 2025 骏泰素材工作台")
