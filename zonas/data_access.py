"""
Capa de acceso a datos de EcoEnergy.

Este módulo NO usa Models ni ORM. Lee directamente los archivos JSON
(zonas.json, categorias.json, dispositivos.json) y resuelve las
relaciones entre ellos usando estructuras Python (diccionarios y listas).

Cada función vuelve a leer los archivos en cada llamada, por lo que si
el docente modifica el JSON durante la revisión, el próximo request ya
refleja el cambio (no hay caché ni datos "congelados" en memoria).
"""

import json
from pathlib import Path

from django.conf import settings
from jsonschema import validate as validar_esquema
from jsonschema.exceptions import ValidationError

# Umbral de consumo: por sobre el límite de la zona, el estado es ALERTA.
ESTADO_NORMAL = "NORMAL"
ESTADO_ALERTA = "ALERTA"

# Textos de estado exigidos por la regla de negocio del Resumen por zona
# (Requerimiento 3, sección 3.3). Se mantienen separados de ESTADO_NORMAL/
# ESTADO_ALERTA porque el enunciado exige literalmente estos textos para
# esta interfaz, aunque la comparación (consumo_total vs limite_kwh) sea
# la misma regla que ya usa calcular_estado().
ESTADO_DENTRO_LIMITE = "DENTRO DEL LÍMITE"
ESTADO_LIMITE_SUPERADO = "LÍMITE SUPERADO"

# Esquemas mínimos (claves obligatorias y tipos) exigidos en la sección 4.2
# del enunciado. jsonschema se usa para descartar registros mal formados
# sin detener la aplicación (refuerza CA-02/CA-06: procesar colecciones
# que crecen o cambian sin exigir cambios de código).
ESQUEMA_ZONA = {
    "type": "object",
    "required": ["id", "nombre", "limite_kwh"],
    "properties": {
        "id": {"type": "integer"},
        "nombre": {"type": "string"},
        "limite_kwh": {"type": "number"},
    },
}

ESQUEMA_CATEGORIA = {
    "type": "object",
    "required": ["id", "nombre", "descripcion"],
    "properties": {
        "id": {"type": "integer"},
        "nombre": {"type": "string"},
        "descripcion": {"type": "string"},
    },
}

ESQUEMA_DISPOSITIVO = {
    "type": "object",
    "required": ["id", "nombre", "consumo_kwh", "zona_id", "categoria_id"],
    "properties": {
        "id": {"type": "integer"},
        "nombre": {"type": "string"},
        "consumo_kwh": {"type": "number"},
        "zona_id": {"type": "integer"},
        "categoria_id": {"type": "integer"},
    },
}


def _leer_json(nombre_archivo):
    """
    Lee un archivo JSON desde settings.DATA_DIR y devuelve su contenido
    ya parseado (lista de diccionarios). Si el archivo no existe o el
    JSON es inválido, devuelve una lista vacía en vez de romper la app.
    """
    ruta = Path(settings.DATA_DIR) / nombre_archivo
    try:
        with open(ruta, encoding="utf-8") as archivo:
            return json.load(archivo)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _filtrar_validos(registros, esquema):
    """
    Devuelve solo los registros que cumplen el esquema mínimo indicado.
    Un registro con una clave faltante o un tipo incorrecto se descarta
    en silencio en vez de romper el procesamiento del resto de la
    colección (así la app sigue funcionando aunque un registro venga
    mal formado).
    """
    validos = []
    for registro in registros:
        try:
            validar_esquema(instance=registro, schema=esquema)
            validos.append(registro)
        except ValidationError:
            continue
    return validos


def obtener_zonas():
    """Devuelve las zonas de zonas.json que cumplen el esquema mínimo."""
    return _filtrar_validos(_leer_json("zonas.json"), ESQUEMA_ZONA)


def obtener_categorias():
    """Devuelve las categorías de categorias.json que cumplen el esquema mínimo."""
    return _filtrar_validos(_leer_json("categorias.json"), ESQUEMA_CATEGORIA)


def obtener_dispositivos():
    """
    Devuelve los dispositivos de dispositivos.json que cumplen el
    esquema mínimo Y cuyo zona_id existe entre las zonas válidas.
    Un dispositivo que referencia una zona inexistente se descarta
    (integridad referencial), sin afectar al resto de la colección.
    """
    dispositivos_validos = _filtrar_validos(_leer_json("dispositivos.json"), ESQUEMA_DISPOSITIVO)
    ids_zonas_validas = {zona["id"] for zona in obtener_zonas()}
    return [d for d in dispositivos_validos if d["zona_id"] in ids_zonas_validas]


def _indexar_por_id(registros):
    """
    Convierte una lista de diccionarios en un diccionario indexado por
    su clave "id". Esto permite buscar una categoría o zona puntual en
    O(1) en vez de recorrer la lista completa cada vez.
    """
    return {registro["id"]: registro for registro in registros}


def obtener_zona_por_id(zona_id):
    """
    Busca una zona por su id. Devuelve el diccionario de la zona o
    None si no existe (para que la vista pueda responder 404).
    """
    zonas_indexadas = _indexar_por_id(obtener_zonas())
    return zonas_indexadas.get(zona_id)


def calcular_estado(consumo_total, limite_kwh):
    """
    Aplica la regla de negocio CA-05:
    ALERTA cuando consumo_total > limite_kwh, NORMAL en caso contrario.
    """
    if consumo_total > limite_kwh:
        return ESTADO_ALERTA
    return ESTADO_NORMAL


def listar_zonas_con_resumen():
    """
    Arma la información que necesita el listado de zonas (CA-01, CA-02):
    para cada zona, cuántos dispositivos tiene asociados.

    No calcula consumo aquí a propósito: el listado solo necesita la
    cantidad de dispositivos, y así evitamos recorrer dos veces la
    colección completa de dispositivos si no hace falta.
    """
    zonas = obtener_zonas()
    dispositivos = obtener_dispositivos()

    resumen = []
    for zona in zonas:
        cantidad_dispositivos = sum(
            1 for dispositivo in dispositivos if dispositivo.get("zona_id") == zona["id"]
        )
        resumen.append({
            "id": zona["id"],
            "nombre": zona["nombre"],
            "limite_kwh": zona["limite_kwh"],
            "cantidad_dispositivos": cantidad_dispositivos,
        })
    return resumen


def obtener_detalle_zona(zona_id):
    """
    Arma toda la información que necesita el detalle de una zona
    (CA-03, CA-04, CA-05, CA-07): sus dispositivos (con el nombre de
    categoría ya resuelto), el consumo total y el estado.

    Devuelve None si la zona no existe, para que la vista pueda
    responder con un 404 controlado (CA-08).
    """
    zona = obtener_zona_por_id(zona_id)
    if zona is None:
        return None

    categorias_indexadas = _indexar_por_id(obtener_categorias())
    dispositivos_zona = [
        dispositivo for dispositivo in obtener_dispositivos()
        if dispositivo.get("zona_id") == zona_id
    ]

    dispositivos_con_categoria = []
    for dispositivo in dispositivos_zona:
        categoria = categorias_indexadas.get(dispositivo.get("categoria_id"))
        dispositivos_con_categoria.append({
            "id": dispositivo["id"],
            "nombre": dispositivo["nombre"],
            "consumo_kwh": dispositivo["consumo_kwh"],
            "categoria_nombre": categoria["nombre"] if categoria else "Sin categoría",
        })

    consumo_total = sum(d["consumo_kwh"] for d in dispositivos_con_categoria)
    estado = calcular_estado(consumo_total, zona["limite_kwh"])

    return {
        "zona": zona,
        "dispositivos": dispositivos_con_categoria,
        "cantidad_dispositivos": len(dispositivos_con_categoria),
        "consumo_total": consumo_total,
        "estado": estado,
    }


def resumen_por_zona():
    """
    Arma la agregación completa del Requerimiento 3 ("Resumen de
    consumo por zona"). Para cada zona construye un registro con id,
    nombre, cantidad de dispositivos, consumo total (suma de
    consumo_kwh de sus dispositivos), límite y estado según la regla
    3.3.

    Una zona sin dispositivos asociados igual se incluye en el
    resultado, con cantidad 0, consumo total 0 y estado
    "DENTRO DEL LÍMITE" (0 <= limite_kwh siempre que el límite no sea
    negativo).

    También calcula los tres totales generales para las tarjetas
    superiores de la interfaz: cantidad de zonas, cantidad de
    dispositivos y consumo total de todos los dispositivos.

    Toda la lógica de conteo, suma y clasificación vive acá; la vista
    solo llama a esta función y arma el contexto, y el template solo
    presenta los valores ya calculados (separación MVT del 3.4).
    """
    zonas = obtener_zonas()
    dispositivos = obtener_dispositivos()

    resumen_zonas = []
    for zona in zonas:
        dispositivos_zona = [
            dispositivo for dispositivo in dispositivos
            if dispositivo.get("zona_id") == zona["id"]
        ]
        consumo_total = sum(d["consumo_kwh"] for d in dispositivos_zona)
        limite_kwh = zona["limite_kwh"]
        estado = (
            ESTADO_DENTRO_LIMITE if consumo_total <= limite_kwh
            else ESTADO_LIMITE_SUPERADO
        )
        resumen_zonas.append({
            "id": zona["id"],
            "nombre": zona["nombre"],
            "cantidad_dispositivos": len(dispositivos_zona),
            "consumo_total": consumo_total,
            "limite_kwh": limite_kwh,
            "estado": estado,
        })

    totales = {
        "cantidad_zonas": len(zonas),
        "cantidad_dispositivos": len(dispositivos),
        "consumo_total": sum(d["consumo_kwh"] for d in dispositivos),
    }

    return {
        "zonas": resumen_zonas,
        "totales": totales,
    }
