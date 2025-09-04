"""
MongoEngine models for MongoDB collections.
"""
from mongoengine import Document, StringField, DateTimeField, BooleanField, IntField
from mongoengine import connect, disconnect
from django.conf import settings
import datetime


class MongoAccount(Document):
    """MongoDB Account model using MongoEngine."""
    
    email = StringField(required=True, unique=True, max_length=255)
    username = StringField(required=True, max_length=50)
    first_name = StringField(required=True, max_length=30)
    last_name = StringField(required=True, max_length=30)
    phone = StringField(required=True, max_length=15)
    
    is_admin = BooleanField(default=False)
    is_active = BooleanField(default=True)
    is_staff = BooleanField(default=False)
    is_superuser = BooleanField(default=False)
    
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    updated_at = DateTimeField(default=datetime.datetime.utcnow)
    
    meta = {
        'collection': 'authentication_account',
        'indexes': [
            'email',
            'username',
            'created_at',
            ('email', 'username'),
        ]
    }
    
    def __str__(self):
        return self.username
    
    @property
    def full_name(self):
        """Return user's full name."""
        return f"{self.first_name} {self.last_name}".strip()
    
    def save(self, *args, **kwargs):
        """Override save to update updated_at timestamp."""
        self.updated_at = datetime.datetime.utcnow()
        return super().save(*args, **kwargs)


class MongoPost(Document):
    """MongoDB Post model using MongoEngine."""
    
    title = StringField(required=True, max_length=200)
    content = StringField(required=True)
    author_id = StringField(required=True, max_length=24)  # Reference to MongoAccount
    author_username = StringField(required=True, max_length=50)
    
    is_published = BooleanField(default=True)
    view_count = IntField(default=0)
    
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    updated_at = DateTimeField(default=datetime.datetime.utcnow)
    
    meta = {
        'collection': 'blog_post',
        'indexes': [
            'title',
            'author_id',
            'created_at',
            ('title', 'content'),  # Text search index
        ]
    }
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        """Override save to update updated_at timestamp."""
        self.updated_at = datetime.datetime.utcnow()
        return super().save(*args, **kwargs)


def connect_to_mongodb():
    """Connect to MongoDB using MongoEngine."""
    try:
        mongodb_settings = getattr(settings, 'MONGODB_SETTINGS', {})
        if mongodb_settings:
            connect(**mongodb_settings)
            print("✅ Connected to MongoDB successfully!")
            return True
        else:
            print("⚠️ MongoDB settings not found")
            return False
    except Exception as e:
        print(f"⚠️ MongoDB connection failed: {e}")
        return False


def disconnect_from_mongodb():
    """Disconnect from MongoDB."""
    try:
        disconnect()
        print("✅ Disconnected from MongoDB")
    except Exception as e:
        print(f"⚠️ Error disconnecting from MongoDB: {e}")


def create_sample_data():
    """Create sample data in MongoDB collections."""
    try:
        # Create sample accounts
        if not MongoAccount.objects(email="admin@example.com").first():
            admin = MongoAccount(
                email="admin@example.com",
                username="admin",
                first_name="Admin",
                last_name="User",
                phone="0812345678",
                is_admin=True,
                is_staff=True,
                is_superuser=True
            )
            admin.save()
            print("✅ Created admin account")
        
        if not MongoAccount.objects(email="user@example.com").first():
            user = MongoAccount(
                email="user@example.com",
                username="testuser",
                first_name="Test",
                last_name="User",
                phone="0812345679",
                is_admin=False,
                is_staff=False,
                is_superuser=False
            )
            user.save()
            print("✅ Created test user account")
        
        # Create sample posts
        admin = MongoAccount.objects(email="admin@example.com").first()
        if admin and not MongoPost.objects(title="Welcome to Our Blog").first():
            post1 = MongoPost(
                title="Welcome to Our Blog",
                content="This is the first post on our blog. Welcome everyone!",
                author_id=str(admin.id),
                author_username=admin.username
            )
            post1.save()
            print("✅ Created sample post 1")
        
        if admin and not MongoPost.objects(title="MongoDB Integration").first():
            post2 = MongoPost(
                title="MongoDB Integration",
                content="We have successfully integrated MongoDB with our Django application using MongoEngine.",
                author_id=str(admin.id),
                author_username=admin.username
            )
            post2.save()
            print("✅ Created sample post 2")
        
        print("✅ Sample data created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        return False
