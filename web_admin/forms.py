# web_admin/forms.py

from django import forms
from .models import Herramienta, ReporteUsuario, Administrador

class ReporteUsuarioForm(forms.ModelForm):
    # 🚨 DEFINICIÓN DE CHOICES PARA EL CAMPO 'TIPO'
    TIPO_REPORTES_CHOICES = [
        ('Error de Detección', 'Error de Detección'),
        ('Sugerencia', 'Sugerencia'),
        ('Falla de App', 'Falla de App'),
    ]

    # Campo oculto para llevar el UID anónimo/de sesión
    usuario_uid = forms.CharField(widget=forms.HiddenInput()) 

    # 🚨 1. SOBRESCRIBIR EL CAMPO 'tipo' COMO ChoiceField
    tipo = forms.ChoiceField(
        choices=TIPO_REPORTES_CHOICES,
        label='Tipo de Reporte',
        widget=forms.Select(attrs={'class': 'form-select'}) # Usamos select widget
    )

    class Meta:
        model = ReporteUsuario
        # Incluimos 'tipo' en fields, pero ya lo hemos redefinido arriba.
        fields = ['usuario_uid', 'herramienta', 'tipo', 'descripcion'] 
        
        widgets = {
            # 2. Eliminamos el TextInput para 'tipo'
            'descripcion': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Describe el problema o sugerencia en detalle...'}),
        }
        labels = {
            'herramienta': 'Herramienta Relacionada (Opcional)',
            # 'tipo' ya tiene label arriba
            'descripcion': 'Retroalimentación detallada',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['herramienta'].queryset = Herramienta.objects.all().order_by('nombre')
        self.fields['herramienta'].empty_label = "--- No aplica (Error general) ---"

        # Aplicamos la clase 'form-control' al campo 'descripcion' para estilo
        self.fields['descripcion'].widget.attrs.update({'class': 'form-control'}) 
        
        # Aplicamos la clase 'form-select' al campo 'herramienta'
        self.fields['herramienta'].widget.attrs.update({'class': 'form-select'})
        
# --- Nuevo Formulario de Filtros para el Dashboard ---
class ReporteUsuarioFilterForm(forms.Form):
    # Opciones de estado (basadas en la tabla ReporteUsuario)
    ESTADO_CHOICES = [
        ('', 'Todos los estados'),
        ('pendiente', 'Pendiente'),
        ('revisado', 'Revisado'),
        ('resuelto', 'Resuelto'),
    ]
    
    # Opciones de tipo (puedes expandir estas según la data real)
    TIPO_CHOICES = [
        ('', 'Todos los tipos'),
        ('Error de Detección', 'Error de Detección'),
        ('Sugerencia', 'Sugerencia'),
        ('Falla de App', 'Falla de App'),
    ]

    estado = forms.ChoiceField(
        choices=ESTADO_CHOICES,
        required=False,
        label='Estado',
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )
    
    tipo = forms.ChoiceField(
        choices=TIPO_CHOICES,
        required=False,
        label='Tipo',
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )
    
    fecha_inicio = forms.DateField(
        required=False,
        label='Desde',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-sm'})
    )

    fecha_fin = forms.DateField(
        required=False,
        label='Hasta',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-sm'})
    )
    
    # Campo de búsqueda por texto libre
    busqueda = forms.CharField(
        required=False,
        label='Buscar Descripción/UID',
        widget=forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Descripción o UID'})
    )

class GeneracionInformeForm(forms.Form):
    # 🚨 NUEVA OPCIÓN 'ambos'
    FORMATO_CHOICES = [
        ('csv', 'CSV (Hoja de Cálculo)'),
        ('pdf', 'PDF (Documento Físico)'),
        ('ambos', 'Ambos (CSV y PDF)'),
    ]
    
    formato = forms.ChoiceField(
        choices=FORMATO_CHOICES,
        required=True,
        label='Formato de Salida',
        initial='csv', # Opción por defecto
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )