from django import forms
from django.core.exceptions import ValidationError
from .models import (
    Cliente, Farmacia, Repartidor, Producto, Pedido, 
    DetallePedido, Direccion, ObraSocial, MetodoPago
)
import re

class BusquedaProductoForm(forms.Form):
    """Formulario para buscar productos"""
    busqueda = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar medicamentos, productos...',
            'id': 'busqueda-producto'
        }),
        required=False
    )
    categoria = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Categoría (opcional)',
            'id': 'categoria-producto'
        }),
        required=False
    )
    farmacia = forms.ModelChoiceField(
        queryset=Farmacia.objects.filter(activa=True),
        empty_label="Todas las farmacias",
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'farmacia-producto'
        }),
        required=False
    )

class RecetaForm(forms.Form):
    """Formulario para subir receta médica"""
    archivo_receta = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*,.pdf',
            'id': 'archivo-receta'
        }),
        help_text="Sube una foto o PDF de tu receta médica (opcional)"
    )
    observaciones_receta = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Observaciones adicionales sobre la receta...',
            'id': 'observaciones-receta'
        }),
        required=False,
        help_text="Información adicional sobre la receta"
    )

class ConfirmacionPedidoForm(forms.Form):
    """Formulario para confirmar el pedido"""
    metodo_pago = forms.ChoiceField(
        choices=MetodoPago.choices,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'metodo-pago'
        })
    )
    observaciones = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Instrucciones especiales para la entrega...',
            'id': 'observaciones-pedido'
        }),
        required=False,
        help_text="Instrucciones especiales para la entrega"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar las opciones de método de pago
        self.fields['metodo_pago'].choices = [
            ('', 'Selecciona método de pago'),
            (MetodoPago.EFECTIVO, 'Efectivo'),
            (MetodoPago.TARJETA_DEBITO, 'Tarjeta de Débito'),
            (MetodoPago.TARJETA_CREDITO, 'Tarjeta de Crédito'),
            (MetodoPago.TRANSFERENCIA, 'Transferencia Bancaria'),
            (MetodoPago.MERCADO_PAGO, 'Mercado Pago'),
        ]

class DireccionForm(forms.ModelForm):
    """Formulario para crear/editar direcciones"""
    class Meta:
        model = Direccion
        fields = ['calle', 'numero', 'ciudad', 'provincia', 'codigo_postal']
        widgets = {
            'calle': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la calle',
                'id': 'direccion-calle'
            }),
            'numero': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número',
                'id': 'direccion-numero'
            }),
            'ciudad': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ciudad',
                'id': 'direccion-ciudad',
                'value': 'Buenos Aires'
            }),
            'provincia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Provincia',
                'id': 'direccion-provincia',
                'value': 'Buenos Aires'
            }),
            'codigo_postal': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código postal',
                'id': 'direccion-codigo-postal'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        calle = cleaned_data.get('calle')
        numero = cleaned_data.get('numero')
        ciudad = cleaned_data.get('ciudad')
        provincia = cleaned_data.get('provincia')
        
        # Validación básica
        if not all([calle, numero]):
            raise forms.ValidationError('Calle y número son obligatorios.')
        
        return cleaned_data

class PerfilClienteForm(forms.ModelForm):
    """Formulario para editar perfil del cliente"""
    class Meta:
        model = Cliente
        fields = ['telefono', 'fecha_nacimiento', 'obra_social']
        widgets = {
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de teléfono'
            }),
            'fecha_nacimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'obra_social': forms.Select(attrs={
                'class': 'form-control'
            })
        }

class ContactoForm(forms.Form):
    """Formulario de contacto para soporte"""
    nombre = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tu nombre'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'tu@email.com'
        })
    )
    asunto = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Asunto del mensaje'
        })
    )
    mensaje = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Escribe tu mensaje aquí...'
        })
    )
