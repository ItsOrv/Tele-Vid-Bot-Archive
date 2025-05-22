# Tele-Vid-Bot-Archive

A Telegram bot for managing video links and video files organized by categories. Built with Telethon and SQLite.

## 🌟 Features

- **📁 Categories**: Organize videos into custom categories
- **🎬 Video Management**: Add, delete, and browse videos
- **🔒 Access Control**: Admin access and password-based temporary access for users
- **📱 Visual UI**: Clean interface with inline buttons for navigation
- **🗃 Smart Storage**: Store video files locally or save video links
- **🖼 Thumbnail Generation**: Automatically generate thumbnails for video files
- **🔍 Platform Detection**: Support for various video platforms like YouTube and Pornhub
- **🌐 URL Processing**: Extract information from URLs and detect video types and IDs

## 📋 Requirements

- Python 3.6+
- Dependencies listed in `requirements.txt`
- For Docker deployment: Docker and Docker Compose

## 🚀 Installation and Setup

### Method 1: Direct Installation

1. **Clone the repository:**
   ```
   git clone https://github.com/yourusername/Tele-Vid-Bot-Archive.git
   cd Tele-Vid-Bot-Archive
   ```

2. **Run the setup script:**
   ```
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Edit the `.env` file with your credentials:**
   - Get `API_ID` and `API_HASH` from [my.telegram.org/apps](https://my.telegram.org/apps)
   - Create a bot and get `BOT_TOKEN` from [@BotFather](https://t.me/BotFather)
   - Set your Telegram user ID as `ADMIN_ID` (you can get it from [@userinfobot](https://t.me/userinfobot))
   - Set an `ACCESS_PASSWORD` for temporary access

4. **Run the bot:**
   ```
   python main.py
   ```

### Method 2: Docker Installation

1. **Clone the repository:**
   ```
   git clone https://github.com/yourusername/Tele-Vid-Bot-Archive.git
   cd Tele-Vid-Bot-Archive
   ```

2. **Run the Docker setup script:**
   ```
   chmod +x docker-setup.sh
   ./docker-setup.sh
   ```

3. **Edit the `.env` file with your credentials.**

4. **Restart with new settings:**
   ```
   docker-compose up -d
   ```

5. **View logs:**
   ```
   docker-compose logs -f
   ```

## 📊 Database Structure

The bot uses SQLite with the following tables:

- **users**: For access control
  - `id`: User's Telegram ID
  - `username`: User's Telegram username
  - `access_until`: Access expiration timestamp

- **categories**: For organizing videos
  - `id`: Auto-incremented ID
  - `name`: Category name

- **videos**: For storing video information
  - `id`: Auto-incremented ID
  - `title`: Video title
  - `type`: Either 'file' or 'link'
  - `path_or_url`: File path or URL
  - `category_id`: Foreign key to categories
  - `thumbnail_path`: Path to thumbnail image
  - `platform`: Video platform (like youtube or pornhub)
  - `video_id`: Video ID on the original platform

## 📱 Usage

1. **Start the bot**: Send `/start` to the bot
   - If you're the admin, you'll get immediate access
   - If not, you'll need to enter the access password

2. **Main Menu**:
   - 📁 Categories: Browse videos by category
   - 🎬 Manage Videos: Add or delete videos
   - 🗂 Manage Categories: Add or delete categories

3. **Adding Videos**:
   - Enter video title
   - Upload video file or paste video link
   - Select the category

## 🧱 Project Structure

```
/Tele-Vid-Bot-Archive
├── main.py                     # Entry point
├── config.py                   # Configuration loader
├── .env                        # Environment variables
├── .env.example                # Example environment variables
├── requirements.txt            # Dependencies
├── Dockerfile                  # Docker configuration
├── docker-compose.yml          # Docker Compose configuration
├── setup.sh                    # Setup script
├── docker-setup.sh             # Docker setup script
├── DATA/                       # Video storage
│   ├── videos/                 # Video files
│   └── thumbnails/             # Thumbnail images
├── database/
│   ├── __init__.py
│   └── database.py             # Database operations
├── handlers/
│   ├── __init__.py
│   ├── auth_handler.py         # Authentication
│   ├── category_handler.py     # Category management
│   └── video_handler.py        # Video management
├── utils/
│   ├── __init__.py
│   └── media_utils.py          # Media handling utilities
└── tests/
    ├── data/                   # Test data
    │   ├── thumbnails/         # Test thumbnails
    │   └── url_tests/          # URL test results
    ├── url_thumbnail_tester.py # URL thumbnail tester
    ├── simple_url_tester.py    # Simple URL tester
    ├── convert_ppm_to_jpg.py   # PPM to JPG converter
    ├── generate_sample_thumbnails.py # Sample thumbnail generator
    └── README_thumbnails.md    # Thumbnail tools documentation
```

## 🐳 Docker Commands

- **Build and run:**
  ```
  docker-compose up -d
  ```

- **View logs:**
  ```
  docker-compose logs -f
  ```

- **Stop:**
  ```
  docker-compose down
  ```

- **Rebuild:**
  ```
  docker-compose up -d --build
  ```

## 📜 License

MIT License