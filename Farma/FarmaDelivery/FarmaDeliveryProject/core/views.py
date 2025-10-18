from django.shortcuts import render

# Importamos este decorador para forzar el inicio de sesión
from django.contrib.auth.decorators import login_required 

# Esta vista solo se ejecuta si el usuario está logueado
@login_required 
def home_page(request):
    # El render busca tu archivo en la ruta: 'core/pagina_principal.html'
    return render(request, 'core/index.html')
# Create your views here.
