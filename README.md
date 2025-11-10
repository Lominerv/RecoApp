# 📚 RecoApp — Intelligent Book Recommendation System

**RecoApp** is a desktop application built with **Python + PyQt6** that helps users discover new books based on their personal preferences, ratings, and favorites.  
It combines a sleek UI, a local SQLite database, and a tag-based recommendation algorithm.

---

## 🚀 Features

- 🔑 **User Authentication**
  - Sign up, sign in, and log out
  - Role separation: regular user and admin

- 💡 **Book Recommendations**
  - Personalized recommendations based on ratings and favorites  
  - Requires at least 3 rated books to activate the recommendation system

- ⭐ **Rating System**
  - Rate and unrate books (1–5 stars)
  - Automatically updates average book ratings

- ❤️ **Favorites**
  - Add or remove books from favorites  
  - Browse all favorite books in one place

- 🧠 **Admin Panel**
  - Add, edit, or delete books  
  - View system statistics: total users, books, and active sessions

- 🖼️ **Modern UI**
  - Built with PyQt6 and QSS styling  
  - Dynamic book cards with adaptive layout (`FlowLayout`)  
  - Custom message dialogs (`FancyMessageBox`) for smooth UX

---

## 🧩 Project Structure
app/
├── ui/
│ ├── main_window.py # Main window & navigation logic
│ ├── widgets/
│ │ ├── add_book_dialog.py # Add new book dialog
│ │ ├── book_card.py # Book card widget
│ │ ├── fancy_message_box.py # Custom message dialogs
│ │ └── flow_layout.py # Adaptive layout for cards
│ └── style_gray.qss # Application stylesheet
│
├── services/
│ ├── auth_service.py # Authentication logic
│ ├── catalog_service.py # Book catalog operations
│ ├── rating_service.py # Rating management
│ ├── favorites_service.py # Favorites handling
│ ├── admin_service.py # Admin panel operations
│ └── recommendation_service.py# Tag-based recommendations
│
├── repositories/
│ ├── users_repo.py # User repository
│ ├── books_repo.py # Book repository
│ ├── ratings_repo.py # Ratings repository
│ ├── favorites_repo.py # Favorites repository
│ └── tags_repo.py # Tag management
│
├── db/
│ └── connection.py # SQLite connection
│
├── assets/
│ ├── icons/ # Interface icons
│ └── placeholders/ # Cover placeholders
│
└── config.py # Global configuration


---

## ⚙️ Tech Stack

- **Python 3.11+**
- **PyQt6** — GUI framework
- **SQLite3** — Local database
- **bcrypt** — Password hashing
- **QSS** — Styling for UI components

---

## 🧠 Recommendation Algorithm

RecoApp analyzes the books a user has **rated** or **added to favorites**,  
extracts the most frequent tags, and recommends similar books based on those tags.

Example:
> If you rate several books tagged *fantasy* or *adventure*, the system will recommend other books with similar tags.

---

## 🛡️ User Roles

| Role | Capabilities |
|------|---------------|
| 👤 User | Browse catalog, rate books, manage favorites |
| 👑 Admin | Add/edit/delete books, view statistics |

---

## 🔧 Installation & Launch

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/RecoApp.git
   cd RecoApp
📦 Future Plans

🔍 Advanced search and filtering

🧩 Machine-learning-based recommendations

🌐 Cloud synchronization

📤 Export/import user library

👨‍💻 Author

Arthur — aspiring Machine Learning engineer and software developer.
RecoApp is a personal project built to combine AI + UX and make book discovery intelligent and engaging.
