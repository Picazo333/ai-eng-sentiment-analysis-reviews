# Checkpoint de auditoría — actividad 50 de la plataforma

**Para:** Auditor — Rodrigo Salcedo (independiente; nunca es el autor de este trabajo).
**Fecha de este checkpoint:** 13 nov 2026, 11:15 (hora de CDMX).
**Regla de veredicto:** si el trabajo **pasa la rúbrica oficial**, se da por bueno aunque haya hallazgos menores o irrelevantes. Solo un hallazgo **GRAVE** bloquea. GRAVE = rompe un criterio de la rúbrica o la seguridad (secretos, auth, inyección, pérdida de datos). MENOR se reporta y no bloquea. IRRELEVANTE se anota y no retrasa.

## Actividad

| Campo | Valor |
|---|---|
| Número de la plataforma | 50 |
| Título | Sentiment Analysis on Customer Reviews — WeLoveReviews |
| Slug | `ai-eng-sentiment-analysis-reviews` |
| Tarea LMS | 1022023 |
| Enlace LMS | https://learn.4geeks.com/main-cohort/latam-aie-pt-6/syllabus/latam-models-training-rag/project/ai-eng-sentiment-analysis-reviews?moduleId=1 |
| Repositorio | `Picazo333/ai-eng-sentiment-analysis-reviews` (independiente) |
| PR | https://github.com/Picazo333/ai-eng-sentiment-analysis-reviews/pull/1 |
| Rama | `cursor/sentiment-reviews-032-0a05` |
| Head auditado (esta pasada) | `c888a34015a000a4c09e5141ea97dad52bab24d9` |
| Estado LMS (13 nov 2026, API viva, GET) | PENDING / PENDING, `github_url` vacío (tarea 1022023) |

## Rúbrica de referencia

Enunciado oficial: `/workspace/ejecucion/032-ai-eng-sentiment-analysis-reviews/source/OFFICIAL_README.md` @ syllabus `fd2da034`, L105–L115. Primera pasada.

El auditor no usa como única fuente la autoevaluación del autor. Contrasta con el enunciado oficial. No reescribe el código, no hace merge, no envía al LMS y un autor nunca audita su propio trabajo.


## Qué intentar romper (de todas las formas razonables)

1. **Tests:** correr las suites documentadas en un entorno limpio. Registrar comando, salida y fallos. Distinguir fallos nuevos de los heredados de la base (por ejemplo `tests/api` / `rag-tests`).
2. **Entradas inválidas:** vacíos, tipos incorrectos, tamaños extremos, Unicode, IDs inexistentes, tokens caducados o reutilizados, dobles envíos.
3. **Seguridad:** authz (datos de otro usuario), inyección, CSRF donde aplique, límites de tasa. **Nunca imprimas, copies ni subas secretos reales.**
4. **Secretos:** buscar claves, tokens, contraseñas o URIs con password en el árbol, en la evidencia y en el historial del PR. Un secreto en el repo es GRAVE.
5. **UI** (si hay interfaz): responsiva (aprox. 390 / 768 / 1280), teclado, foco, contraste, textos alternativos, estados de error y vacío. Si declara SIGNAL, comprobar tokens; no imponer SIGNAL contra la rúbrica.
6. **Rendimiento** (si la rúbrica lo pide): mediciones en producción (build + start), nunca en modo dev.
7. **Reproducibilidad desde cero:** seguir el README de un clone limpio. Lo que la rúbrica deja en HITL humano no se convierte en FAIL.
8. **Cumplimiento literal del enunciado** y de las prohibiciones (no usar IA, no copiar la solución oficial, etc.), con evidencia.
9. **Integridad:** no fabricar evidencia, no contar mocks como integración real, no inflar PASS, no inventar autoría.

## Tabla de hallazgos (a llenar por el auditor)

| ID | Severidad (GRAVE / MENOR / IRRELEVANTE) | Dónde (archivo, línea, SHA, comando) | Qué se observó | Criterio de rúbrica afectado | ¿Bloquea? |
|---|---|---|---|---|---|
| H1 | IRRELEVANTE | `tests/test_app.py`; `src/app.py`. El auditor no instaló `transformers`/`torch` en esta caja. | La suite (11 casos; la mayoría con pipeline falso) no se relanzó aquí. El CSV de 500 reseñas, el cuaderno ejecutado (13/13 celdas de código con salida) y la revisión clavada `8f6f4e3a8f70be4b65d3a4a8762b6d781cda240d` sí están en el árbol. No es un defecto del trabajo. | No rompe L105–L115. | No |

No hay hallazgos GRAVE. GRAVE 0, MENOR 0, IRRELEVANTE 1.

HITL abiertos, no bloquean: envío al LMS (tarea 1022023, PENDING); merge. No son GRAVE.

## Veredicto

- **READY** — pasa la rúbrica oficial. Los MENOR e IRRELEVANTE no lo impiden.
- **NO READY** — hay al menos un GRAVE, o un criterio obligatorio en FAIL / UNVERIFIED que no sea HITL explícito de Miguel.
- Los HITL de Miguel (merge, envío al LMS, VPS, key de LLM, prueba en dispositivo, video) no restan del porcentaje de la rúbrica y no los cierra el auditor.

## Veredicto del auditor (13 nov 2026)

- **READY / PASA. Primera pasada. Criterios oficiales cubiertos con artefactos y código. 0 GRAVE.**
- Conteos: GRAVE 0, MENOR 0, IRRELEVANTE 1.
- Informe: `AUDIT_REPORT_50_ai-eng-sentiment-analysis-reviews.md (solo local / academic; no se publica en el repo independiente)`.

## Dónde dejar el reporte

1. En esta misma rama, en el `AUDIT_CHECKPOINT.md` de la raíz (único fichero de auditoría que se publica en repos independientes). No se publica el informe aparte en la raíz.
2. Una copia en `/workspace/intake/zip_1112/runtime-private/academic/050_ADVERSARIAL_AUDIT_2026-11-13.md` (sin pisar recibos `*_INDEPENDENT_REVIEW.md`).
3. Avisa al Orquestador. No comentes en el LMS ni pidas tú más datos a los profesores.

## Estado portable de la cohorte

Las 83 actividades, en el orden de la plataforma, están en `Picazo333/4geeks-control-tower`, carpeta `estado/`, rama `estado-cohorte-2026-11-13`, PR https://github.com/Picazo333/4geeks-control-tower/pull/32 (sin merge). En esta caja: `/workspace/ESTADO/`.
