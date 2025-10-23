from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from .models import Farmacia, Repartidor, Cliente

class CustomLoginView(LoginView):
    """Vista de login personalizada que redirige según el tipo de usuario"""
    
    def get_success_url(self):
        """Determinar la URL de redirección según el tipo de usuario"""
        user = self.request.user
        
        # Verificar si es farmacéutico
        try:
            farmacia = Farmacia.objects.get(user=user)
            return reverse_lazy('panel_farmacia')
        except Farmacia.DoesNotExist:
            pass
        
        # Verificar si es repartidor
        try:
            repartidor = Repartidor.objects.get(user=user)
            return reverse_lazy('panel_repartidor')
        except Repartidor.DoesNotExist:
            pass
        
        # Verificar si es cliente
        try:
            cliente = Cliente.objects.get(user=user)
            return reverse_lazy('home')
        except Cliente.DoesNotExist:
            pass
        
        # Por defecto, ir al home
        return reverse_lazy('home')
