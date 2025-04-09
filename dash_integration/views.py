# dash_integration/views.py
from django.views.generic import TemplateView

class DashAppView(TemplateView):
    template_name = 'dash_integration/dashboard.html'

dash_view = DashAppView.as_view()