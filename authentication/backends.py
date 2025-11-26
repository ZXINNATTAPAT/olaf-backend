from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class EmailBackend(ModelBackend):
    """
    Custom authentication backend that allows users to log in using their email address.
    """
    def authenticate(self, request, username=None, password=None, email=None, **kwargs):
        UserModel = get_user_model()
        
        # Support both 'email' and 'username' parameters
        email_to_check = email or username
        
        if email_to_check is None:
            return None
            
        try:
            user = UserModel.objects.get(email=email_to_check)
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user
            UserModel().set_password(password)
            return None
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        return None

    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
