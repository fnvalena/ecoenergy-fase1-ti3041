"""
URL configuration for ecoenergy_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

from zonas import views as zonas_views

urlpatterns = [
    path('admin/', admin.site.urls),
    # La raíz redirige al listado de zonas, que es la pantalla de inicio del caso EcoEnergy.
    path('', RedirectView.as_view(pattern_name='zonas:listado'), name='inicio'),
    path('zonas/', include('zonas.urls')),
    # Requerimiento 3: interfaz "Resumen de consumo por zona".
    # Se registra a nivel raíz (fuera del include de 'zonas/') para que
    # la ruta final sea exactamente /resumen-zonas/, tal como lo pide
    # el enunciado (sección 3.1), reutilizando la vista de la app zonas.
    path('resumen-zonas/', zonas_views.resumen_zonas, name='resumen_zonas'),
]
