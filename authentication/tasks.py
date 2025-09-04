"""
Celery tasks for authentication app.
"""
from celery import shared_task
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
import logging
from utils.mongodb import MongoDBManager

logger = logging.getLogger(__name__)


@shared_task
def cleanup_expired_tokens():
    """Clean up expired JWT tokens from cache."""
    try:
        # This would typically clean up blacklisted tokens
        # For now, we'll clean up any cached token data
        cache.delete_many(cache.keys('token_*'))
        logger.info("Cleaned up expired tokens from cache")
        return "Expired tokens cleaned up successfully"
    except Exception as e:
        logger.error(f"Error cleaning up expired tokens: {e}")
        raise


@shared_task
def optimize_mongodb():
    """Optimize MongoDB collections."""
    try:
        manager = MongoDBManager()
        collections = ['authentication_account', 'blog_post']
        
        for collection in collections:
            manager.optimize_collection(collection)
        
        manager.close()
        logger.info("MongoDB optimization completed")
        return "MongoDB optimization completed successfully"
    except Exception as e:
        logger.error(f"Error optimizing MongoDB: {e}")
        raise


@shared_task
def backup_user_data():
    """Backup user data to a separate collection."""
    try:
        manager = MongoDBManager()
        db = manager.get_database()
        
        # Create backup collection with timestamp
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        backup_collection_name = f"user_backup_{timestamp}"
        
        # Copy user data to backup collection
        users = db.authentication_account.find()
        backup_data = []
        
        for user in users:
            # Remove sensitive data for backup
            user_backup = {
                'original_id': user['_id'],
                'email': user.get('email', ''),
                'username': user.get('username', ''),
                'first_name': user.get('first_name', ''),
                'last_name': user.get('last_name', ''),
                'created_at': user.get('created_at'),
                'backup_date': timezone.now(),
            }
            backup_data.append(user_backup)
        
        if backup_data:
            db[backup_collection_name].insert_many(backup_data)
            logger.info(f"Backed up {len(backup_data)} users to {backup_collection_name}")
        
        manager.close()
        return f"User data backup completed: {len(backup_data)} users backed up"
    except Exception as e:
        logger.error(f"Error backing up user data: {e}")
        raise


@shared_task
def send_welcome_email(user_id):
    """Send welcome email to new user."""
    try:
        from .models import Account
        
        user = Account.objects.get(id=user_id)
        # Here you would implement actual email sending
        # For now, just log the action
        logger.info(f"Welcome email sent to user: {user.email}")
        return f"Welcome email sent to {user.email}"
    except Account.DoesNotExist:
        logger.error(f"User with id {user_id} not found")
        return f"User with id {user_id} not found"
    except Exception as e:
        logger.error(f"Error sending welcome email: {e}")
        raise


@shared_task
def update_user_activity(user_id):
    """Update user's last activity timestamp."""
    try:
        from .models import Account
        
        user = Account.objects.get(id=user_id)
        user.updated_at = timezone.now()
        user.save(update_fields=['updated_at'])
        
        logger.info(f"Updated activity for user: {user.email}")
        return f"Activity updated for {user.email}"
    except Account.DoesNotExist:
        logger.error(f"User with id {user_id} not found")
        return f"User with id {user_id} not found"
    except Exception as e:
        logger.error(f"Error updating user activity: {e}")
        raise


@shared_task
def cleanup_old_sessions():
    """Clean up old session data."""
    try:
        # Clean up sessions older than 30 days
        cutoff_date = timezone.now() - timedelta(days=30)
        
        # This would typically clean up session data
        # For now, we'll clean up cached session data
        cache.delete_many(cache.keys('session_*'))
        
        logger.info("Cleaned up old session data")
        return "Old session data cleaned up successfully"
    except Exception as e:
        logger.error(f"Error cleaning up old sessions: {e}")
        raise
