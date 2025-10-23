from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import transaction
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

# --- TUS FORMULARIOS DE REGISTRO (ADAPTADOS) ---

class ClienteSignUpForm(UserCreationForm):
    dni = forms.CharField(max_length=8, required=True, label="DNI")
    first_name = forms.CharField(max_length=150, required=True, label="Nombre")
    last_name = forms.CharField(max_length=150, required=True, label="Apellido")

    # Adaptado para usar el modelo ObraSocial
    obra_social = forms.ModelChoiceField(
        queryset=ObraSocial.objects.all(),
        required=False,
        empty_label="No tengo / No informar",
        label="Obra Social"
    )
    numero_afiliado = forms.CharField(max_length=50, required=False, label="N° Afiliado (Opcional)")

    # Campos adaptados para el modelo Direccion
    calle = forms.CharField(max_length=100, required=True)
    numero = forms.CharField(max_length=10, required=True)
    entre_calles = forms.CharField(max_length=255, required=False)
    ciudad = forms.CharField(max_length=50, required=True, initial="Buenos Aires")
    provincia = forms.CharField(max_length=50, required=True, initial="Buenos Aires")
    codigo_postal = forms.CharField(max_length=10, required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'email')

    def clean_dni(self):
        dni = self.cleaned_data.get('dni')
        if Cliente.objects.filter(dni=dni).exists():
            raise forms.ValidationError("Ya existe un cliente registrado con este DNI.")
        if User.objects.filter(username=dni).exists():
             raise forms.ValidationError("Este DNI ya está asociado a otra cuenta.")
        return dni

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['dni'] # Usamos DNI como username
        if commit:
            user.save()
            # Guardamos el modelo Direccion
            direccion = Direccion.objects.create(
                calle=self.cleaned_data.get('calle'),
                numero=self.cleaned_data.get('numero'),
                entre_calles=self.cleaned_data.get('entre_calles'),
                ciudad=self.cleaned_data.get('ciudad'),
                provincia=self.cleaned_data.get('provincia'),
                codigo_postal=self.cleaned_data.get('codigo_postal'),
            )
            # Creamos el Cliente
            Cliente.objects.create(
                user=user,
                dni=self.cleaned_data.get('dni'),
                obra_social=self.cleaned_data.get('obra_social'),
                numero_afiliado=self.cleaned_data.get('numero_afiliado'),
                direccion=direccion # Asignamos la Direccion
            )
        return user

class FarmaciaSignUpForm(UserCreationForm):
    dni = forms.CharField(max_length=8, required=True, label="DNI del Responsable")
    nombre_farmacia = forms.CharField(max_length=150, required=True, label="Nombre de la Farmacia")
    cuit = forms.CharField(max_length=13, required=True, label="CUIT")
    matricula = forms.CharField(max_length=50, required=True, label="Matrícula")
    telefono = forms.CharField(max_length=20, required=True)
    email_contacto = forms.EmailField(required=True, label="Email de Contacto")

    # Campos adaptados para el modelo Direccion
    calle = forms.CharField(max_length=100, required=True)
    numero = forms.CharField(max_length=10, required=True)
    entre_calles = forms.CharField(max_length=255, required=False)
    ciudad = forms.CharField(max_length=50, required=True, initial="Buenos Aires")
    provincia = forms.CharField(max_length=50, required=True, initial="Buenos Aires")
    codigo_postal = forms.CharField(max_length=10, required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email',) # 'username' se autocompleta con DNI

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['dni'] # Usamos DNI como username
        if commit:
            user.save()
            direccion = Direccion.objects.create(
                calle=self.cleaned_data.get('calle'),
                numero=self.cleaned_data.get('numero'),
                entre_calles=self.cleaned_data.get('entre_calles'),
                ciudad=self.cleaned_data.get('ciudad'),
                provincia=self.cleaned_data.get('provincia'),
                codigo_postal=self.cleaned_data.get('codigo_postal'),
            )
            # Creamos la Farmacia usando los nombres de campos del equipo
            Farmacia.objects.create(
                user=user,
                nombre=self.cleaned_data.get('nombre_farmacia'), # 'nombre' en el modelo
                cuit=self.cleaned_data.get('cuit'),
                matricula=self.cleaned_data.get('matricula'),
                telefono=self.cleaned_data.get('telefono'),
                email_contacto=self.cleaned_data.get('email_contacto'),
                direccion=direccion, # Asignamos la Direccion
                activa=False # Inicia inactiva
            )
        return user

class RepartidorSignUpForm(UserCreationForm):
    dni = forms.CharField(max_length=8, required=True, label="DNI")
    first_name = forms.CharField(max_length=150, required=True, label="Nombre")
    last_name = forms.CharField(max_length=150, required=True, label="Apellido")
    telefono = forms.CharField(max_length=20, required=True)

    # Tu lógica de vehículo
    tipo_vehiculo = forms.ChoiceField(choices=Repartidor.TIPO_VEHICULO, required=True, label="Tipo de Vehículo")
    patente = forms.CharField(max_length=10, required=False, label="Patente (si es Moto)")
    cedula_vehiculo = forms.ImageField(required=False, label="Foto de Cédula (si es Moto)")

    # Adaptado a Direccion
    calle = forms.CharField(max_length=100, required=True)
    numero = forms.CharField(max_length=10, required=True)
    entre_calles = forms.CharField(max_length=255, required=False)
    ciudad = forms.CharField(max_length=50, required=True, initial="Buenos Aires")
    provincia = forms.CharField(max_length=50, required=True, initial="Buenos Aires")
    codigo_postal = forms.CharField(max_length=10, required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'email')

    def clean(self):
        cleaned_data = super().clean()
        tipo_vehiculo = cleaned_data.get('tipo_vehiculo')
        patente = cleaned_data.get('patente')
        cedula = cleaned_data.get('cedula_vehiculo')

        if tipo_vehiculo == 'MOTO':
            if not patente:
                self.add_error('patente', 'La patente es obligatoria si el vehículo es una motocicleta.')
            if not cedula:
                self.add_error('cedula_vehiculo', 'La foto de la cédula es obligatoria si el vehículo es una motocicleta.')
        elif tipo_vehiculo == 'BICI':
             cleaned_data['patente'] = None
             cleaned_data['cedula_vehiculo'] = None
        return cleaned_data

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['dni'] # DNI como username
        if commit:
            user.save()
            direccion = Direccion.objects.create(
                calle=self.cleaned_data.get('calle'),
                numero=self.cleaned_data.get('numero'),
                entre_calles=self.cleaned_data.get('entre_calles'),
                ciudad=self.cleaned_data.get('ciudad'),
                provincia=self.cleaned_data.get('provincia'),
                codigo_postal=self.cleaned_data.get('codigo_postal'),
            )
            # Creamos el Repartidor
            Repartidor.objects.create(
                user=user,
                dni=self.cleaned_data.get('dni'),
                telefono=self.cleaned_data.get('telefono'),
                tipo_vehiculo=self.cleaned_data.get('tipo_vehiculo'),
                patente=self.cleaned_data.get('patente'),
                cedula_vehiculo=self.cleaned_data.get('cedula_vehiculo'),
                direccion=direccion, # Asignamos la Direccion
                activo=False # Inicia inactivo
            )
        return user