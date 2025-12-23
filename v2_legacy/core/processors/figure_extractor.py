#!/usr/bin/env python3
"""
从本地PDF文件中提取图片
使用AI模型识别图片区域并自动裁剪
"""

import os
import sys
import argparse
import layoutparser as lp
import cv2
import numpy as np
from pdf2image import convert_from_path

def extract_images_from_pdf(pdf_path: str, output_dir: str = "extracted_images"):
    """
    从PDF文件中提取图片
    
    Args:
        pdf_path: PDF文件路径
        output_dir: 输出目录
    """
    if not os.path.exists(pdf_path):
        print(f"❌ 文件不存在: {pdf_path}")
        return
    
    # 创建输出目录
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    target_dir = os.path.join(output_dir, pdf_name)
    os.makedirs(target_dir, exist_ok=True)
    
    print(f"📄 处理PDF: {pdf_path}")
    print(f"📂 输出目录: {target_dir}")
    
    try:
        print("\n[*] 初始化AI布局模型 (Mask R-CNN)...")
        home_dir = os.path.expanduser("~")
        local_weights = os.path.join(home_dir, ".layoutparser", "model_final.pth")
        
        if os.path.exists(local_weights):
            print(f"[*] 从本地缓存加载模型: {local_weights}")
            model = lp.Detectron2LayoutModel(
                config_path='lp://PubLayNet/mask_rcnn_X_101_32x8d_FPN_3x/config',
                model_path=local_weights,
                extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.5],
                label_map={0: "Text", 1: "Title", 2: "List", 3: "Table", 4: "Figure"}
            )
        else:
            print("[*] 本地模型未找到,使用自动下载...")
            model = lp.Detectron2LayoutModel(
                config_path='lp://PubLayNet/mask_rcnn_X_101_32x8d_FPN_3x/config',
                extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.5],
                label_map={0: "Text", 1: "Title", 2: "List", 3: "Table", 4: "Figure"}
            )
        
        print("\n[*] 将PDF页面转换为图片...")
        images = convert_from_path(pdf_path, dpi=200)
        print(f"✅ 共 {len(images)} 页")
        
        total_figures = 0
        
        for i, image in enumerate(images):
            print(f"\n📖 分析第 {i+1}/{len(images)} 页...")
            
            # 转换为numpy数组
            image_np = np.array(image)
            
            # 检测布局
            layout = model.detect(image_np)
            
            # 筛选图片区域
            figure_blocks = lp.Layout([b for b in layout if b.type == 'Figure'])
            
            if not figure_blocks:
                print(f"   [ ] 未检测到图片")
                continue
            
            print(f"   [+] 发现 {len(figure_blocks)} 张图片")
            
            for j, block in enumerate(figure_blocks):
                # 裁剪图片
                segment_image = block.crop_image(image_np)
                
                # 过滤太小的图片
                if segment_image.size == 0 or segment_image.shape[0] < 50 or segment_image.shape[1] < 50:
                    print(f"       [跳过] 图片 {j+1} 太小")
                    continue
                
                # 保存
                filename = f"page{i+1}_figure{j+1}.png"
                filepath = os.path.join(target_dir, filename)
                
                # RGB转BGR (OpenCV格式)
                segment_image_bgr = cv2.cvtColor(segment_image, cv2.COLOR_RGB2BGR)
                cv2.imwrite(filepath, segment_image_bgr)
                
                print(f"       ✅ {filename} (置信度: {block.score:.2f})")
                total_figures += 1
        
        print(f"\n🎉 完成! 共提取 {total_figures} 张图片")
        print(f"📁 保存位置: {target_dir}")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="从本地PDF提取图片")
    parser.add_argument("pdf_file", help="PDF文件路径")
    parser.add_argument("--output", "-o", default="extracted_images", help="输出目录 (默认: extracted_images)")
    
    args = parser.parse_args()
    
    extract_images_from_pdf(args.pdf_file, args.output)
