# AI Engineer Roadmap — Plan 4

## 🧠 Computer Vision, Multimodal AI & Edge Optimization

Esta organización reúne los proyectos del **Plan 4 — Computer Vision, Multimodal AI & Edge Optimization**.

Este plan pertenece a la ruta mayor:

```txt id="dw2sp7"
Path-AI-Engineer-2.0
```

El objetivo de este cuarto plan es entrar con más fuerza al mundo de la **percepción visual**, modelos de visión, datos multimodales e inferencia optimizada.

Este plan continúa la base construida en:

```txt id="2ukkz9"
Plan 1 — Machine Learning Engineering & Software Foundations
Plan 2 — Deep Learning Core
Plan 3 — Advanced ML Backgrounds
```

Ahora el enfoque cambia hacia sistemas capaces de trabajar con:

```txt id="b9fjfg"
imágenes
→ video
→ objetos
→ embeddings visuales
→ búsqueda visual
→ modelos multimodales
→ inferencia optimizada
→ edge AI
```

La idea no es solo entrenar modelos de Computer Vision.

La idea es aprender cómo una IA percibe, representa, busca, clasifica y ejecuta modelos visuales de forma eficiente.

---

## 🎯 Objetivo general

Convertirme en un AI Engineer capaz de:

* Construir clasificadores de imágenes más sólidos.
* Usar transfer learning en Computer Vision.
* Entender embeddings visuales.
* Crear sistemas de búsqueda visual.
* Detectar objetos en imágenes.
* Trabajar con video de forma inicial.
* Entender modelos multimodales.
* Conectar texto e imagen.
* Optimizar modelos para inferencia.
* Comprender edge AI.
* Evaluar rendimiento, latencia y precisión.
* Prepararme para robótica, visión multimodal, Vision Transformers y sistemas de percepción avanzada.

---

## 🧭 Filosofía de trabajo

Este plan se trabaja con una regla clara:

```txt id="jnob9e"
Ver no es solo clasificar.
Percibir implica detectar, representar, comparar, localizar y decidir.
```

En este plan sí habrá proyectos aplicados, pero no todos deben convertirse en sistemas grandes.

Regla del plan:

```txt id="tr7n96"
Primero visión sólida.
Luego representación visual.
Después multimodalidad.
Finalmente optimización para inferencia real.
```

El objetivo no es entrenar modelos enormes.

El objetivo es entender el flujo completo de percepción visual desde datos hasta despliegue eficiente.

---

## 🧩 Conceptos base

### Computer Vision

Área de IA enfocada en procesar imágenes o video para extraer información útil.

Puede incluir:

* Clasificación de imágenes.
* Detección de objetos.
* Segmentación.
* OCR.
* Búsqueda visual.
* Análisis de video.
* Percepción para robótica.

---

### Transfer Learning

Técnica donde se reutiliza un modelo preentrenado y se adapta a una tarea nueva.

En Computer Vision es muy importante porque entrenar modelos visuales grandes desde cero suele ser costoso.

Ejemplos:

* ResNet.
* EfficientNet.
* MobileNet.
* Vision Transformer.
* CLIP.

---

### Embeddings visuales

Representaciones vectoriales de imágenes.

Permiten comparar imágenes por similitud.

Ejemplos de uso:

* Búsqueda visual.
* Recomendación visual.
* Duplicados.
* Agrupación de imágenes.
* Recuperación de imágenes similares.

---

### Object Detection

Tarea donde el modelo no solo dice qué hay en una imagen, sino también dónde está.

Ejemplos:

```txt id="cdzy17"
imagen → clase + bounding box
```

Puede usarse en:

* Retail.
* Seguridad.
* Robótica.
* Inventario.
* Vehículos autónomos.
* Sistemas industriales.

---

### Multimodal AI

Área donde el sistema combina más de un tipo de dato.

Ejemplos:

```txt id="yco9x2"
texto + imagen
imagen + audio
video + texto
sensores + visión
```

Este plan introduce multimodalidad desde el lado visual.

---

### Edge Optimization

Optimización de modelos para ejecutarlos en ambientes con recursos limitados.

Ejemplos:

* Dispositivos móviles.
* Cámaras inteligentes.
* Raspberry Pi.
* Robots.
* Dispositivos IoT.
* Sistemas embebidos.

La pregunta central es:

```txt id="5ht73r"
¿Cómo hago que un modelo sea útil no solo en mi laptop, sino en un entorno real?
```

---

## 🧪 Tipos de proyectos en este plan

### Aplicado

Proyecto donde se construye un sistema funcional con visión.

Ejemplos:

* Clasificador visual.
* Detector de objetos.
* Buscador visual.

### Lab avanzado

Proyecto para entender una técnica específica.

Ejemplos:

* Visual embeddings.
* CLIP.
* Model compression.
* Edge inference.

### Integrador ligero

Proyecto que conecta varias piezas sin convertirse todavía en plataforma enorme.

Ejemplos:

* Sistema multimodal simple.
* API visual con inferencia optimizada.

---

## 🗺️ Cronograma Plan 4

| Semana | Proyecto                                | Objetivo                                          |
| ------ | --------------------------------------- | ------------------------------------------------- |
| 73-76  | `19-image-classification-api` | Clasificación fina, calibración, API y Studio visual |
| 77-80  | `20-retail-shelf-object-detection`      | Detección densa, conteo visible, API y consola    |
| 81-85  | `21-segmentation-quality-control-lab`   | Segmentación visual aplicada a control de calidad |
| 86-89  | `22-document-vision-ocr-extractor`      | OCR, extracción estructurada y evidencia espacial |
| 90-94  | `23-multimodal-image-text-assistant`    | Sistema simple imagen + texto                     |
| 95-99  | `24-edge-vision-optimization-lab`       | Optimización de modelos visuales para inferencia  |

Duración total aproximada:

```txt id="ym4f4r"
27 semanas
```

---

# 📁 Proyectos del Plan 4

## 19 — transfer-learning-image-classifier

### Objetivo

Construir un clasificador de imágenes usando transfer learning.

Este proyecto fortalece Computer Vision sin entrenar una CNN grande desde cero.

---

### Flujo

```txt id="4owd1z"
dataset de imágenes
→ preprocessing
→ modelo preentrenado
→ fine-tuning parcial
→ entrenamiento
→ evaluación
→ demo de predicción
```

---

### Aprendizajes principales

* Transfer Learning.
* Fine-tuning.
* Feature extractor.
* Modelos preentrenados.
* ResNet / EfficientNet / MobileNet.
* Data augmentation.
* Overfitting visual.
* Métricas de clasificación.
* Confusion Matrix.
* Predicción sobre imagen nueva.

---

### Módulos

* Image Dataset Preparation.
* Pretrained Model Loading.
* Feature Extractor Mode.
* Fine-Tuning Mode.
* Evaluation and Error Analysis.
* Prediction Demo.

---

### Labs

* `tec-transfer-learning-foundations-lab`
* `tec-pretrained-cnn-lab`
* `tec-feature-extractor-vs-finetuning-lab`
* `tec-visual-classification-error-analysis-lab`
* `tec-image-prediction-demo-lab`

---

### Entregable final

* Dataset preparado.
* Modelo preentrenado adaptado.
* Training loop.
* Métricas.
* Confusion Matrix.
* Demo de predicción.
* README técnico.
* Reporte de errores.

---

## 20 — visual-search-embeddings-api

### Objetivo

Crear un sistema de búsqueda visual usando embeddings de imágenes.

Este proyecto introduce la idea de representar imágenes como vectores comparables.

---

### Flujo

```txt id="9c1rwg"
imágenes
→ modelo extractor
→ embeddings visuales
→ índice vectorial
→ consulta por imagen
→ similitud
→ resultados similares
→ API
```

---

### Aprendizajes principales

* Embeddings visuales.
* Similarity search.
* Cosine similarity.
* Vector index.
* Image retrieval.
* Feature extraction.
* Búsqueda por imagen.
* Ranking visual.
* API de búsqueda.
* Limitaciones de similitud visual.

---

### Módulos

* Visual Embedding Extraction.
* Vector Index Basics.
* Similarity Scoring.
* Image Query Search.
* Ranking and Retrieval.
* Visual Search API.

---

### Labs

* `tec-visual-embeddings-lab`
* `tec-cosine-similarity-visual-lab`
* `tec-vector-index-basics-lab`
* `tec-image-retrieval-lab`
* `tec-visual-search-api-lab`

---

### Entregable final

* Colección de imágenes.
* Embeddings visuales.
* Índice de búsqueda.
* Consulta por imagen.
* Ranking de imágenes similares.
* API funcional.
* README técnico.
* Demo local.

---

## 21 — object-detection-retail-lab

### Objetivo

Construir un lab aplicado de detección de objetos en imágenes de retail.

Este proyecto pasa de clasificar imágenes completas a localizar objetos dentro de la imagen.

---

### Flujo

```txt id="bu4gjr"
imágenes anotadas
→ bounding boxes
→ dataset detection
→ modelo detector
→ entrenamiento / inferencia
→ evaluación
→ visualización de detecciones
```

---

### Aprendizajes principales

* Object Detection.
* Bounding boxes.
* Clases.
* Anotaciones.
* YOLO / Faster R-CNN conceptual.
* mAP conceptual.
* IoU.
* Confidence score.
* Visualización de detecciones.
* Errores de localización.

---

### Módulos

* Detection Dataset Format.
* Bounding Box Annotation.
* Pretrained Detector Inference.
* Fine-Tuning Concept.
* Detection Metrics.
* Retail Detection Report.

---

### Labs

* `tec-bounding-box-foundations-lab`
* `tec-object-detection-dataset-lab`
* `tec-yolo-inference-lab`
* `tec-iou-map-concept-lab`
* `tec-detection-error-analysis-lab`

---

### Entregable final

* Dataset o muestra anotada.
* Detector probado.
* Visualización de bounding boxes.
* Métricas o señales de detección.
* Análisis de errores.
* README técnico.
* Conclusión sobre límites del detector.

---

## 22 — document-vision-ocr-extractor

### Objetivo

Crear un workbench de Document AI que convierta un recibo de una página en texto localizado,
campos normalizados y evidencia auditable.

---

### Flujo

```txt id="d8sp3z"
imagen o PDF de una página
→ validación y preprocessing
→ localización y OCR
→ orden de lectura
→ extracción de campos
→ normalización y revisión
→ JSON o CSV
```

---

### Aprendizajes principales

* OCR con texto, confianza y cajas.
* Orden de lectura y evidencia espacial.
* Extracción de `company`, `date`, `address` y `total`.
* Normalización sin sobrescribir el valor raw.
* Separación entre predicciones y ediciones del operador.
* CER, WER, exact match, review rate y error propagation.
* Límites entre fixtures de cualificación y benchmarks oficiales.

---

### Módulos

* Document Ingestion.
* Image Preprocessing.
* OCR and Reading Order.
* Layout-Aware Field Extraction.
* Evidence Review and Export.
* Qualification Evaluation.

---

### Labs

* `tec-document-preprocessing-lab`
* `tec-ocr-localization-lab`
* `tec-layout-field-extraction-lab`
* `tec-normalization-review-lab`
* `tec-ocr-evaluation-lab`

---

### Entregable final

* API FastAPI y workbench React.
* Recibos de cualificación reproducibles.
* OCR localizado y campos con evidencia.
* Comparación raw vs normalizado y revisión humana.
* Exportación JSON/CSV.
* Evaluación oracle vs end-to-end.
* Docker y preparación para AWS App Runner.

---

## 23 — multimodal-image-text-assistant

### Objetivo

Crear un asistente simple que combine imagen y texto.

Este proyecto introduce multimodalidad desde una versión controlada y pequeña.

---

### Flujo

```txt id="duybuv"
imagen + pregunta
→ análisis visual
→ extracción de descripción
→ prompt textual
→ respuesta
→ reporte de limitaciones
```

---

### Aprendizajes principales

* Multimodal AI.
* Image captioning conceptual.
* CLIP conceptual.
* Image-text alignment.
* Visual question answering conceptual.
* Prompt con contexto visual.
* Limitaciones de interpretación visual.
* Riesgo de alucinación multimodal.
* Diseño de respuesta útil.

---

### Módulos

* Image-to-Text Context.
* CLIP Concept Lab.
* Image-Text Similarity.
* Visual Question Answering Basics.
* Response Generation.
* Multimodal Limitations Report.

---

### Labs

* `tec-clip-concept-lab`
* `tec-image-text-similarity-lab`
* `tec-image-captioning-concept-lab`
* `tec-vqa-basics-lab`
* `tec-multimodal-limitations-lab`

---

### Entregable final

* Sistema simple imagen + texto.
* Análisis visual básico.
* Respuesta textual.
* Documentación de limitaciones.
* README técnico.
* Demo controlada.

---

## 24 — edge-vision-optimization-lab

### Objetivo

Optimizar un modelo visual para inferencia más ligera.

Este proyecto cierra el Plan 4 conectando visión con eficiencia, latencia y despliegue en entornos limitados.

---

### Flujo

```txt id="x6m38a"
modelo visual
→ baseline inference
→ medición de latencia
→ optimización
→ modelo ligero
→ comparación
→ reporte edge
```

---

### Aprendizajes principales

* Edge AI.
* Latency.
* Throughput.
* Model size.
* Quantization conceptual.
* Pruning conceptual.
* ONNX conceptual.
* MobileNet.
* Efficient inference.
* Trade-off precisión vs velocidad.
* Deployment constraints.

---

### Módulos

* Inference Baseline.
* Latency Measurement.
* Model Size Analysis.
* Lightweight Model Comparison.
* Quantization Concept.
* Edge Readiness Report.

---

### Labs

* `tec-inference-latency-lab`
* `tec-model-size-analysis-lab`
* `tec-lightweight-cnn-lab`
* `tec-quantization-concept-lab`
* `tec-onnx-export-concept-lab`
* `tec-edge-readiness-report-lab`

---

### Entregable final

* Modelo visual base.
* Medición de latencia.
* Comparación con modelo ligero.
* Reporte de tamaño del modelo.
* Optimización conceptual.
* README técnico.
* Conclusión sobre trade-offs de edge AI.

---

# 📊 Nivel esperado al terminar Plan 4

| Área                                  | Nivel esperado |
| ------------------------------------- | -------------: |
| Computer Vision aplicado              |           8/10 |
| Transfer Learning                     |         8.5/10 |
| Fine-tuning visual                    |           8/10 |
| Image preprocessing                   |         8.5/10 |
| Visual embeddings                     |           8/10 |
| Similarity search visual              |           8/10 |
| Object Detection                      |         7.5/10 |
| Bounding boxes / IoU / mAP conceptual |         7.5/10 |
| Video understanding básico            |           7/10 |
| Multimodal AI inicial                 |         7.5/10 |
| CLIP conceptual                       |         7.5/10 |
| Image-text alignment                  |           7/10 |
| Edge AI conceptual                    |         7.5/10 |
| Latency / model size analysis         |           8/10 |
| Optimización de inferencia            |         7.5/10 |

---

# 🧠 Resultado esperado del Plan 4

Al completar este plan, podré decir:

```txt id="bcxdkp"
Sé construir sistemas de Computer Vision aplicados.
Sé usar modelos preentrenados para clasificación visual.
Sé extraer embeddings visuales y hacer búsqueda por similitud.
Sé entender detección de objetos y bounding boxes.
Sé procesar video como secuencia de frames.
Sé conectar imagen y texto en un sistema multimodal básico.
Sé medir latencia, tamaño y rendimiento de modelos visuales.
Sé explicar trade-offs entre precisión, velocidad y despliegue.
Sé prepararme para visión avanzada, robótica y modelos multimodales.
```

---

# 🧭 Regla final

```txt id="g6d4ma"
Una IA visual no solo clasifica.
Percibe, representa, compara, localiza y decide.

Un modelo visual no solo debe ser preciso.
También debe ser usable en condiciones reales.
```

---

# 👤 Autor

**Jean Franck Loa Rojas**

AI Engineer Path Builder
Computer Vision • Multimodal AI • Visual Search • Object Detection • Video Understanding • Edge AI • Model Optimization
