from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        if username is None:
            return None
            
        # Intentar buscar por correo electrónico (insensible a mayúsculas/minúsculas)
        try:
            user = UserModel.objects.get(email__iexact=username)
            if user.check_password(password):
                return user
        except UserModel.DoesNotExist:
            pass
            
        # Intentar por nombre de usuario tradicional (insensible a mayúsculas/minúsculas)
        try:
            user = UserModel.objects.get(username__iexact=username)
            if user.check_password(password):
                return user
        except UserModel.DoesNotExist:
            return None
            
        return None
