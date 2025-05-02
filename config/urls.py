from django.urls import path, include
from viewflow.contrib.admin import Admin
from viewflow.contrib.auth import AuthViewset
from viewflow.urls import Site, Application
from django_plotly_dash.views import routes

from grafico_ingresos.dashboard_viewset import GraficoIframeDashboard
from mi_dashboard.dashboard_viewset import ascensoresDashboard
from django_plotly_dash.views import routes
from dashboardOts.dashboard_viewset import DashboardOts
from partidas.dashboard_viewset import Partidas_presupuestarias
from grafico_salidas.dashboard_views import GraficoSalidas
from dashboard_operaciones.dashboard_views import DashboardOperaciones
from indicadores_preventivos.dashboard_views import IndicadoresPreventivos
from indicadores_torres.dashboard_views import IndicadoresTorres
from indicadores_vehiculos.dashboard_views import IndicadoresVehiculos
from indicadores_avance.dashboard_views import IndicadoresAvance
from indicadores_carrotensor.dashboard_views import IndicadoresCarroTensor
site = Site(
    title="Mantenimiento",
    primary_color="#3949ab",
    secondary_color="#5c6bc0",
    viewsets=[
        Application(
            title="Mi Teleferico",
            viewsets=[
                    DashboardOts(),
                    Partidas_presupuestarias(),
                    GraficoIframeDashboard(),
                    GraficoSalidas(),
                    ascensoresDashboard(),
                    DashboardOperaciones(),
                    IndicadoresPreventivos(),
                    IndicadoresTorres(),
                    IndicadoresVehiculos(),
                    IndicadoresAvance(),
                    IndicadoresCarroTensor(),
            ],
        ),
        Admin(),
    ],
)

urlpatterns = [
    path("", site.urls),
    path("accounts/", AuthViewset().urls),
    path('dash/', routes),
]