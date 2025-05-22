FROM python:3.10-slim

# تنظیم محیط کاری
WORKDIR /app

# کپی فایل‌های مورد نیاز
COPY requirements.txt ./

# نصب وابستگی‌های مورد نیاز
RUN pip install --no-cache-dir -r requirements.txt

# کپی کد منبع
COPY . .

# ایجاد دایرکتوری‌های مورد نیاز
RUN mkdir -p DATA/videos DATA/thumbnails

# تنظیم متغیرهای محیطی
ENV PYTHONUNBUFFERED=1

# اجرای برنامه
CMD ["python", "main.py"] 