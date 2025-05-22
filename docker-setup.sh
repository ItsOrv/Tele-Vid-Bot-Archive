#!/bin/bash

# رنگ‌ها
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # بدون رنگ

echo -e "${YELLOW}شروع راه‌اندازی ربات Tele-Vid-Bot-Archive با داکر...${NC}"

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

# بررسی نصب داکر و داکر کامپوز
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}داکر نصب نشده است. لطفاً ابتدا داکر را نصب کنید.${NC}"
    echo "https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}داکر کامپوز نصب نشده است. لطفاً ابتدا داکر کامپوز را نصب کنید.${NC}"
    echo "https://docs.docker.com/compose/install/"
    exit 1
fi

# ساخت و اجرای کانتینرها
echo -e "${YELLOW}در حال ساخت و اجرای کانتینرها...${NC}"
docker-compose up -d --build

echo -e "${GREEN}راه‌اندازی با داکر با موفقیت انجام شد!${NC}"
echo -e "${YELLOW}برای مشاهده لاگ‌ها، دستور زیر را وارد کنید:${NC}"
echo "docker-compose logs -f"

exit 0 