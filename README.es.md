# Análisis de sentimiento en reseñas — WeLoveReviews

Harbor House Café, 500 reseñas de servicio. La pregunta es si el sentimiento del texto acompaña una media de **4.5 / 5**.

`src/explore.ipynb` es el análisis, en español y con salidas ejecutadas. `src/app.py` es la ruta de producción: el modelo se carga una vez y el script escribe el CSV.

## Resultado

La misma regla en las dos filas: 1–2 negativo, 3 neutral, 4–5 positivo. La media humana de este archivo es el 4.5 anunciado.

| Fuente | Positivo (4–5) | Neutral (3) | Negativo (1–2) | Media de estrellas |
| --- | --- | --- | --- | --- |
| Rating humano | 86.4% | 7.6% | 6.0% | 4.500 |
| Texto nlptown | 82.4% | 8.2% | 9.4% | 4.398 |
| Brecha (modelo − rating) | −4.0 pp | +0.6 pp | +3.4 pp | −0.102 |

El texto sostiene el 4.5. Hay 16 falsos negativos estrictos (humano 4–5, modelo 1–2). Los ejemplos, el patrón de frases y la lectura de 18 reseñas están en las conclusiones del notebook.

## Cómo ejecutarlo

Comprobado con Python 3.12. `torch` es la rueda de CPU.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/app.py
pytest
```

`python src/app.py` lee `data/raw/reviews.csv` y escribe `data/processed/reviews_with_sentiment.csv`. La primera ejecución descarga el modelo. Los pesos no van en git.

Para volver a ejecutar el notebook, desde la raíz del repositorio:

```bash
python -m nbconvert --to notebook --execute --inplace src/explore.ipynb
```

## Estructura

| Ruta | Para qué |
| --- | --- |
| `data/raw/reviews.csv` | 500 reseñas oficiales |
| `data/processed/reviews_with_sentiment.csv` | Estrellas, banda, score y falso negativo |
| `src/explore.ipynb` | Del objetivo a las conclusiones |
| `src/app.py` | Inferencia de producción |
| `src/utils.py` | Ayudante de base de datos de la plantilla. Este análisis no lo llama |
| `tests/test_app.py` | Bandas, carga única, contrato del CSV y un smoke test con el modelo real |
| `PROVENANCE.md` | Commit de la plantilla y hash del dataset |

## Modelo

- `nlptown/bert-base-multilingual-uncased-sentiment`
- Revisión `8f6f4e3a8f70be4b65d3a4a8762b6d781cda240d`
- Una carga con `pipeline("sentiment-analysis", revision=...)`
- Bandas: 1–2 Negative, 3 Neutral, 4–5 Positive

El modelo se afinó con reseñas de productos. Estas filas son de servicio. Ese desajuste se analiza en el notebook; no se cambia el modelo.

## Procedencia

Copia de [machine-learning-python-template](https://github.com/4GeeksAcademy/machine-learning-python-template) en el commit `b49eff6673b76ba5b0003103e32f62a2eb9904a4`. Ese commit no trae archivo `LICENSE`, y aquí no se inventa uno. El sha256 del dataset y la revisión del modelo están en `PROVENANCE.md`.

Este proyecto no tiene interfaz de usuario.
