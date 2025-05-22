#!/bin/bash

# رنگ‌ها
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # بدون رنگ

echo -e "${YELLOW}شروع راه‌اندازی ربات Tele-Vid-Bot-Archive...${NC}"

# بررسی وجود فایل .env
if [ ! -f .env ]; then
    echo -e "${YELLOW}فایل .env یافت نشد، در حال ایجاد از روی نمونه...${NC}"
    cp .env.example .env
    echo -e "${GREEN}فایل .env ایجاد شد. لطفاً آن را با تنظیمات خود ویرایش کنید.${NC}"
    echo -e "${YELLOW}برای ویرایش فایل .env، دستور زیر را وارد کنید:${NC}"
    echo "nano .env"
    exit 1
fi

# ایجاد دایرکتوری‌های مورد نیاز
echo -e "${YELLOW}در حال ایجاد دایرکتوری‌های مورد نیاز...${NC}"
mkdir -p DATA/videos DATA/thumbnails

# نصب وابستگی‌ها
echo -e "${YELLOW}در حال نصب وابستگی‌ها...${NC}"
pip install -r requirements.txt

echo -e "${GREEN}راه‌اندازی با موفقیت انجام شد!${NC}"
echo -e "${YELLOW}برای اجرای ربات، دستور زیر را وارد کنید:${NC}"
echo "python main.py"

exit 0 