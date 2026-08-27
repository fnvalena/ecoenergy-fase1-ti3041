# EcoEnergy · Fase 1 (Django, sin ORM)

Aplicación de monitoreo energético para PyMEs. Permite consultar zonas de
consumo y el detalle de los dispositivos instalados en cada una, usando
archivos JSON como fuente de datos (sin Models, sin ORM, sin base de datos).

## Requisitos

- Python 3.10 o superior
- pip

## Instalación

```bash
# 1. Clonar el repositorio
git clone <URL_DEL_REPOSITORIO>
cd <NOMBRE_DEL_REPOSITORIO>

# 2. Crear y activar un entorno virtual
python3 -m venv .venv
source .venv/bin/activate        # En Windows: .venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt
```

## Ejecución

```bash
python manage.py check      # Verifica que el proyecto esté sano
python manage.py runserver
```

Luego abrir en el navegador: <http://127.0.0.1:8000/>

## Rutas funcionales

| Ruta                  | Descripción                                                   |
|-----------------------|----------------------------------------------------------------|
| `/`                   | Redirige al listado de zonas.                                 |
| `/zonas/`             | Listado de todas las zonas (nombre, límite, N° dispositivos). |
| `/zonas/<id>/`        | Detalle de una zona: dispositivos, categoría, consumo total y estado (NORMAL/ALERTA). Si `<id>` no existe, responde con una página 404 propia (status 404). |

## Datos de origen

Los archivos JSON viven en `data/`:

- `data/zonas.json`
- `data/categorias.json`
- `data/dispositivos.json`

Toda la lectura y el cruce de estos archivos se resuelve en Python puro
dentro de `zonas/data_access.py` (sin ORM). El módulo también valida cada
registro con la librería `jsonschema`: un registro con una clave faltante,
un tipo incorrecto o una referencia (`zona_id`/`categoria_id`) inexistente
se descarta sin detener la aplicación.

## Pruebas realizadas manualmente

Con el servidor corriendo (`python manage.py runserver`):

1. **Listado**: entrar a `/zonas/` y confirmar que aparecen las 4 zonas de
   `zonas.json` con su límite y cantidad de dispositivos.
2. **Detalle NORMAL**: entrar a `/zonas/1/` (Bodega Norte, 450/500 kWh) y
   confirmar el badge verde "NORMAL".
3. **Detalle ALERTA**: entrar a `/zonas/2/` (Oficinas, 380/300 kWh) y
   confirmar el badge rojo "ALERTA".
4. **Zona sin dispositivos**: entrar a `/zonas/4/` (Sala de Servidores) y
   confirmar el mensaje "Esta zona no tiene dispositivos".
5. **Zona inexistente**: entrar a `/zonas/999/` y confirmar página 404
   propia, sin traza técnica.
6. **Nuevos registros en caliente**: con el servidor corriendo, agregar un
   par de dispositivos nuevos a `data/dispositivos.json` (respetando el
   esquema) y recargar `/zonas/<id>/`: las cantidades y el consumo se
   actualizan solos, sin tocar código.
7. **Registro corrupto**: agregar a `data/dispositivos.json` un registro
   con `consumo_kwh` como texto o con un `zona_id` inexistente: el
   registro se descarta automáticamente y el resto de la zona sigue
   mostrándose correctamente (no se cae la app).

## Estructura del proyecto

```
ecoenergy_project/   Configuración global de Django (settings, urls)
zonas/                App principal
├── data_access.py    Carga, validación y cruce de los JSON (sin ORM)
├── views.py           Listado y detalle de zonas
└── urls.py            Rutas /zonas/ y /zonas/<id>/
templates/
├── base.html                     Layout común (header, nav, footer, Bootstrap)
└── zonas/
    ├── listado_zonas.html
    ├── detalle_zona.html
    └── zona_no_encontrada.html   404 controlado
data/                 zonas.json, categorias.json, dispositivos.json
```
