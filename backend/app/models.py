"""
MakuUP Studio — MongoEngine Models
All business data stored in MongoDB Atlas.
"""
import datetime
import mongoengine as me


# ──────────────────────────────────────────────
# 1. BOOKING
# ──────────────────────────────────────────────
class Booking(me.Document):
    STATUS_CHOICES = ('new', 'contacted', 'confirmed')

    name       = me.StringField(required=True, max_length=200)
    email      = me.EmailField(required=True)
    phone      = me.StringField(max_length=20)
    service    = me.StringField(required=True, max_length=100)
    date       = me.StringField(required=True)   # stored as "YYYY-MM-DD"
    message    = me.StringField(default='')
    status     = me.StringField(default='new', choices=STATUS_CHOICES)
    created_at = me.DateTimeField(default=datetime.datetime.utcnow)

    meta = {
        'collection': 'bookings',
        'ordering': ['-created_at'],
        'indexes': ['date', 'status', 'email'],
    }

    def __str__(self):
        return f"{self.name} – {self.service} on {self.date}"


# ──────────────────────────────────────────────
# 2. TESTIMONIAL
# ──────────────────────────────────────────────
class Testimonial(me.Document):
    name       = me.StringField(required=True, max_length=200)
    location   = me.StringField(max_length=200)
    service    = me.StringField(max_length=100)
    quote      = me.StringField(required=True)
    rating     = me.IntField(default=5, min_value=1, max_value=5)
    avatar_bg  = me.StringField(default='linear-gradient(135deg, #e96cba, #a855f7)')
    initial    = me.StringField(max_length=1, default='')
    is_visible = me.BooleanField(default=True)
    created_at = me.DateTimeField(default=datetime.datetime.utcnow)

    meta = {
        'collection': 'testimonials',
        'ordering': ['-created_at'],
    }

    def save(self, *args, **kwargs):
        if self.name and not self.initial:
            self.initial = self.name[0].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.rating}★)"


# ──────────────────────────────────────────────
# 3. PORTFOLIO IMAGE
# ──────────────────────────────────────────────
class PortfolioImage(me.Document):
    CATEGORY_CHOICES = ('bridal', 'editorial', 'glam', 'other')

    title      = me.StringField(required=True, max_length=200)
    category   = me.StringField(required=True, choices=CATEGORY_CHOICES, default='other')
    image_url  = me.StringField(required=True)          # Cloudinary URL
    public_id  = me.StringField(default='')             # Cloudinary public_id (for deletion)
    alt_text   = me.StringField(max_length=300, default='')
    is_visible = me.BooleanField(default=True)
    sort_order = me.IntField(default=0)
    created_at = me.DateTimeField(default=datetime.datetime.utcnow)

    meta = {
        'collection': 'portfolio',
        'ordering': ['sort_order', '-created_at'],
    }

    def __str__(self):
        return f"{self.title} [{self.category}]"


# ──────────────────────────────────────────────
# 4. SERVICE (for admin price management)
# ──────────────────────────────────────────────
class Service(me.Document):
    slug       = me.StringField(required=True, unique=True, max_length=50)
    name       = me.StringField(required=True, max_length=200)
    description = me.StringField(default='')
    price_from = me.IntField(default=0)                 # in INR
    is_featured = me.BooleanField(default=False)
    is_active  = me.BooleanField(default=True)
    sort_order = me.IntField(default=0)

    meta = {
        'collection': 'services',
        'ordering': ['sort_order'],
    }

    def __str__(self):
        return f"{self.name} (₹{self.price_from}+)"
