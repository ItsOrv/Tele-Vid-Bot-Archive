#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
تبدیل تصاویر PPM به JPG.
این اسکریپت تصاویر PPM موجود در دایرکتوری data/thumbnails را به فرمت JPG تبدیل می‌کند.
"""

import os
import sys
import glob

# تلاش برای واردکردن کتابخانه PIL
try:
    from PIL import Image
    HAS_PIL = True
    print("PIL/Pillow library available - will use it for conversion")
except ImportError:
    HAS_PIL = False
    print("PIL/Pillow not available - conversion may not work properly")

# دایرکتوری تامبنیل‌ها
thumbnails_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "thumbnails")

def convert_ppm_to_jpg(ppm_path):
    """تبدیل یک فایل PPM به JPG."""
    if not os.path.exists(ppm_path):
        print(f"فایل {ppm_path} وجود ندارد")
        return None
        
    # تولید مسیر فایل JPG
    jpg_path = os.path.splitext(ppm_path)[0] + ".jpg"
    
    if HAS_PIL:
        try:
            # باز کردن تصویر PPM با استفاده از PIL
            img = Image.open(ppm_path)
            # ذخیره به فرمت JPG
            img.save(jpg_path, "JPEG", quality=95)
            print(f"تصویر {ppm_path} به {jpg_path} تبدیل شد")
            return jpg_path
        except Exception as e:
            print(f"خطا در تبدیل {ppm_path}: {str(e)}")
            return None
    else:
        print(f"کتابخانه PIL در دسترس نیست، نمی‌توان {ppm_path} را تبدیل کرد")
        return None

def main():
    """تبدیل تمام تصاویر PPM به JPG."""
    # پیدا کردن تمام فایل‌های PPM
    ppm_files = glob.glob(os.path.join(thumbnails_dir, "*.ppm"))
    print(f"تعداد {len(ppm_files)} فایل PPM یافت شد")
    
    # تبدیل هر فایل
    converted = 0
    for ppm_file in ppm_files:
        jpg_path = convert_ppm_to_jpg(ppm_file)
        if jpg_path:
            converted += 1
            # حذف فایل اصلی PPM بعد از تبدیل موفق
            try:
                os.remove(ppm_file)
                print(f"فایل اصلی {ppm_file} حذف شد")
            except Exception as e:
                print(f"خطا در حذف فایل {ppm_file}: {str(e)}")
    
    print(f"تبدیل {converted} از {len(ppm_files)} فایل با موفقیت انجام شد")
    
    # باز کردن دایرکتوری تامبنیل‌ها
    if converted > 0:
        if sys.platform == "darwin":  # macOS
            os.system(f"open {thumbnails_dir}")
        elif sys.platform == "win32":  # Windows
            os.system(f"explorer {thumbnails_dir}")
        elif sys.platform == "linux" and os.path.exists("/usr/bin/xdg-open"):  # Linux with xdg-open
            os.system(f"xdg-open {thumbnails_dir}")

if __name__ == "__main__":
    main() 