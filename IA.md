# IA.md · Registro de uso de Inteligencia Artificial

## Herramienta utilizada

Claude (Anthropic), a través de la interfaz de chat de Claude.ai.

## Prompts principales utilizados

1. Solicitud de lectura y resumen del enunciado de la Evaluación
   Sumativa I · Fase 1 (EcoEnergy) para clarificar alcance y criterios.
2. Solicitud de apoyo para estructurar el proyecto Django (sin Models,
   sin ORM), incluyendo la app `zonas`, el módulo de acceso a datos, las
   vistas, las rutas y los templates Bootstrap según los bocetos del
   enunciado.
3. Solicitud de apoyo para integrar una librería externa (`jsonschema`)
   que validara la estructura de los archivos JSON y descartara
   registros inválidos sin detener la aplicación.
4. Solicitud de pruebas manuales (vía `curl` y modificación temporal de
   los JSON) para verificar los distintos escenarios exigidos: estado
   NORMAL/ALERTA, zona sin dispositivos, id inexistente (404) y
   comportamiento dinámico ante nuevos registros o registros corruptos.

## Partes utilizadas de la respuesta de la IA

- Estructura general del proyecto Django (`ecoenergy_project/`, app
  `zonas/`).
- Módulo `zonas/data_access.py`: carga de JSON, validación con
  `jsonschema`, cruce de relaciones (zona–dispositivo–categoría),
  cálculo de consumo total y estado.
- `zonas/views.py` y `zonas/urls.py`.
- Templates Bootstrap (`base.html`, `listado_zonas.html`,
  `detalle_zona.html`, `zona_no_encontrada.html`).
- `requirements.txt` y `.gitignore`.

## Cambios propios / adaptaciones

> **A completar por la estudiante antes de la entrega.** Se recomienda
> revisar cada función de `data_access.py` y `views.py`, ajustar nombres,
> comentarios o estructura al propio estilo, y registrar aquí cualquier
> modificación realizada (por ejemplo: renombrar variables, cambiar el
> criterio de un mensaje, ajustar estilos CSS propios, agregar
> validaciones adicionales, etc.), de modo que el código entregado sea
> plenamente explicable en la revisión oral/presencial.

## Verificación y pruebas realizadas

- `python manage.py check` sin errores.
- Pruebas manuales de las rutas `/zonas/` y `/zonas/<id>/` cubriendo:
  listado completo, zona en estado NORMAL, zona en estado ALERTA, zona
  sin dispositivos, id inexistente (404 controlado), incorporación de
  registros nuevos sin cambios de código, y descarte de registros
  corruptos o con referencias inexistentes (detalladas en `README.md`).

## Nota sobre el alcance permitido de uso de IA

El enunciado autoriza el uso de IA principalmente para apoyar análisis,
HTML, Bootstrap y revisión de código. Dado que en este caso también se
usó IA para plantear la lógica de `data_access.py` y las vistas, se deja
constancia expresa de ello en este documento, y se recomienda que la
estudiante repase e internalice esa lógica a fondo antes de la entrega,
de modo de poder explicar cualquier parte del código durante la
evaluación.
