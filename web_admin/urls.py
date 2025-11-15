# web_admin/urls.py

from django.urls import path
from . import views

app_name = 'web_admin'

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('reportar-error/', views.ReportarErrorView.as_view(), name='reportar_error'),
    path('gestionar-reportes/', views.ReporteAdminView.as_view(), name='gestionar_reportes'),
    path('descarga-csv-temp/', views.DescargaCSVTemporalView.as_view(), name='descarga_csv_temp'), 
    path('descarga-pdf-temp/', views.DescargaPDFTemporalView.as_view(), name='descarga_pdf_temp'),
    path('descargar-bd/<int:reporte_id>/', views.DescargarReporteBDView.as_view(), name='descargar_bd'),
    
]

