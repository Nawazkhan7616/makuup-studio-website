# 💄 MakuUP Studio Website

> A premium beauty studio booking & AI-powered beauty advisor platform built for **MakuUP Studio** by Noor Khan, Mumbai.

![MakuUP Studio](./images/hero_model.png)

---

## ✨ Features

### 🌐 Main Website (`index.html`)
- Stunning hero section with animated effects
- Services showcase (Bridal, Editorial, Sangeet & more)
- Portfolio gallery with category filters
- Client testimonials section
- **Booking form** — clients can request appointments directly
- Confirmation email sent automatically on booking
- Fully responsive across all devices

### 🤖 Glow Guide AI (`/glow-guide`)
- **AI Chatbot** — powered by Google Gemini for beauty advice
- **Skin Analysis** — personalised skin type quiz & routine generator
- **Hair Analysis** — hair health quiz & weekly care plan
- **Nail Care** — nail health analysis & recommendations
- **User authentication** — each user gets their own private AI experience
- **Daily beauty tips** blog

### 🛡️ Admin Dashboard (`dashboard.html`)
- Secure login with JWT authentication
- View all booking enquiries with client details
- Filter bookings by date, status, or search by name/email
- Update booking status (New → Contacted → Confirmed)
- View & approve pending client testimonials
- See submission date & time (IST) for every booking

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | HTML5, CSS3 (Vanilla), JavaScript (ES6+) |
| **Backend** | Python 3.14, Django 4.2, Django REST Framework |
| **Database** | MongoDB Atlas (via MongoEngine) |
| **AI** | Google Gemini API (`gemini-2.0-flash`) |
| **Auth** | JWT (SimpleJWT) |
| **Email** | SMTP (Gmail / custom domain) |
| **Payments** | Razorpay (configured) |
| **Deployment** | Railway (backend) · GitHub Pages / Firebase (frontend) |

---

## 📁 Project Structure

```
MakuUP Studio Website/
├── index.html              # Main website
├── dashboard.html          # Admin dashboard
├── script.js               # Frontend JS
├── style.css               # Main styles
├── images/                 # Website images
├── glow-guide/             # Glow Guide AI module
│   ├── index.html          # Glow Guide home
│   ├── chatbot/            # AI chatbot
│   ├── skin-analysis/      # Skin quiz
│   ├── hair-analysis/      # Hair quiz
│   ├── nail-care/          # Nail quiz
│   ├── dashboard/          # User dashboard
│   ├── auth/               # Login / register
│   └── blog/               # Daily tips
└── backend/                # Django REST API
    ├── manage.py
    ├── requirements.txt
    ├── .env.example        # ← copy to .env and fill in secrets
    ├── app/                # Main app (bookings, auth, portfolio)
    │   ├── models.py
    │   ├── views.py
    │   ├── serializers.py
    │   └── services/       # Email, WhatsApp, Payment
    ├── glow_guide/         # Glow Guide AI backend
    └── makuup/             # Django project settings
        └── settings/
            ├── base.py
            ├── dev.py
            └── prod.py
```

---

## 🚀 Getting Started (Local Development)

### 1. Clone the repository
```bash
git clone https://github.com/Nawazkhan7616/makuup-studio-website.git
cd makuup-studio-website
```

### 2. Set up the backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### 3. Configure environment variables
```bash
copy .env.example .env
# Open .env and fill in your credentials
```

### 4. Run the backend
```bash
python manage.py runserver
# API running at http://127.0.0.1:8000
```

### 5. Run the frontend
```bash
# From project root
python -m http.server 5500
# Website at http://127.0.0.1:5500
```

---

## 🔑 Environment Variables

Create `backend/.env` from `backend/.env.example`:

```env
# Django
SECRET_KEY=your-django-secret-key
DEBUG=True

# MongoDB Atlas
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_DB_NAME=makuup_studio

# Email (SMTP)
EMAIL_HOST_USER=hello@makuupstudio.in
EMAIL_HOST_PASSWORD=your-email-password

# Google Gemini AI
GEMINI_API_KEY=your-gemini-api-key

# Razorpay (optional)
RAZORPAY_KEY_ID=your-key
RAZORPAY_KEY_SECRET=your-secret
```

> ⚠️ **Never commit your `.env` file** — it is in `.gitignore` and kept private.

---

## 📡 API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/api/health/` | Health check | Public |
| `POST` | `/api/bookings/create/` | Submit booking | Public |
| `GET` | `/api/bookings/list/` | List all bookings | Admin |
| `PATCH` | `/api/bookings/update-status/:id/` | Update status | Admin |
| `DELETE` | `/api/bookings/delete/:id/` | Delete booking | Admin |
| `POST` | `/api/auth/login/` | Admin login | Public |
| `POST` | `/api/auth/logout/` | Admin logout | Admin |
| `GET` | `/api/testimonials/` | Public testimonials | Public |
| `POST` | `/api/glow-guide/chat/` | AI chatbot | User |
| `POST` | `/api/glow-guide/skin-analysis/` | Skin analysis | User |
| `POST` | `/api/glow-guide/hair-analysis/` | Hair analysis | User |

---

## 🎨 Services Offered

- 👰 Bridal Makeup
- 📸 Editorial & Fashion
- 💃 Sangeet & Event
- 💍 Engagement Ceremony
- 🌿 Mehendi Ceremony
- ✨ Everyday Glam
- 🎓 Makeup Lessons
- 🧴 Pre-Bridal Skincare Prep

---

## 👤 Admin Access

The admin dashboard is at `/dashboard.html`. Contact the studio owner for credentials.

---

## 📸 Screenshots

### 🌐 Main Website
![Main Website](./screenshots/screenshot_home.png)

### 🛡️ Admin Dashboard
![Admin Dashboard](./screenshots/screenshot_dashboard.png)

---

## 📄 License

This project is proprietary. All rights reserved © 2026 **MakuUP Studio by Noor Khan**.

---

<div align="center">
  Made with 💕 for <strong>MakuUP Studio</strong> · Mumbai
</div>
