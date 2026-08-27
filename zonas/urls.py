from django.urls import path

from . import views

app_name = "zonas"

urlpatterns = [
    path("", views.listado_zonas, name="listado"),
    path("<int:zona_id>/", views.detalle_zona, name="detalle"),
]
