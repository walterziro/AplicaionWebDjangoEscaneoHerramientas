from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, View
from django.http import HttpResponse
from django.db import IntegrityError
from django.db.models import Q
from django.urls import reverse
from .utils import get_admin_data, get_administrador_by_user
from .forms import ReporteUsuarioForm, ReporteUsuarioFilterForm, GeneracionInformeForm
from .models import Usuario, ReporteUsuario, ReporteAdmin, Administrador

import uuid
import csv
from io import BytesIO, StringIO
from django.utils import timezone
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import base64


# ----------------------------------------------------------------------
# VISTA PÚBLICA - REPORTAR ERROR
# ----------------------------------------------------------------------
class ReportarErrorView(View):
    template_name = 'web_admin/reportar_error.html'
    
    def get_user_id_from_cookie(self, request):
        usuario_uid = request.COOKIES.get('user_report_id')
        if not usuario_uid:
            usuario_uid = 'anon-' + str(uuid.uuid4())[:18]
        try:
            usuario_db = Usuario.objects.get(uid=usuario_uid)
        except Usuario.DoesNotExist:
            try:
                usuario_db = Usuario.objects.create(uid=usuario_uid)
            except IntegrityError:
                return None, None
        return usuario_uid, usuario_db

    def render_form_page(self, request, form, usuario_uid, success_message=None):
        context = {
            'form': form,
            'titulo': 'Reportar Error o Sugerencia',
            'usuario_anonimo_id': usuario_uid,
            'success_message': success_message
        }
        response = render(request, self.template_name, context)
        response.set_cookie('user_report_id', usuario_uid, max_age=365 * 24 * 60 * 60)
        return response

    def get(self, request, *args, **kwargs):
        usuario_uid, usuario_db = self.get_user_id_from_cookie(request)
        if not usuario_db:
            return redirect(reverse('web_admin:home'))
        form = ReporteUsuarioForm(initial={'usuario_uid': usuario_uid})
        return self.render_form_page(request, form, usuario_uid)

    def post(self, request, *args, **kwargs):
        usuario_uid, usuario_db = self.get_user_id_from_cookie(request)
        if not usuario_db:
            return redirect(reverse('web_admin:home'))
        form = ReporteUsuarioForm(request.POST)
        if form.is_valid():
            reporte = form.save(commit=False)
            reporte.usuario = usuario_db
            # Asignar la fecha del reporte al momento actual si no fue proporcionada
            if not reporte.fecha_reporte:
                reporte.fecha_reporte = timezone.now()
            reporte.estado = 'pendiente'
            reporte.save()
            form = ReporteUsuarioForm(initial={'usuario_uid': usuario_uid})
            return self.render_form_page(
                request,
                form,
                usuario_uid,
                success_message="¡Reporte enviado con éxito! Gracias por tu retroalimentación."
            )
        return self.render_form_page(request, form, usuario_uid)


def home(request):
    """Vista del Home PÚBLICO."""
    context = {
        'titulo': 'Identificador de Herramientas Iniciales - Portal de Acceso',
        'mensaje': 'Bienvenido. Selecciona tu rol para continuar.',
    }
    return render(request, 'web_admin/home.html', context)


# ----------------------------------------------------------------------
# DASHBOARD ADMIN
# ----------------------------------------------------------------------
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'web_admin/dashboard.html'
    login_url = '/admin/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        admin_data, _ = get_admin_data(self.request.user)
        if not admin_data:
            context['error'] = 'No se encontró el administrador asociado a tu cuenta.'
            return context
        context.update({
            'admin_data': admin_data,
            'titulo': "Dashboard - Menú Principal",
        })
        return context


# ----------------------------------------------------------------------
# GESTIÓN DE REPORTES ADMIN
# ----------------------------------------------------------------------
class ReporteAdminView(LoginRequiredMixin, TemplateView):
    template_name = 'web_admin/gestionar_reportes.html'
    login_url = '/admin/login/'

    # -------------------------------
    # Funciones auxiliares
    # -------------------------------
    def _generar_csv_content(self, reportes):
        csvfile = StringIO()
        writer = csv.writer(csvfile)
        writer.writerow(['ID', 'Fecha Reporte', 'Tipo', 'Estado', 'Herramienta', 'Usuario UID', 'Descripción'])
        for r in reportes:
            writer.writerow([
                r.id,
                r.fecha_reporte.strftime("%Y-%m-%d %H:%M:%S") if r.fecha_reporte else "",
                r.tipo,
                r.estado,
                r.herramienta.nombre if r.herramienta else 'N/A',
                r.usuario.uid,
                r.descripcion.replace('\n', ' ').strip() if r.descripcion else ''
            ])
        content_bytes = csvfile.getvalue().encode('utf-8')
        return content_bytes, f"reporte_admin_{timezone.now().strftime('%Y%m%d_%H%M')}.csv"

    def _generar_pdf_content(self, reportes):
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        c.setFont("Helvetica", 12)
        c.drawString(50, 800, "Informe Administrativo - Reportes de Usuario")
        c.drawString(50, 785, f"Generado: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
        y = 760
        for r in reportes:
            text = f"ID {r.id} | Tipo: {r.tipo} | Estado: {r.estado} | Usuario: {r.usuario.uid}"
            c.drawString(50, y, text[:110])
            y -= 15
            if y < 100:
                c.showPage()
                c.setFont("Helvetica", 12)
                y = 800
        c.save()
        buffer.seek(0)
        return buffer.getvalue(), f"reporte_admin_{timezone.now().strftime('%Y%m%d_%H%M')}.pdf"

    # -------------------------------
    # GET y POST
    # -------------------------------
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        admin_data, _ = get_admin_data(self.request.user)
        context['admin_data'] = admin_data
        context['titulo'] = "Gestión de Reportes de Usuario"

        filter_form = ReporteUsuarioFilterForm(self.request.GET)
        context['filter_form'] = filter_form

        reportes_query = ReporteUsuario.objects.all().select_related('usuario', 'herramienta', 'administrador').order_by('-fecha_reporte')
        if filter_form.is_valid():
            cleaned = filter_form.cleaned_data
            if cleaned.get('estado'):
                reportes_query = reportes_query.filter(estado=cleaned['estado'])
            if cleaned.get('tipo'):
                reportes_query = reportes_query.filter(tipo=cleaned['tipo'])

        context['reportes_filtrados'] = reportes_query
        context['generacion_form'] = GeneracionInformeForm()

        if self.request.GET.get('archivos_listos') == 'true':
            csv_ready = 'temp_csv_data' in self.request.session
            pdf_ready = 'temp_pdf_data' in self.request.session

            if csv_ready or pdf_ready:
                context['descarga_doble_activa'] = True
                context['alerta_exito'] = "Informes generados con éxito. Utilice los botones de abajo para descargar sus archivos."

                if csv_ready:
                    context['csv_download_url'] = reverse('web_admin:descarga_csv_temp')
                    context['csv_filename'] = self.request.session.get('temp_csv_filename', 'reporte.csv')

                if pdf_ready:
                    context['pdf_download_url'] = reverse('web_admin:descarga_pdf_temp')
                    context['pdf_filename'] = self.request.session.get('temp_pdf_filename', 'reporte.pdf')
            else:
                context['alerta_error'] = "Error: Los archivos temporales han expirado o no se encontraron."

        return context

    def post(self, request, *args, **kwargs):
        reporte_ids = request.POST.getlist('reporte_id')
        generacion_form = GeneracionInformeForm(request.POST)

        if not reporte_ids or not generacion_form.is_valid():
            return redirect(reverse('web_admin:gestionar_reportes') + '?error_rep=validation_error')

        formato = generacion_form.cleaned_data['formato']
        reportes = ReporteUsuario.objects.filter(id__in=reporte_ids).select_related('usuario', 'herramienta')
        admin_instance = get_administrador_by_user(request.user)

        csv_content = None
        pdf_content = None
        csv_filename = None
        pdf_filename = None

        if formato in ['csv', 'ambos']:
            csv_content, csv_filename = self._generar_csv_content(reportes)
        if formato in ['pdf', 'ambos']:
            pdf_content, pdf_filename = self._generar_pdf_content(reportes)

        # Guardar los archivos binarios en la base de datos
        if admin_instance:
            ReporteUsuario.objects.filter(id__in=reporte_ids).update(
                estado='revisado', administrador=admin_instance
            )
            if csv_content:
                ReporteAdmin.objects.create(
                    administrador=admin_instance,
                    tipo_reporte="Informe CSV",
                    fecha_generacion=timezone.now(),
                    parametros_filtro={'reporte_ids': reporte_ids},
                    periodo="actual",
                    archivo_binario=csv_content,
                    url_descarga=csv_filename
                )
            if pdf_content:
                ReporteAdmin.objects.create(
                    administrador=admin_instance,
                    tipo_reporte="Informe PDF",
                    fecha_generacion=timezone.now(),
                    parametros_filtro={'reporte_ids': reporte_ids},
                    periodo="actual",
                    archivo_binario=pdf_content,
                    url_descarga=pdf_filename
                )

        if (formato == 'csv' and csv_content) or (formato == 'pdf' and pdf_content):
            content = csv_content if formato == 'csv' else pdf_content
            filename = csv_filename if formato == 'csv' else pdf_filename
            content_type = 'text/csv' if formato == 'csv' else 'application/pdf'
            response = HttpResponse(content, content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response

        elif formato == 'ambos' and csv_content and pdf_content:
            request.session['temp_csv_data'] = base64.b64encode(csv_content).decode('ascii')
            request.session['temp_csv_filename'] = csv_filename
            request.session['temp_pdf_data'] = base64.b64encode(pdf_content).decode('ascii')
            request.session['temp_pdf_filename'] = pdf_filename
            return redirect(reverse('web_admin:gestionar_reportes') + '?archivos_listos=true')

        else:
            return redirect(reverse('web_admin:gestionar_reportes') + '?error_rep=no_archivo_generado_o_invalido')


# ----------------------------------------------------------------------
# DESCARGAS TEMPORALES (para doble descarga)
# ----------------------------------------------------------------------
class DescargaCSVTemporalView(View):
    def get(self, request, *args, **kwargs):
        csv_data_base64 = request.session.pop('temp_csv_data', None)
        csv_filename = request.session.pop('temp_csv_filename', None)
        if csv_data_base64 and csv_filename:
            csv_data_bytes = base64.b64decode(csv_data_base64.encode('ascii'))
            response = HttpResponse(csv_data_bytes, content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{csv_filename}"'
            return response
        else:
            return redirect(reverse('web_admin:gestionar_reportes') + '?error_rep=csv_no_disponible')


class DescargaPDFTemporalView(View):
    def get(self, request, *args, **kwargs):
        pdf_data_base64 = request.session.pop('temp_pdf_data', None)
        pdf_filename = request.session.pop('temp_pdf_filename', None)
        if pdf_data_base64 and pdf_filename:
            pdf_data_bytes = base64.b64decode(pdf_data_base64.encode('ascii'))
            response = HttpResponse(pdf_data_bytes, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{pdf_filename}"'
            return response
        else:
            return redirect(reverse('web_admin:gestionar_reportes') + '?error_rep=pdf_no_disponible')


# ----------------------------------------------------------------------
# DESCARGA DIRECTA DESDE BASE DE DATOS
# ----------------------------------------------------------------------
class DescargarReporteBDView(View):
    def get(self, request, reporte_id):
        try:
            reporte = get_object_or_404(ReporteAdmin, id=reporte_id)
        except ReporteAdmin.DoesNotExist:
            return HttpResponse("Reporte no encontrado.", status=404)

        if not reporte.archivo_binario:
            return HttpResponse("El reporte no tiene archivo almacenado en la base de datos.", status=404)

        is_pdf = "PDF" in (reporte.tipo_reporte or "").upper()
        filename = reporte.url_descarga if reporte.url_descarga else f"reporte_{reporte.id}.{'pdf' if is_pdf else 'csv'}"
        content_type = "application/pdf" if is_pdf else "text/csv"

        response = HttpResponse(reporte.archivo_binario, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename=\"{filename}\"'
        return response
