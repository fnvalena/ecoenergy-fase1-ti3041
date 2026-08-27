from django.shortcuts import render

from . import data_access


def listado_zonas(request):
    """
    Vista de listado (CA-01, CA-02).
    Muestra todas las zonas registradas con nombre, límite y cantidad
    de dispositivos. Si no hay zonas, el template muestra el mensaje
    "No hay zonas disponibles" (boceto 1).
    """
    zonas = data_access.listar_zonas_con_resumen()
    contexto = {
        "zonas": zonas,
    }
    return render(request, "zonas/listado_zonas.html", contexto)


def detalle_zona(request, zona_id):
    """
    Vista de detalle (CA-03, CA-04, CA-05, CA-07, CA-08).
    Muestra los dispositivos de la zona, su categoría, el consumo
    total y el estado (NORMAL/ALERTA).

    Si la zona no existe, se renderiza un template propio de "no
    encontrado" con status=404 explícito (CA-08). Esto asegura una
    respuesta controlada independiente del valor de settings.DEBUG,
    en vez de depender de la página técnica por defecto de Django.
    """
    detalle = data_access.obtener_detalle_zona(zona_id)
    if detalle is None:
        return render(
            request,
            "zonas/zona_no_encontrada.html",
            {"zona_id": zona_id},
            status=404,
        )

    return render(request, "zonas/detalle_zona.html", detalle)


def resumen_zonas(request):
    """
    Vista "Resumen de consumo por zona" (Requerimiento 3).

    Delega toda la agregación (conteos, sumas y la clasificación
    DENTRO DEL LÍMITE / LÍMITE SUPERADO) en data_access.resumen_por_zona(),
    y solo arma el contexto que el template va a presentar. El template
    no contiene lógica de agregación: recibe listas y totales ya
    calculados.
    """
    contexto = data_access.resumen_por_zona()
    return render(request, "zonas/resumen_zonas.html", contexto)
