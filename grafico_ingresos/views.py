# grafico_ingresos/views.py
from django.views.generic import TemplateView

class GraficoIngresoIframeView(TemplateView):
    template_name = "grafico_ingresos/grafico_ingresos_iframe.html"
