from django import forms
from django.core.exceptions import ValidationError
from .models import (
    Cliente, Farmacia, Repartidor, Producto, Pedido, 
    DetallePedido, Direccion, ObraSocial, MetodoPago,
    DescuentoObraSocial
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
        help_text="Sube una foto o PDF de tu receta médica",
        required=False
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
    
    def __init__(self, *args, **kwargs):
        requiere_receta = kwargs.pop('requiere_receta', False)
        super().__init__(*args, **kwargs)
        
        if requiere_receta:
            self.fields['archivo_receta'].required = True
            self.fields['archivo_receta'].help_text = "Sube una foto o PDF de tu receta médica (obligatorio)"
        else:
            self.fields['archivo_receta'].help_text = "Sube una foto o PDF de tu receta médica (opcional)"

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
    def __init__(self, *args, **kwargs):
        # Extraer la dirección del cliente si se proporciona
        direccion_cliente = kwargs.pop('direccion_cliente', None)
        super().__init__(*args, **kwargs)
        
        # Si hay una dirección del cliente, usarla como valores iniciales
        if direccion_cliente:
            self.fields['calle'].initial = direccion_cliente.calle
            self.fields['numero'].initial = direccion_cliente.numero
            self.fields['ciudad'].initial = direccion_cliente.ciudad
            self.fields['provincia'].initial = direccion_cliente.provincia
            self.fields['codigo_postal'].initial = direccion_cliente.codigo_postal
    
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
                'id': 'direccion-ciudad'
            }),
            'provincia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Provincia',
                'id': 'direccion-provincia'
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

# ===== FORMULARIOS PARA FARMACÉUTICOS =====

class ActualizarStockForm(forms.Form):
    """Formulario para actualizar stock de productos"""
    stock = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control stock-input',
            'min': '0',
            'step': '1',
            'placeholder': 'Cantidad en stock'
        }),
        label='Stock Disponible'
    )
    
    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        if stock is not None and stock < 0:
            raise forms.ValidationError('El stock no puede ser negativo.')
        return stock

class DescuentoObraSocialForm(forms.ModelForm):
    """Formulario para crear/editar descuentos por obra social"""
    class Meta:
        model = DescuentoObraSocial
        fields = ['producto', 'obra_social', 'descuento_porcentaje', 'descuento_fijo']
        widgets = {
            'producto': forms.Select(attrs={
                'class': 'form-control',
                'id': 'producto-descuento'
            }),
            'obra_social': forms.Select(attrs={
                'class': 'form-control',
                'id': 'obra-social-descuento'
            }),
            'descuento_porcentaje': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '100',
                'step': '0.01',
                'placeholder': '0.00',
                'id': 'descuento-porcentaje'
            }),
            'descuento_fijo': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'placeholder': '0.00',
                'id': 'descuento-fijo'
            }),
        }
        labels = {
            'descuento_porcentaje': 'Descuento Porcentual (%)',
            'descuento_fijo': 'Descuento Fijo ($)',
        }
    
    def __init__(self, *args, **kwargs):
        farmacia = kwargs.pop('farmacia', None)
        super().__init__(*args, **kwargs)
        
        if farmacia:
            # Filtrar productos solo de esta farmacia
            self.fields['producto'].queryset = Producto.objects.filter(
                farmacia=farmacia, 
                activo=True
            ).order_by('nombre')
        
        # Hacer que los campos de descuento sean opcionales
        self.fields['descuento_porcentaje'].required = False
        self.fields['descuento_fijo'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        descuento_porcentaje = cleaned_data.get('descuento_porcentaje')
        descuento_fijo = cleaned_data.get('descuento_fijo')
        
        # Validar que al menos uno de los descuentos esté presente
        if not descuento_porcentaje and not descuento_fijo:
            raise forms.ValidationError('Debe especificar al menos un tipo de descuento.')
        
        # Validar que no se especifiquen ambos tipos de descuento
        if descuento_porcentaje and descuento_fijo:
            raise forms.ValidationError('Solo puede especificar un tipo de descuento por vez.')
        
        # Validar rangos
        if descuento_porcentaje is not None and (descuento_porcentaje < 0 or descuento_porcentaje > 100):
            raise forms.ValidationError('El descuento porcentual debe estar entre 0 y 100.')
        
        if descuento_fijo is not None and descuento_fijo < 0:
            raise forms.ValidationError('El descuento fijo no puede ser negativo.')
        
        return cleaned_data

class ConfiguracionFarmaciaForm(forms.ModelForm):
    """Formulario para configurar datos de la farmacia"""
    class Meta:
        model = Farmacia
        fields = [
            'nombre', 'matricula', 'cuit', 'telefono', 
            'email_contacto', 'horario_apertura', 'horario_cierre'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la farmacia',
                'id': 'nombre-farmacia'
            }),
            'matricula': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Matrícula profesional',
                'id': 'matricula-farmacia'
            }),
            'cuit': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'CUIT',
                'id': 'cuit-farmacia'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono de contacto',
                'id': 'telefono-farmacia'
            }),
            'email_contacto': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email de contacto',
                'id': 'email-farmacia'
            }),
            'horario_apertura': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
                'id': 'horario-apertura'
            }),
            'horario_cierre': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
                'id': 'horario-cierre'
            }),
        }
        labels = {
            'email_contacto': 'Email de Contacto',
            'horario_apertura': 'Horario de Apertura',
            'horario_cierre': 'Horario de Cierre',
        }
    
    def clean_cuit(self):
        cuit = self.cleaned_data.get('cuit')
        if cuit:
            # Validar formato básico de CUIT
            cuit_clean = re.sub(r'[^\d]', '', cuit)
            if len(cuit_clean) != 11:
                raise forms.ValidationError('El CUIT debe tener 11 dígitos.')
        return cuit
    
    def clean_matricula(self):
        matricula = self.cleaned_data.get('matricula')
        if matricula:
            # Validar que la matrícula sea única
            if Farmacia.objects.filter(matricula=matricula).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError('Esta matrícula ya está registrada.')
        return matricula

class ConfiguracionDireccionFarmaciaForm(forms.ModelForm):
    """Formulario para configurar dirección de la farmacia"""
    class Meta:
        model = Direccion
        fields = ['calle', 'numero', 'ciudad', 'provincia', 'codigo_postal']
        widgets = {
            'calle': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la calle',
                'id': 'direccion-calle-farmacia'
            }),
            'numero': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número',
                'id': 'direccion-numero-farmacia'
            }),
            'ciudad': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ciudad',
                'id': 'direccion-ciudad-farmacia'
            }),
            'provincia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Provincia',
                'id': 'direccion-provincia-farmacia'
            }),
            'codigo_postal': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código postal',
                'id': 'direccion-codigo-postal-farmacia'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        calle = cleaned_data.get('calle')
        numero = cleaned_data.get('numero')
        ciudad = cleaned_data.get('ciudad')
        provincia = cleaned_data.get('provincia')
        
        # Validación básica
        if not all([calle, numero, ciudad, provincia]):
            raise forms.ValidationError('Todos los campos de dirección son obligatorios.')
        
        return cleaned_data

class ProductoForm(forms.ModelForm):
    """Formulario para crear/editar productos"""
    class Meta:
        model = Producto
        fields = [
            'nombre', 'descripcion', 'precio_base', 'codigo_barras',
            'categoria', 'laboratorio', 'requiere_receta', 'stock_disponible'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del producto',
                'id': 'producto-nombre'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción del producto',
                'id': 'producto-descripcion'
            }),
            'precio_base': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'placeholder': '0.00',
                'id': 'producto-precio'
            }),
            'codigo_barras': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código de barras',
                'id': 'producto-codigo-barras'
            }),
            'categoria': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Categoría',
                'id': 'producto-categoria'
            }),
            'laboratorio': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Laboratorio',
                'id': 'producto-laboratorio'
            }),
            'requiere_receta': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'producto-requiere-receta'
            }),
            'stock_disponible': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '1',
                'placeholder': '0',
                'id': 'producto-stock'
            }),
        }
        labels = {
            'precio_base': 'Precio Base ($)',
            'codigo_barras': 'Código de Barras',
            'requiere_receta': 'Requiere Receta Médica',
            'stock_disponible': 'Stock Disponible',
        }
    
    def __init__(self, *args, **kwargs):
        farmacia = kwargs.pop('farmacia', None)
        super().__init__(*args, **kwargs)
        
        if farmacia:
            self.instance.farmacia = farmacia
    
    def clean_precio_base(self):
        precio = self.cleaned_data.get('precio_base')
        if precio is not None and precio <= 0:
            raise forms.ValidationError('El precio debe ser mayor a 0.')
        return precio
    
    def clean_stock_disponible(self):
        stock = self.cleaned_data.get('stock_disponible')
        if stock is not None and stock < 0:
            raise forms.ValidationError('El stock no puede ser negativo.')
        return stock
