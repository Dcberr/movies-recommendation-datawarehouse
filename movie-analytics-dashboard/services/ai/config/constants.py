# services/ai/config/constants.py

# 🎭 Keyword → Genre mapping
GENRE_KEYWORDS = {
    "Action": [
        "hành động", "hanh dong",
        "action", "combat", "đánh nhau", "danh nhau", "chiến đấu", "chien dau"
    ],
    "Comedy": [
        "hài", "hai",
        "hài hước", "hai huoc",
        "vui", "vui nhộn", "vui nhon",
        "funny", "comedy", "giải trí", "giai tri"
    ],
    "Family": [
        "trẻ em", "tre em",
        "kids", "family",
        "thiếu nhi", "thieu nhi",
        "gia đình", "gia dinh"
    ],
    "Adventure": [
        "phiêu lưu", "phieu luu",
        "adventure", "khám phá", "kham pha"
    ],
    "Drama": [
        "tâm lý", "tam ly",
        "drama", "cảm xúc", "cam xuc"
    ],
    "Fantasy": [
        "giả tưởng", "gia tuong",
        "fantasy", "phép thuật", "phep thuat", "magic"
    ],
    "Animation": [
        "hoạt hình", "hoat hinh",
        "animation", "cartoon", "anime"
    ],
    "Romance": [
        "tình cảm", "tinh cam",
        "romance", "love", "lãng mạn", "lang man"
    ],
    "Thriller": [
        "hồi hộp", "hoi hop",
        "thriller", "căng thẳng", "cang thang", "giật gân", "giat gan"
    ],
    "Horror": [
        "kinh dị", "kinh di",
        "horror", "ma", "ghê rợn", "ghe ron"
    ],
    "Crime": [
        "tội phạm", "toi pham",
        "crime", "hình sự", "hinh su"
    ],
    "Sci-Fi": [
        "khoa học viễn tưởng", "khoa hoc vien tuong",
        "sci fi", "sci-fi", "viễn tưởng", "vien tuong"
    ],
    "War": [
        "chiến tranh", "chien tranh",
        "war", "quân đội", "quan doi"
    ],
    "History": [
        "lịch sử", "lich su",
        "history", "cổ đại", "co dai"
    ],
    "Mystery": [
        "bí ẩn", "bi an",
        "mystery"
    ],
    "Music": [
        "âm nhạc", "am nhac",
        "music"
    ],
    "Musical": [
        "nhạc kịch", "nhac kich",
        "musical"
    ],
    "Documentary": [
        "tài liệu", "tai lieu",
        "documentary"
    ],
    "Biography": [
        "tiểu sử", "tieu su",
        "biography"
    ],
    "Sport": [
        "thể thao", "the thao",
        "sport"
    ],
    "Western": [
        "cao bồi", "cao boi",
        "western"
    ],
    "Film-Noir": [
        "đen tối", "den toi",
        "film noir"
    ],
    "Reality-TV": [
        "thực tế", "thuc te",
        "reality"
    ],
    "Talk-Show": [
        "talk show", "phỏng vấn", "phong van"
    ],
    "News": [
        "tin tức", "tin tuc",
        "news"
    ],
    "Short": [
        "phim ngắn", "phim ngan",
        "short"
    ],
    "Adult": [
        "18+", "người lớn", "nguoi lon",
        "adult"
    ],
    "Unknown": [
        "không rõ", "khong ro",
        "unknown"
    ]
}

SCORING_WEIGHTS = {
    "genre_match": 0.35,
    "rating": 0.45,
    "votes": 0.2
}

# 🎯 Số lượng recommend mặc định
TOP_K = 10