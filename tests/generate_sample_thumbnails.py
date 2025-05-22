#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
تولید نمونه تامبنیل برای آزمایش.
این اسکریپت چند تصویر نمونه در دایرکتوری thumbnails ایجاد می‌کند تا استخراج تامبنیل را شبیه‌سازی کند.
"""

import os
import sys
import json
import time
import random
import datetime
from urllib.parse import urlparse

# تلاش برای واردکردن کتابخانه PIL
try:
    from PIL import Image
    HAS_PIL = True
    print("PIL/Pillow library available - will use it for high-quality JPG images")
except ImportError:
    HAS_PIL = False
    print("PIL/Pillow not available - will use basic image generation methods")

# دایرکتوری تامبنیل‌ها
thumbnails_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "thumbnails")
os.makedirs(thumbnails_dir, exist_ok=True)

def generate_color_data(width=320, height=180, color=None):
    """تولید داده‌های تصویر رنگی ساده."""
    if color is None:
        # تولید یک رنگ تصادفی
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    
    if HAS_PIL:
        # ایجاد تصویر با استفاده از PIL
        img = Image.new('RGB', (width, height), color=color)
        return img
    else:
        # ایجاد داده‌های PPM برای یک تصویر رنگی ساده
        ppm_header = f"P6\n{width} {height}\n255\n"
        
        # تولید داده‌های پیکسل
        pixel_data = bytearray()
        for _ in range(width * height):
            pixel_data.extend([color[0], color[1], color[2]])
        
        return ppm_header.encode() + pixel_data

def generate_gradient_image(width=320, height=180, color1=None, color2=None):
    """تولید یک تصویر گرادیان از رنگ 1 به رنگ 2."""
    if color1 is None:
        color1 = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    if color2 is None:
        color2 = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    
    if HAS_PIL:
        # ایجاد تصویر با استفاده از PIL
        img = Image.new('RGB', (width, height))
        pixels = img.load()
        
        for y in range(height):
            for x in range(width):
                # محاسبه درصد مکان در محور x
                r = color1[0] + (color2[0] - color1[0]) * x // width
                g = color1[1] + (color2[1] - color1[1]) * x // width
                b = color1[2] + (color2[2] - color1[2]) * x // width
                pixels[x, y] = (r, g, b)
        
        return img
    else:
        # ایجاد داده‌های PPM برای تصویر گرادیان
        ppm_header = f"P6\n{width} {height}\n255\n"
        
        # تولید داده‌های پیکسل
        pixel_data = bytearray()
        for y in range(height):
            for x in range(width):
                # محاسبه درصد مکان در محور x
                r = color1[0] + (color2[0] - color1[0]) * x // width
                g = color1[1] + (color2[1] - color1[1]) * x // width
                b = color1[2] + (color2[2] - color1[2]) * x // width
                pixel_data.extend([r, g, b])
        
        return ppm_header.encode() + pixel_data

def save_image_file(data, filename, description=None):
    """ذخیره داده‌های تصویر به فایل JPG."""
    # اطمینان از اینکه فایل با پسوند jpg است
    if not filename.lower().endswith('.jpg'):
        filename = os.path.splitext(filename)[0] + '.jpg'
    
    filepath = os.path.join(thumbnails_dir, filename)
    
    if HAS_PIL and isinstance(data, Image.Image):
        # ذخیره تصویر PIL به فرمت JPG
        try:
            data.save(filepath, "JPEG", quality=95)
            print(f"تصویر PIL به فایل JPG ذخیره شد: {filepath}")
            return filepath
        except Exception as e:
            print(f"خطا در ذخیره تصویر PIL: {str(e)}")
            return None
    elif not HAS_PIL and isinstance(data, bytes):
        # تبدیل داده‌های PPM به فایل
        try:
            # برای حالتی که PIL در دسترس نیست، فایل PPM را با پسوند jpg ذخیره می‌کنیم
            # (این کار آیدال نیست، اما برای نمایش کارکرد مناسب است)
            with open(filepath, 'wb') as f:
                f.write(data)
            print(f"داده‌های باینری به فایل JPG ذخیره شد: {filepath}")
            return filepath
        except Exception as e:
            print(f"خطا در ذخیره داده‌های باینری: {str(e)}")
            return None
    else:
        print(f"قالب داده‌های تصویر نامعتبر است: {type(data)}")
        return None

def get_timestamp():
    """تولید یک رشته زمان فعلی."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def generate_thumbnails(url="https://www.pornhub.com/view_video.php?viewkey=68012db864390"):
    """تولید تامبنیل‌های نمونه برای یک URL."""
    domain = urlparse(url).netloc
    
    # تولید چند تصویر نمونه
    thumbnails = []
    
    # 1. تصویر ساده (رنگ قرمز)
    red_image = generate_color_data(color=(230, 30, 30))
    red_path = save_image_file(red_image, "thumbnail_red.jpg", "تصویر قرمز ساده")
    if red_path:
        thumbnails.append({
            "path": red_path,
            "method": "solid_color",
            "description": "تصویر قرمز ساده به عنوان پیش‌فرض برای خطاها",
            "timestamp": get_timestamp()
        })
    
    # 2. تصویر ساده (رنگ آبی)
    blue_image = generate_color_data(color=(30, 30, 230))
    blue_path = save_image_file(blue_image, "thumbnail_blue.jpg", "تصویر آبی ساده")
    if blue_path:
        thumbnails.append({
            "path": blue_path,
            "method": "solid_color",
            "description": "تصویر آبی ساده به عنوان پیش‌فرض برای خطاها",
            "timestamp": get_timestamp()
        })
    
    # 3. تصویر گرادیان
    gradient_image = generate_gradient_image(
        color1=(255, 165, 0),  # نارنجی
        color2=(128, 0, 128)   # بنفش
    )
    gradient_path = save_image_file(gradient_image, "thumbnail_gradient.jpg", "تصویر گرادیان")
    if gradient_path:
        thumbnails.append({
            "path": gradient_path,
            "method": "gradient",
            "description": "تصویر گرادیان نارنجی به بنفش",
            "timestamp": get_timestamp()
        })
    
    # 4. تصویر گرادیان دیگر
    gradient_image2 = generate_gradient_image()  # رنگ‌های تصادفی
    gradient_path2 = save_image_file(gradient_image2, "thumbnail_gradient2.jpg", "تصویر گرادیان تصادفی")
    if gradient_path2:
        thumbnails.append({
            "path": gradient_path2,
            "method": "gradient_random",
            "description": "تصویر گرادیان با رنگ‌های تصادفی",
            "timestamp": get_timestamp()
        })
    
    # ذخیره خلاصه به صورت JSON
    summary = {
        "url": url,
        "domain": domain,
        "timestamp": get_timestamp(),
        "thumbnails": thumbnails,
        "methods_tested": ["solid_color", "gradient"],
        "total_thumbnails": len(thumbnails)
    }
    
    summary_path = os.path.join(thumbnails_dir, "summary.json")
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f"خلاصه در مسیر {summary_path} ذخیره شد")
    print(f"تعداد {len(thumbnails)} تصویر در مسیر {thumbnails_dir} تولید شد")
    
    # چاپ مسیر مطلق
    print(f"مسیر مطلق دایرکتوری تامبنیل‌ها: {os.path.abspath(thumbnails_dir)}")
    
    return thumbnails

if __name__ == "__main__":
    generate_thumbnails()
    
    # سعی در باز کردن دایرکتوری تامبنیل‌ها در مرورگر فایل
    print("\nتلاش برای باز کردن دایرکتوری تامبنیل‌ها...")
    try:
        if sys.platform == "darwin":  # macOS
            os.system(f"open {thumbnails_dir}")
        elif sys.platform == "win32":  # Windows
            os.system(f"explorer {thumbnails_dir}")
        elif sys.platform == "linux" and os.path.exists("/usr/bin/xdg-open"):  # Linux
            os.system(f"xdg-open {thumbnails_dir}")
        else:
            print(f"لطفاً به صورت دستی به مسیر زیر بروید:")
            print(f"{os.path.abspath(thumbnails_dir)}")
    except Exception as e:
        print(f"خطا در باز کردن دایرکتوری: {str(e)}")
        print(f"لطفاً به صورت دستی به مسیر زیر بروید:")
        print(f"{os.path.abspath(thumbnails_dir)}") 