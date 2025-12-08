# app.py - 修复和优化版（添加视频抽帧工具）
import zipfile
from io import BytesIO
import streamlit as st
import os
import math
from PIL import Image
import tempfile
import random
import base64
import cv2
import numpy as np
from moviepy.editor import VideoFileClip, AudioFileClip
import glob

# 设置页面配置
st.set_page_config(
    page_title="骏泰产品图智能合成工坊", 
    page_icon="🎨", 
    layout="wide",
    initial_sidebar_state="expanded"
)

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
            padding: 0.5rem 0;
            margin-bottom: 0.5rem !important;
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
        
        .stTabs [data-baseweb="tab"] {
            padding: 10px 20px;
            border-radius: 5px 5px 0 0;
            font-weight: 500;
        }
        
        /* 按钮样式 */
        .stButton > button {
            border-radius: 8px;
            padding: 0.6rem 1.2rem;
            font-weight: 600;
            transition: all 0.3s ease;
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
        
        /* 视频信息卡片 */
        .video-info-card {
            background-color: #e8f4fd;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #2196F3;
        }
        
        .video-info-title {
            font-weight: 600;
            color: #2196F3;
            margin-bottom: 5px;
        }
        
        .video-info-text {
            color: #555;
            font-size: 14px;
        }
    </style>
    """

# 应用CSS样式
st.markdown(get_custom_css(), unsafe_allow_html=True)

# 页面标题
st.markdown('<h1 class="main-header">🎨 骏泰产品图智能合成工坊</h1>', unsafe_allow_html=True)
st.markdown("---")

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

# ==================== 核心函数定义 ====================
def compose_image(bg_img, product_img, logo_img, template, product_size, product_position, output_size, output_format):
    """合成单张图片的核心函数"""
    # 1. 处理背景：调整到输出尺寸（智能裁剪铺满）
    bg = bg_img.convert("RGBA")
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
    
    # 2. 处理产品图：调整大小并放置
    product = product_img.convert("RGBA")
    product.thumbnail((product_size, product_size), Image.Resampling.LANCZOS)
    
    # 根据选择的位置计算坐标
    position_map = {
        '左上': (20, 20), '中上': ((output_size - product.width)//2, 20), '右上': (output_size - product.width - 20, 20),
        '左中': (20, (output_size - product.height)//2), '居中': ((output_size - product.width)//2, (output_size - product.height)//2),
        '右中': (output_size - product.width - 20, (output_size - product.height)//2),
        '左下': (20, output_size - product.height - 20), '中下': ((output_size - product.width)//2, output_size - product.height - 20),
        '右下': (output_size - product.width - 20, output_size - product.height - 20)
    }
    product_x, product_y = position_map.get(product_position, (0, 0))
    
    # 将产品图粘贴到背景上
    bg.paste(product, (product_x, product_y), product)
    
    # 3. 处理Logo图 - 直接全画布叠加
    if logo_img:
        logo = logo_img.convert("RGBA")
        # 确保Logo图尺寸与输出尺寸一致
        if logo.size != (output_size, output_size):
            logo = logo.resize((output_size, output_size), Image.Resampling.LANCZOS)
        # 直接以"遮罩"方式叠加整个Logo图层
        bg = Image.alpha_composite(bg, logo)
    
    # 4. 根据输出格式处理背景
    if output_format.upper() == 'JPG':
        bg_rgb = Image.new('RGB', bg.size, (255, 255, 255))
        bg_rgb.paste(bg, mask=bg.split()[3])
        final_image = bg_rgb
    else:
        final_image = bg
    
    return final_image

def generate_modified_images(uploaded_file, num_copies, num_pixels_to_change=1):
    """生成多张经过像素微调的图片"""
    try:
        # 1. 读取原始图片
        original_img = Image.open(uploaded_file).convert('RGB')
        width, height = original_img.size
        
        # 存储生成的图片用于预览
        preview_images = []
        
        # 2. 准备一个内存中的Zip文件
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # 3. 循环生成指定数量的图片
            for i in range(num_copies):
                # 复制原始图片，避免在原图上修改
                modified_img = original_img.copy()
                pixels = modified_img.load()  # 获取像素访问对象
                
                # 4. 随机修改指定数量的像素点
                for _ in range(num_pixels_to_change):
                    # 随机选择一个像素位置
                    x = random.randint(0, width - 1)
                    y = random.randint(0, height - 1)
                    
                    # 获取原像素颜色
                    original_r, original_g, original_b = pixels[x, y]
                    
                    # 在每个颜色通道上进行微小随机调整（±2范围内）
                    new_r = max(0, min(255, original_r + random.randint(-2, 2)))
                    new_g = max(0, min(255, original_g + random.randint(-2, 2)))
                    new_b = max(0, min(255, original_b + random.randint(-2, 2)))
                    
                    # 应用新颜色
                    pixels[x, y] = (new_r, new_g, new_b)
                
                # 5. 将修改后的图片保存到内存，并加入Zip
                img_buffer = BytesIO()
                # 根据原格式保存，保持质量
                if uploaded_file.type in ['image/jpeg', 'image/jpg']:
                    modified_img.save(img_buffer, format='JPEG', quality=95)
                    ext = '.jpg'
                else:
                    modified_img.save(img_buffer, format='PNG')
                    ext = '.png'
                
                img_buffer.seek(0)
                # 生成文件名：原名称_序号
                file_name = f"{os.path.splitext(uploaded_file.name)[0]}_modified_{i+1:03d}{ext}"
                zip_file.writestr(file_name, img_buffer.getvalue())
                
                # 存储前3张用于预览
                if i < 3:
                    preview_images.append(modified_img.copy())
        
        zip_buffer.seek(0)
        return zip_buffer, preview_images
        
    except Exception as e:
        st.error(f"处理图片时发生错误: {e}")
        return None, []

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
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # MP4编码
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

# ==================== 侧边栏设置区域 ====================
with st.sidebar:
    st.markdown("### ⚙️ 合成设置")
    
    # 将所有设置存储到session_state中
    # 1. 模板选择
    st.markdown('<div class="settings-title">选择合成模板</div>', unsafe_allow_html=True)
    st.session_state.template = st.selectbox(
        "选择合成模板",
        ["标准模板", "电商海报", "社交媒体", "产品展示"],
        help="选择适合您需求的合成模板",
        label_visibility="collapsed",
        key="template_select"
    )
    
    st.markdown("---")
    
    # 2. Logo设置
    st.markdown('<div class="settings-title">🖼️ Logo设置</div>', unsafe_allow_html=True)
    st.session_state.logo_color = st.radio(
        "选择Logo颜色",
        ["黑色Logo", "白色Logo"],
        horizontal=True,
        help="根据背景颜色选择合适的Logo颜色以确保清晰可见",
        key="logo_color_select"
    )
    
    
    st.markdown("---")
    
    # 3. 产品图设置
    st.markdown('<div class="settings-title">📐 产品图设置</div>', unsafe_allow_html=True)
    st.session_state.product_size = st.slider(
        "产品图最大边长", 
        min_value=500, 
        max_value=1000, 
        value=800, 
        step=50,
        help="控制产品图在合成图中的大小",
        key="product_size_slider"
    )
    
    st.session_state.product_position = st.select_slider(
        "产品图位置", 
        options=['左上', '中上', '右上', '左中', '居中', '右中', '左下', '中下', '右下'],
        value='居中',
        help="选择产品图在合成图中的位置",
        key="product_position_slider"
    )
    
    st.markdown("---")
    
    # 4. 输出设置
    st.markdown('<div class="settings-title">📦 输出设置</div>', unsafe_allow_html=True)
    
    col_size1, col_size2 = st.columns(2)
    with col_size1:
        st.session_state.output_size = st.selectbox(
            "输出尺寸", 
            [400, 600, 800, 1000, 1200, 1500, 2000],
            index=2,
            help="选择输出图片的尺寸",
            key="output_size_select"
        )
    with col_size2:
        st.session_state.output_format = st.radio(
            "输出格式", 
            ['JPG', 'PNG'],
            horizontal=True,
            help="JPG适用于照片，PNG适用于需要透明背景的图片",
            key="output_format_radio"
        )
    
    st.markdown("---")
    
    # 5. 预览设置
    st.markdown('<div class="settings-title">👀 预览设置</div>', unsafe_allow_html=True)
    st.session_state.preview_page_size = st.select_slider(
        "每页预览数量", 
        options=[6, 9, 12, 16, 20, 25, 30],
        value=12,
        help="控制每页显示的图片数量",
        key="preview_page_size_slider"
    )
    
    st.markdown("---")
    
    # 6. 处理按钮
    process_button = st.button(
        "🚀 开始智能批量合成", 
        type="primary", 
        use_container_width=True,
        help="点击开始处理所有图片",
        key="process_button"
    )

# ==================== 主区域：标签页 ====================
tab1, tab2, tab3, tab4 = st.tabs(["📤 上传图片", "🖼️ 预置背景库", "🔄 图片去重生成器", "🎬 视频抽帧工具"])

# 标签页1：上传图片
with tab1:
    st.subheader("上传你的素材")
    
    # 使用两列布局
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        # 背景图上传
        st.markdown("#### 背景图上传")
        bg_files = st.file_uploader(
            "拖拽或选择背景图片",
            type=['png', 'jpg', 'jpeg'],
            accept_multiple_files=True,
            key="bg_upload",
            help="支持JPG/PNG格式，可以一次选择多张图片",
            label_visibility="collapsed"
        )
        
        if bg_files:
            bg_count = len(bg_files)
            st.markdown(f'<div class="status-success">✅ 已上传 <span class="file-count">{bg_count}</span> 张背景图</div>', unsafe_allow_html=True)
            
            # 显示前几张预览
            st.markdown("**预览（最多显示12张）**")
            
            # 计算每行列数
            cols_per_row = min(4, bg_count) if bg_count > 0 else 4
            preview_count = min(12, bg_count)
            
            # 创建网格布局
            for i in range(0, preview_count, cols_per_row):
                cols = st.columns(cols_per_row)
                for j in range(cols_per_row):
                    idx = i + j
                    if idx < preview_count:
                        with cols[j]:
                            file = bg_files[idx]
                            img = Image.open(file)
                            # 保持原始比例，设置合适宽度
                            display_width = 180
                            ratio = display_width / img.width
                            display_height = int(img.height * ratio)
                            
                            # 使用高质量的调整大小
                            display_img = img.copy()
                            display_img.thumbnail((display_width, display_height * 2), Image.Resampling.LANCZOS)
                            
                            st.image(
                                display_img, 
                                caption=file.name[:18] + "..." if len(file.name) > 18 else file.name,
                                width=display_width
                            )
    
    with col2:
        # 产品图上传
        st.markdown("#### 产品图上传")
        product_files = st.file_uploader(
            "拖拽或选择产品图片",
            type=['png', 'jpg', 'jpeg'],
            accept_multiple_files=True,
            key="product_upload",
            help="建议使用透明背景的PNG图片以获得最佳效果",
            label_visibility="collapsed"
        )
        
        if product_files:
            product_count = len(product_files)
            st.markdown(f'<div class="status-success">✅ 已上传 <span class="file-count">{product_count}</span> 张产品图</div>', unsafe_allow_html=True)
            
            # 显示前几张预览
            st.markdown("**预览（最多显示12张）**")
            
            # 计算每行列数
            cols_per_row = min(4, product_count) if product_count > 0 else 4
            preview_count = min(12, product_count)
            
            # 创建网格布局
            for i in range(0, preview_count, cols_per_row):
                cols = st.columns(cols_per_row)
                for j in range(cols_per_row):
                    idx = i + j
                    if idx < preview_count:
                        with cols[j]:
                            file = product_files[idx]
                            img = Image.open(file)
                            # 保持原始比例，设置合适宽度
                            display_width = 180
                            ratio = display_width / img.width
                            display_height = int(img.height * ratio)
                            
                            # 使用高质量的调整大小
                            display_img = img.copy()
                            display_img.thumbnail((display_width, display_height * 2), Image.Resampling.LANCZOS)
                            
                            st.image(
                                display_img, 
                                caption=file.name[:18] + "..." if len(file.name) > 18 else file.name,
                                width=display_width
                            )
    
    # 上传状态汇总
    if bg_files and product_files:
        total_combinations = len(bg_files) * len(product_files)
        st.info(f"📊 **准备合成:** {len(bg_files)} 张背景图 × {len(product_files)} 张产品图 = **{total_combinations} 张合成图**")

# 标签页2：预置背景库
with tab2:
    st.header("🖼️ 预置背景库")
    st.markdown("选择或管理预置的背景图片")
    
    # 这里可以添加背景库的显示和管理功能
    st.markdown("""
    <div style="text-align: center; padding: 3rem; color: #666;">
        <h3>🎨 背景库功能开发中</h3>
        <p>即将推出：纯色背景、渐变背景、纹理背景库</p>
    </div>
    """, unsafe_allow_html=True)

# 标签页3：图片去重生成器
with tab3:
    st.header("🔄 图片去重生成器")
    st.markdown("""
    <div style="background-color: #f8f9fa; border-radius: 10px; padding: 1.5rem; margin-bottom: 1.5rem; border-left: 4px solid #2196F3;">
        <p>通过微调图片像素，生成大量数据层不同的相似图片，可用于应对平台的重复检测。</p>
        <p><b>原理</b>：随机修改图片中单个像素的颜色，变化微小到人眼无法察觉。</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 使用两列布局
    col_left, col_right = st.columns([1, 1], gap="large")
    
    with col_left:
        st.markdown("#### 1. 上传图片")
        uploaded_file = st.file_uploader(
            "选择需要处理的图片", 
            type=['png', 'jpg', 'jpeg'], 
            key="unique_uploader",
            help="支持JPG和PNG格式",
            label_visibility="collapsed"
        )
        
        if uploaded_file:
            # 显示原图，但控制大小
            st.markdown("**原始图片预览**")
            
            # 读取图片
            img = Image.open(uploaded_file)
            
            # 根据图片大小自适应显示
            max_display_size = 400  # 最大显示尺寸
            
            # 计算显示尺寸，保持宽高比
            display_width = min(max_display_size, img.width)
            display_height = int(img.height * (display_width / img.width))
            
            # 高质量调整大小
            display_img = img.copy()
            display_img.thumbnail((display_width, display_height), Image.Resampling.LANCZOS)
            
            # 显示调整后的图片
            st.image(display_img, caption=f"原图: {uploaded_file.name}", width=display_width)
            
            # 显示图片信息
            st.caption(f"尺寸: {img.width} × {img.height} 像素 | 格式: {uploaded_file.type}")
    
    with col_right:
        if uploaded_file:
            st.markdown("#### 2. 生成设置")
            
            # 参数设置
            num_copies = st.slider(
                "生成图片数量", 
                min_value=1, 
                max_value=100, 
                value=10, 
                step=1,
                help="生成多少张经过微调的图片"
            )
            
            num_pixels_to_change = st.slider(
                "修改的像素点数量", 
                min_value=1, 
                max_value=10, 
                value=2, 
                step=1,
                help="每张图片随机修改多少个像素点的颜色。数量越多，数据差异越大。"
            )
            
            # 生成按钮
            if st.button("🚀 开始批量生成", type="primary", use_container_width=True, key="generate_unique"):
                with st.spinner(f'正在批量生成 {num_copies} 张图片...'):
                    # 调用核心处理函数
                    zip_buffer, preview_images = generate_modified_images(
                        uploaded_file, num_copies, num_pixels_to_change
                    )
                    
                    if zip_buffer:
                        st.session_state.processed_images = preview_images
                        st.session_state.last_zip_buffer = zip_buffer
                        
                        st.success(f"✅ 成功生成 {num_copies} 张图片！")
                        
                        # 显示生成预览
                        if preview_images:
                            st.markdown("#### 生成预览（前3张）")
                            
                            # 使用网格布局显示预览
                            preview_cols = st.columns(3)
                            for idx, preview_img in enumerate(preview_images):
                                with preview_cols[idx]:
                                    # 高质量调整大小
                                    display_img = preview_img.copy()
                                    display_width = 180
                                    ratio = display_width / display_img.width
                                    display_height = int(display_img.height * ratio)
                                    display_img.thumbnail((display_width, display_height), Image.Resampling.LANCZOS)
                                    
                                    st.image(
                                        display_img, 
                                        caption=f"微调图 {idx+1}",
                                        width=display_width
                                    )
                                    st.caption(f"尺寸: {preview_img.width} × {preview_img.height}")
            
            # 如果之前已经生成了图片，显示下载按钮
            if st.session_state.last_zip_buffer and uploaded_file:
                st.markdown("#### 3. 下载结果")
                st.download_button(
                    label=f"📥 下载生成的图片 (ZIP压缩包)",
                    data=st.session_state.last_zip_buffer,
                    file_name=f"{os.path.splitext(uploaded_file.name)[0]}_modified_{num_copies}copies.zip",
                    mime="application/zip",
                    use_container_width=True,
                    key="download_unique"
                )

# 标签页4：视频抽帧工具
with tab4:
    st.header("🎬 视频抽帧工具")
    st.markdown("""
    <div style="background-color: #f8f9fa; border-radius: 10px; padding: 1.5rem; margin-bottom: 1.5rem; border-left: 4px solid #FF6B6B;">
        <p>通过随机删除视频中的两帧，生成内容相似但数据不同的新视频，可用于应对平台的重复检测。</p>
        <p><b>原理</b>：随机删除视频中的两帧，变化微小到人眼无法察觉，但能改变视频的哈希值。</p>
        <p><b>特点</b>：保留原始视频的音频、画质和时长基本不变。</p>
    </div>
    """, unsafe_allow_html=True)
    
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
                    
                    st.markdown("**视频信息**")
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
                    st.markdown("**视频预览**")
                    st.video(video_file)
                else:
                    st.warning("无法读取视频信息，请检查视频格式是否支持。")
            except Exception as e:
                st.error(f"读取视频信息时出错: {e}")
    
    with col_right_video:
        if video_file:
            st.markdown("#### 2. 处理设置")
            
            # 显示处理说明
            st.info("""
            **处理说明：**
            - 工具将随机删除视频中的两帧
            - 保留原始音频和画质
            - 输出视频时长几乎不变
            - 适合用于应对平台重复检测
            """)
            
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
                        st.markdown("**处理后的视频预览**")
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

# ==================== 执行批处理 ====================
if process_button:
    # 检查必要文件
    if not bg_files:
        st.error("❌ 请至少上传一张背景图。")
        st.stop()
    if not product_files:
        st.error("❌ 请至少上传一张产品图。")
        st.stop()
    
    # 获取Logo图像对象
    logo_to_use = None
    logo_path = None
    
    # 从session_state获取设置值
    logo_color = st.session_state.get('logo_color', '黑色Logo')
    template = st.session_state.get('template', '标准模板')
    product_size = st.session_state.get('product_size', 600)
    product_position = st.session_state.get('product_position', '居中')
    output_size = st.session_state.get('output_size', 800)
    output_format = st.session_state.get('output_format', 'JPG')
    preview_page_size = st.session_state.get('preview_page_size', 12)
    
    if logo_color == "黑色Logo":
        logo_path = "logos/black_logo.png"
    else:
        logo_path = "logos/white_logo.png"
    
    if os.path.exists(logo_path):
        logo_to_use = Image.open(logo_path)
        st.info(f"🎨 使用{logo_color}进行合成")
    else:
        st.warning(f"⚠️ 未找到{logo_color}文件：{logo_path}")
        st.warning("请在 logos/ 文件夹中提供 black_logo.png 和 white_logo.png 文件")
        logo_to_use = None
    
    # 创建临时目录存放结果
    with tempfile.TemporaryDirectory() as tmpdir:
        output_files = []
        total = len(bg_files) * len(product_files)
        
        # 进度条
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        processed = 0
        for i, bg_file in enumerate(bg_files):
            bg_image = Image.open(bg_file)
            for j, product_file in enumerate(product_files):
                product_image = Image.open(product_file)
                
                # 更新进度
                processed += 1
                progress = processed / total
                progress_bar.progress(progress)
                status_text.text(f"正在处理: {processed}/{total} ({progress*100:.1f}%)")
                
                # 调用合成函数
                result = compose_image(
                    bg_image, product_image, logo_to_use,
                    template, product_size, product_position, output_size, output_format
                )
                
                # 保存结果
                output_filename = f"{os.path.splitext(bg_file.name)[0]}_{os.path.splitext(product_file.name)[0]}.{output_format.lower()}"
                output_path = os.path.join(tmpdir, output_filename)
                
                if output_format.upper() == 'JPG':
                    result.save(output_path, format='JPEG', quality=95)
                else:
                    result.save(output_path, format='PNG')
                
                output_files.append(output_path)
        
        progress_bar.empty()
        status_text.empty()
        
        # 打包所有文件为ZIP
        st.success(f"✅ 合成完成！共生成 {len(output_files)} 张图片。")
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file_path in output_files:
                zip_file.write(file_path, os.path.basename(file_path))
        
        zip_buffer.seek(0)
        
        # 提供下载按钮
        st.download_button(
            label=f"📥 下载所有合成图片 ({output_format.upper()}格式ZIP包)",
            data=zip_buffer,
            file_name=f"产品图合成_{output_size}px_{output_format.lower()}.zip",
            mime="application/zip",
            use_container_width=True
        )
        
        # ==================== 分页预览区域 ====================
        st.subheader("👁️ 合成结果预览")
        
        if output_files:
            # 计算总页数
            total_previews = len(output_files)
            page_size = preview_page_size
            total_pages = math.ceil(total_previews / page_size)
            
            # 确保当前页码有效
            if st.session_state.current_page >= total_pages:
                st.session_state.current_page = total_pages - 1 if total_pages > 0 else 0
            
            # 分页控件 - 优化布局
            pagination_cols = st.columns([1, 2, 2, 1])
            with pagination_cols[0]:
                if st.button("◀️ 上一页", disabled=st.session_state.current_page == 0, key="prev_page"):
                    st.session_state.current_page -= 1
                    st.rerun()
            with pagination_cols[1]:
                st.write(f"第 {st.session_state.current_page + 1} / {total_pages} 页")
            with pagination_cols[2]:
                st.write(f"共 {total_previews} 张图片")
            with pagination_cols[3]:
                if st.button("下一页 ▶️", disabled=st.session_state.current_page >= total_pages - 1, key="next_page"):
                    st.session_state.current_page += 1
                    st.rerun()
            
            # 显示当前页的图片
            start_idx = st.session_state.current_page * page_size
            end_idx = min(start_idx + page_size, total_previews)
            
            st.markdown(f"**显示 {start_idx + 1} - {end_idx} 张图片**")
            
            # 根据每页数量动态调整列数
            if page_size >= 20:
                cols_per_row = 6
                preview_width = 140
            elif page_size >= 12:
                cols_per_row = 5
                preview_width = 160
            else:
                cols_per_row = 4
                preview_width = 180
            
            # 使用紧凑网格显示图片
            for i in range(start_idx, end_idx, cols_per_row):
                row_cols = st.columns(cols_per_row)
                for j in range(cols_per_row):
                    idx = i + j
                    if idx < end_idx:
                        with row_cols[j]:
                            file_path = output_files[idx]
                            img = Image.open(file_path)
                            
                            # 高质量调整大小，保持清晰度
                            display_img = img.copy()
                            
                            # 计算显示尺寸，保持宽高比
                            display_height = int(preview_width * img.height / img.width)
                            display_img.thumbnail((preview_width * 2, display_height * 2), Image.Resampling.LANCZOS)
                            
                            # 显示图片和文件名
                            st.image(
                                display_img, 
                                width=preview_width
                            )
                            st.caption(
                                os.path.basename(file_path)[:20] + "..." 
                                if len(os.path.basename(file_path)) > 20 
                                else os.path.basename(file_path)
                            )
            
            # 重置页码的按钮
            if st.button("🔄 重置页码到第一页", key="reset_page"):
                st.session_state.current_page = 0
                st.rerun()
        else:
            st.warning("⚠️ 没有生成任何图片")

# ==================== 页脚信息 ====================
st.markdown("---")
st.markdown("### 💡 使用说明")

# 使用四列布局显示说明（因为现在有四个主要功能）
info_col1, info_col2, info_col3, info_col4 = st.columns(4)

with info_col1:
    st.markdown("""
    <div style="background-color: #f8f9fa; border-radius: 10px; padding: 1.2rem; border-left: 4px solid #2196F3;">
        <h4>📝 图片合成</h4>
        <ul>
            <li>背景图：JPG/PNG格式</li>
            <li>产品图：PNG透明背景最佳</li>
            <li>Logo：系统已预置黑/白Logo</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with info_col2:
    st.markdown("""
    <div style="background-color: #f8f9fa; border-radius: 10px; padding: 1.2rem; border-left: 4px solid #2196F3;">
        <h4>🔄 图片去重</h4>
        <ul>
            <li>微调像素生成相似图片</li>
            <li>应对平台重复检测</li>
            <li>批量生成多张图片</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with info_col3:
    st.markdown("""
    <div style="background-color: #f8f9fa; border-radius: 10px; padding: 1.2rem; border-left: 4px solid #2196F3;">
        <h4>🎬 视频抽帧</h4>
        <ul>
            <li>随机删除视频中的两帧</li>
            <li>保留原始音频和画质</li>
            <li>改变视频哈希值</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with info_col4:
    st.markdown("""
    <div style="background-color: #f8f9fa; border-radius: 10px; padding: 1.2rem; border-left: 4px solid #2196F3;">
        <h4>⚡ 快速开始</h4>
        <ol>
            <li>选择对应标签页</li>
            <li>上传素材文件</li>
            <li>调整设置参数</li>
            <li>开始处理并下载</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.caption("💡 提示：如需调整Logo文件，请替换 logos/ 文件夹中的 black_logo.png 或 white_logo.png")
