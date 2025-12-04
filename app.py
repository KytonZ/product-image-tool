# app.py - 优化版 (预设Logo选择、紧凑预览)
import streamlit as st
import os
import math
from PIL import Image
import tempfile
import zipfile
from io import BytesIO

# 设置页面
st.set_page_config(page_title="骏泰产品图智能合成工坊", page_icon="🎨", layout="wide")
st.title("🎨 骏泰产品图智能合成工坊")
st.markdown("---")

# 初始化会话状态
if 'current_page' not in st.session_state:
    st.session_state.current_page = 0

# ==================== 侧边栏设置区域 ====================
with st.sidebar:
    st.header("⚙️ 合成设置")
    
    # 1. 模板选择
    template = st.selectbox(
        "选择合成模板",
        ["标准模板", "更多功能", "更多功能", "更多功能"]
    )
    
    # 2. Logo管理 - 【修改为预设Logo选择，移除上传】
    st.subheader("🖼️ Logo设置")
    
    # Logo颜色选择
    logo_color = st.radio(
        "选择Logo颜色",
        ["黑色Logo", "白色Logo"],
        help="根据背景颜色选择合适的Logo颜色以确保清晰可见"
    )
    
    # Logo预览小图
    st.markdown("**Logo预览**")
    col1, col2 = st.columns(2)
    with col1:
        if os.path.exists("logos/black_logo.png"):
            st.image("logos/black_logo.png", caption="黑色Logo", width=60)
        else:
            st.warning("黑标未找到")
    with col2:
        if os.path.exists("logos/white_logo.png"):
            st.image("logos/white_logo.png", caption="白色Logo", width=60)
        else:
            st.warning("白标未找到")
    
    # 3. 产品图尺寸与位置
    st.subheader("📐 产品图设置")
    product_size = st.slider("产品图最大边长", 500, 900, 800)
    product_position = st.select_slider(
        "产品图位置", 
        options=['左上', '中上', '右上', '左中', '居中', '右中', '左下', '中下', '右下'],
        value='居中'
    )
    
    # 4. 输出设置
    st.subheader("📦 输出设置")
    output_size = st.number_input("输出图片尺寸 (像素)", min_value=400, max_value=2000, value=800, step=50)
    output_format = st.radio("输出格式", ['JPG', 'PNG'])
    
    # 5. 预览设置
    st.subheader("👀 预览设置")
    preview_page_size = st.slider("每页预览数量", 8, 20, 12, help="每页显示的图片数量")
    
    # 6. 处理按钮
    st.markdown("---")
    process_button = st.button("🚀 开始智能批量合成", type="primary", use_container_width=True)

# ==================== 主区域：文件上传 ====================
tab1, tab2 = st.tabs(["📤 上传图片", "🖼️ 预置背景库"])

with tab1:
    st.subheader("上传你的素材")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**背景图**")
        bg_files = st.file_uploader(
            "拖拽或选择背景图片 (支持JPG/PNG格式)",
            type=['png', 'jpg', 'jpeg'],
            accept_multiple_files=True,
            key="bg_upload",
            help="可以一次选择多张背景图片"
        )
        if bg_files:
            st.success(f"✅ 已上传 {len(bg_files)} 张背景图")
            # 【缩小预览】上传图片预览
            cols = st.columns(6)
            for i, file in enumerate(bg_files[:6]):
                with cols[i]:
                    # 缩小预览尺寸：从 use_column_width 改为固定80px
                    st.image(Image.open(file), caption=file.name, width=80)
    
    with col2:
        st.markdown("**产品图**")
        product_files = st.file_uploader(
            "拖拽或选择产品图片 (PNG透明背景效果最佳)",
            type=['png', 'jpg', 'jpeg'],
            accept_multiple_files=True,
            key="product_upload",
            help="建议使用透明背景的PNG图片"
        )
        if product_files:
            st.success(f"✅ 已上传 {len(product_files)} 张产品图")
            # 【缩小预览】上传图片预览
            cols = st.columns(6)
            for i, file in enumerate(product_files[:6]):
                with cols[i]:
                    st.image(Image.open(file), caption=file.name, width=80)

with tab2:
    st.subheader("使用预置背景库")
    st.info("📚 此功能正在开发中，敬请期待！")

# ==================== 图像合成核心函数 ====================
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

# ==================== 执行批处理 ====================
if process_button:
    # 检查必要文件
    if not bg_files:
        st.error("❌ 请至少上传一张背景图。")
        st.stop()
    if not product_files:
        st.error("❌ 请至少上传一张产品图。")
        st.stop()
    
    # 获取Logo图像对象 - 【修改为读取预设Logo文件】
    logo_to_use = None
    logo_path = None
    
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
        st.subheader("👁️ 预览合成结果")
        
        if output_files:
            # 计算总页数
            total_previews = len(output_files)
            page_size = preview_page_size
            total_pages = math.ceil(total_previews / page_size)
            
            # 确保当前页码有效
            if st.session_state.current_page >= total_pages:
                st.session_state.current_page = total_pages - 1 if total_pages > 0 else 0
            
            # 分页控件
            col1, col2, col3, col4 = st.columns([1, 2, 2, 1])
            with col1:
                if st.button("◀️ 上一页", disabled=st.session_state.current_page == 0):
                    st.session_state.current_page -= 1
                    st.rerun()
            with col2:
                st.write(f"第 {st.session_state.current_page + 1} / {total_pages} 页")
            with col3:
                st.write(f"共 {total_previews} 张图片，每页 {page_size} 张")
            with col4:
                if st.button("下一页 ▶️", disabled=st.session_state.current_page >= total_pages - 1):
                    st.session_state.current_page += 1
                    st.rerun()
            
            # 显示当前页的图片
            start_idx = st.session_state.current_page * page_size
            end_idx = min(start_idx + page_size, total_previews)
            
            st.markdown(f"**显示 {start_idx + 1} - {end_idx} 张图片**")
            
            # 【关键修改】增加每行显示列数，缩小预览图
            # 根据页面大小动态调整列数
            if page_size >= 16:
                cols_per_row = 6  # 每行6张，图片最小
            elif page_size >= 12:
                cols_per_row = 5  # 每行5张
            else:
                cols_per_row = 4  # 每行4张
            
            current_row = 0
            
            for i in range(start_idx, end_idx):
                file_path = output_files[i]
                img = Image.open(file_path)
                
                # 每cols_per_row张图片换一行
                if (i - start_idx) % cols_per_row == 0:
                    current_row += 1
                    cols = st.columns(cols_per_row)
                
                with cols[(i - start_idx) % cols_per_row]:
                    # 【关键修改】缩小预览图尺寸：使用固定宽度150px
                    st.image(img, caption=os.path.basename(file_path), width=150)
            
            # 重置页码的按钮
            if st.button("重置页码到第一页"):
                st.session_state.current_page = 0
                st.rerun()
        else:
            st.warning("⚠️ 没有生成任何图片")

# ==================== 页脚信息 ====================
st.markdown("---")
st.markdown("### 💡 使用说明")
col_info1, col_info2 = st.columns(2)

with col_info1:
    st.markdown("""
    **📝 准备图片**
    1. 背景图：JPG/PNG格式
    2. 产品图：PNG透明背景最佳
    3. 系统已预置黑/白Logo
    """)

with col_info2:
    st.markdown("""
    **⚡ 快速开始**
    1. 上传背景图和产品图
    2. 选择Logo颜色和输出设置
    3. 点击"开始智能批量合成"
    4. 下载ZIP包获取所有图片
    """)

st.markdown("---")
st.caption("💡 提示：如需调整Logo文件，请替换 logos/ 文件夹中的 black_logo.png 或 white_logo.png")