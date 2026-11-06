# Procedencia del código base

Este repositorio parte de la plantilla oficial de 4Geeks Academy y del dataset oficial del enunciado. No se copió una solución de otro repositorio.

## Plantilla

- Repositorio: https://github.com/4GeeksAcademy/machine-learning-python-template
- Commit: `b49eff6673b76ba5b0003103e32f62a2eb9904a4`
- Mensaje: Update Dockerfile
- Fecha: 2026-07-23 20:25:05 -0400
- Campo `author` de ese commit: Ehiber Graterol `<56272634+ehiber@users.noreply.github.com>`
- Licencia: ese commit no incluye archivo `LICENSE`. La API pública de GitHub devuelve `license: null` para el repositorio. Este proyecto no añade una licencia inventada.
- Copia local tomada el 2026-11-06 desde `main` de esa URL.

Archivos conservados de esa revisión, sin reescribir su lógica:

- `.devcontainer/` (`devcontainer.json`, `docker-compose.yml`, `Dockerfile`)
- `.env.example`
- `.vscode/settings.json`
- `data/raw/.gitkeep`, `data/interim/.gitkeep`, `data/processed/.gitkeep`
- `models/.gitkeep`
- `preview.jpg` (imagen de la plantilla, no de este análisis)
- `src/utils.py` (conexión opcional a base de datos; este análisis no la llama)

`src/app.py` y `src/explore.ipynb` ocupan el lugar del esqueleto de la plantilla. `README.md`, `README.es.md` y `requirements.txt` se adaptan al enunciado y dejan de ser el texto genérico de la plantilla. El `learn.json` de la plantilla describe la plantilla; el de este proyecto es el `learn.json` del enunciado en el syllabus (ver abajo).

La plantilla fijaba dependencias con rangos (`pandas>=2.3.3`, `scikit-learn` sin versión, etc.) e incluía paquetes que esta entrega no ejecuta (OpenCV, XGBoost, drivers SQL, mapas). `requirements.txt` queda reducido a las librerías que el código importa, con versión exacta verificada en el entorno que generó el CSV.

## Dataset

- Repositorio: https://github.com/4GeeksAcademy/ai-engineering-syllabus
- Commit: `fd2da034894ba93ba738559280ccde074ab1d953`
- Ruta: `content/projects/existing-model-sentiment-analysis-reviews/reviews.csv`
- Destino: `data/raw/reviews.csv`
- sha256: `63439a1a8c48fe8cc479b0b621b151b8da2415c58522b1e6b111582eef6edf10`

El `learn.json` del proyecto corresponde al mismo commit del syllabus, ruta `content/projects/existing-model-sentiment-analysis-reviews/learn.json`, sha256 `aea38b7c2ce6b575e92277e0ec465102ee6759fac98b054ec06ef383a9085c84`.

## Modelo

- Identificador: `nlptown/bert-base-multilingual-uncased-sentiment`
- Revisión fijada: `8f6f4e3a8f70be4b65d3a4a8762b6d781cda240d`
- Consulta: API pública del Hugging Face Hub el 2026-11-06 (`private: false`, `gated: false`)
- Los pesos no se suben al repositorio. `.gitignore` excluye `*.safetensors`, `*.bin`, `*.h5`, `*.msgpack` y cachés. La descarga ocurre al ejecutar `src/app.py`.
