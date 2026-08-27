# ANALISIS.md · EcoEnergy Fase 1

## 1. Relaciones y multiplicidades

Según el modelo UML entregado (Figura 1 del enunciado):

- **Zona (1) — (0..\*) Dispositivo**: una zona puede tener cero o muchos
  dispositivos; cada dispositivo pertenece exactamente a una zona.
- **Categoria (1) — (0..\*) Dispositivo**: una categoría puede clasificar
  cero o muchos dispositivos; cada dispositivo pertenece exactamente a
  una categoría.

Estas relaciones no se implementan con claves foráneas de base de datos:
se resuelven en Python comparando campos id entre las tres colecciones
cargadas desde los JSON.

## 2. Claves de conexión

| Archivo             | Clave primaria | Claves de conexión hacia otros archivos          |
|----------------------|----------------|---------------------------------------------------|
| `zonas.json`          | `id`           | —                                                   |
| `categorias.json`     | `id`           | —                                                   |
| `dispositivos.json`   | `id`           | `zona_id` → `zonas.json[].id`; `categoria_id` → `categorias.json[].id` |

Un `dispositivo` cuyo `zona_id` o `categoria_id` no corresponde a ningún
registro existente se considera inválido y se descarta (ver sección 3).

## 3. Estrategia de carga y validación

Todo el acceso a datos vive en `zonas/data_access.py`:

1. `_leer_json()` abre el archivo correspondiente en `data/` y lo parsea.
   Si el archivo no existe o el JSON es sintácticamente inválido, se
   devuelve una lista vacía (no se detiene la aplicación).
2. `_filtrar_validos()` usa `jsonschema` para descartar cualquier
   registro al que le falte una clave obligatoria o tenga un tipo de
   dato incorrecto (por ejemplo, `consumo_kwh` como texto).
3. `obtener_dispositivos()` además descarta los dispositivos cuyo
   `zona_id` no exista entre las zonas válidas (integridad referencial).
4. `listar_zonas_con_resumen()` calcula, para el listado, la cantidad de
   dispositivos por zona.
5. `obtener_detalle_zona()` resuelve, para una zona puntual, sus
   dispositivos con el nombre de categoría ya resuelto, el consumo total
   (suma de `consumo_kwh`) y el estado (`calcular_estado()`).

## 4. Regla de estado (CA-05)

```
estado = ALERTA   si consumo_total > limite_kwh
estado = NORMAL   si consumo_total <= limite_kwh
```

## 5. Matriz Criterio de aceptación | Archivo/Componente | Prueba

| Criterio | Archivo/Componente | Prueba realizada |
|----------|--------------------|--------------------|
| CA-01 | `zonas/views.py::listado_zonas`, `templates/zonas/listado_zonas.html` | Cargar `/zonas/` y verificar que aparecen las 4 zonas de `zonas.json`. |
| CA-02 | `data_access.py::listar_zonas_con_resumen` | Verificar en el listado que cada tarjeta muestra nombre, límite y cantidad de dispositivos correctos. |
| CA-03 | `data_access.py::obtener_detalle_zona`, `templates/zonas/detalle_zona.html` | Entrar a `/zonas/1/` y verificar tabla de dispositivos con categoría y consumo. |
| CA-04 | `data_access.py` (todo el módulo) | Revisar que ningún número (cantidad, consumo, estado) está escrito en el HTML; todos vienen del contexto de la vista. |
| CA-05 | `data_access.py::calcular_estado` | Comparar zona 1 (450/500 → NORMAL) contra zona 2 (380/300 → ALERTA). |
| CA-06 | `data_access.py` (lectura en cada request) | Agregar dispositivos válidos a `dispositivos.json` en caliente y confirmar que aparecen al recargar, sin tocar código. |
| CA-07 | `zonas/views.py::detalle_zona`, template detalle | Entrar a `/zonas/4/` (sin dispositivos) y verificar el mensaje "Esta zona no tiene dispositivos". |
| CA-08 | `zonas/views.py::detalle_zona` (rama `detalle is None`) | Entrar a `/zonas/999/` y confirmar status 404 con página propia, sin traza técnica. |
| CA-09 | `templates/base.html` | Aumentar zonas/dispositivos en los JSON y confirmar que header, nav y footer se mantienen. |
| CA-10 | `templates/zonas/detalle_zona.html` (clase `tabla-scroll`) | Duplicar dispositivos de una zona y verificar que la tabla scrollea sin desbordar la página. |
| CA-11 | `templates/base.html`, todos los templates de `zonas/` | Revisión visual: header, nav, tarjetas, tabla y botones comparten estilo Bootstrap consistente. |
| CA-12 | `templates/zonas/detalle_zona.html` (badge de estado) | Confirmar que el estado muestra texto ("NORMAL"/"ALERTA") + ícono, no solo color. |
| CA-13 | Proyecto completo | Ejecutar `python manage.py check` sin errores. |
