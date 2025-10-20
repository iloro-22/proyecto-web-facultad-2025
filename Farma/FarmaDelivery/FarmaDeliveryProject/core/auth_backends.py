from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from core.models import Cliente

class DNIAuthBackend(ModelBackend):
    """
    Backend de autenticación que permite login con DNI
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None
        
        try:
            # Intentar encontrar cliente por DNI
            cliente = Cliente.objects.get(dni=username)
            user = cliente.user
            
            # Verificar contraseña
            if user.check_password(password):
                return user
        except Cliente.DoesNotExist:
            pass
        
        # Si no se encuentra por DNI, intentar con username normal
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            pass
        
        return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
