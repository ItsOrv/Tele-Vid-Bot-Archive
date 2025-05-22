# URL Thumbnail Tester

این ابزار برای تست استخراج تامبنیل و پریویو از انواع مختلف لینک‌ها طراحی شده است.

## قابلیت‌ها

- استخراج تامبنیل از لینک‌های ویدیویی (یوتیوب، ویمو، دیلی‌موشن)
- استخراج تصاویر پیش‌نمایش از صفحات وب
- پشتیبانی از انواع متدهای مختلف برای یافتن تصاویر (OpenGraph, Twitter Cards, Schema.org)
- نمایش گزارش جزئیات از روش‌های موفق و ناموفق
- ذخیره تصاویر استخراج شده در فولدر مشخص

## نیازمندی‌ها

برای نصب نیازمندی‌ها:

```bash
pip install -r requirements_tester.txt
```

## نحوه استفاده

### اجرای مستقیم:

```bash
python url_thumbnail_tester.py https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

### اجرا با درخواست ورودی:

```bash
python url_thumbnail_tester.py
```

سپس URL مورد نظر را وارد کنید.

### مشخص کردن دایرکتوری خروجی:

```bash
python url_thumbnail_tester.py -o /path/to/output/dir
```

## متدهای استخراج تامبنیل

این اسکریپت از متدهای زیر برای استخراج تامبنیل استفاده می‌کند:

1. **متدهای اختصاصی پلتفرم‌ها**:
   - یوتیوب: دسترسی مستقیم به تصاویر تامبنیل با کیفیت‌های مختلف
   - ویمو: استفاده از API رسمی برای دریافت تامبنیل
   - دیلی‌موشن: استفاده از API رسمی برای دریافت تامبنیل

2. **متدهای عمومی**:
   - **OpenGraph**: استخراج تگ‌های `og:image` از متادیتای صفحه
   - **Twitter Cards**: استخراج تگ‌های `twitter:image` از متادیتای صفحه
   - **Schema.org**: استخراج اطلاعات تصویر از ساختار JSON-LD
   - **بزرگترین تصویر**: یافتن و استخراج بزرگترین تصویر موجود در صفحه

## خروجی‌ها

اسکریپت گزارشی از متدهای تست شده و موفق نمایش می‌دهد و تصاویر استخراج شده را در دایرکتوری مشخص شده ذخیره می‌کند.

## مثال گزارش

```
============================================================
URL Thumbnail Test Results for: https://www.youtube.com/watch?v=dQw4w9WgXcQ
============================================================

Domain: www.youtube.com
Methods tested: 6
Successful methods: 2
Thumbnails generated: 2

Successful methods:
  - youtube_hq
  - opengraph

Generated thumbnails:
  - youtube_hq: /tmp/url_thumbnails/a1b2c3d4_youtube_hq.jpg
  - opengraph: /tmp/url_thumbnails/e5f6g7h8_opengraph.jpg

Detailed Method Results:
------------------------------------------------------------
  youtube_api: ✅ Success
  opengraph: ✅ Success
  twitter_card: ❌ Failed
  schema_org: ❌ Failed
  largest_image: ❌ Failed
  screenshot: ❌ Failed
============================================================ 