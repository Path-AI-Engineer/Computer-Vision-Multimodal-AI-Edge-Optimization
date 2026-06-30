# 21-object-detection-retail-lab

## 🧠 Descripción

Lab aplicado para entender **detección de objetos** en imágenes de retail.

Este proyecto continúa el:

```txt id="1dvh8d"
20-visual-search-embeddings-api
```

pero cambia el enfoque:

```txt id="99gjpq"
Antes:
buscar imágenes similares

Ahora:
detectar qué objetos hay dentro de una imagen y dónde están
```

Este proyecto pertenece al:

```txt id="b9a0j4"
Plan 4 — Computer Vision, Multimodal AI & Edge Optimization
```

y forma parte del conjunto:

```txt id="ekf3u3"
Percepción Visual, Multimodalidad e Inferencia Ligera
```

La idea central es pasar de clasificación visual a localización visual.

Una clasificación responde:

```txt id="b3hu0y"
¿Qué hay en la imagen?
```

Object Detection responde:

```txt id="2mf8eu"
¿Qué hay en la imagen y dónde está?
```

---

## 🎯 Objetivo

Construir un lab aplicado de detección de objetos usando imágenes de retail o una muestra visual anotada.

El objetivo técnico es aprender:

* Bounding boxes.
* Clases de objetos.
* Anotaciones.
* Inferencia con detector preentrenado.
* Fine-tuning conceptual.
* IoU.
* mAP conceptual.
* Confidence score.
* Visualización de detecciones.
* Error analysis en detección.

---

## 👤 Usuario objetivo

* AI Engineer en formación.
* Estudiante de Computer Vision.
* Equipo retail.
* Equipo de inventario visual.
* Sistema de cámaras inteligentes.
* Futuro constructor de visión para robótica.
* Reclutador técnico interesado en detección visual.

---

## 🧱 Arquitectura esperada

```txt id="wol6ro"
Imágenes
   ↓
Anotaciones
   ↓
Bounding boxes
   ↓
Dataset de detección
   ↓
Detector preentrenado
   ↓
Inferencia / fine-tuning conceptual
   ↓
Visualización de detecciones
   ↓
Evaluación
   ↓
Reporte técnico
```

---

## 🔁 Flujo técnico

```txt id="hfp8yq"
data/images
   ↓
annotations
   ↓
class labels
   ↓
bounding boxes
   ↓
detection model
   ↓
predicted boxes
   ↓
confidence scores
   ↓
IoU / mAP concept
   ↓
visual report
```

---

## 🧩 Módulos

### Módulo 1 — Detection Dataset Format

Entender cómo se organiza un dataset de detección.

Incluye:

* Imágenes.
* Clases.
* Bounding boxes.
* Archivos de anotación.
* Formatos tipo YOLO o COCO.
* Relación imagen-anotación.

Pregunta central:

```txt id="nxwees"
¿Cómo se representa un objeto dentro de una imagen para entrenar o evaluar un detector?
```

---

### Módulo 2 — Bounding Box Annotation

Crear o revisar anotaciones con bounding boxes.

Incluye:

* Coordenadas.
* Caja delimitadora.
* Clase del objeto.
* Calidad de anotación.
* Errores de labeling.
* Visualización de cajas.

Pregunta central:

```txt id="e97ecv"
¿Qué tan precisa debe ser una caja para que el modelo aprenda bien?
```

---

### Módulo 3 — Pretrained Detector Inference

Usar un detector preentrenado para inferencia.

Incluye:

* YOLO conceptual.
* Faster R-CNN conceptual.
* Modelo preentrenado.
* Predicted boxes.
* Confidence scores.
* Visualización sobre imagen.

Pregunta central:

```txt id="kkkscz"
¿Qué puede detectar un modelo ya entrenado antes de adaptarlo a mi caso?
```

---

### Módulo 4 — Fine-Tuning Concept

Entender cómo se adapta un detector a nuevas clases.

Incluye:

* Dataset anotado.
* Clases personalizadas.
* Transfer learning en detection.
* Ajuste del detector.
* Limitaciones por tamaño de dataset.
* Costo de anotación.

Pregunta central:

```txt id="az17s5"
¿Qué necesito para adaptar un detector a productos o clases propias?
```

---

### Módulo 5 — Detection Metrics

Entender las métricas básicas de detección.

Incluye:

* IoU.
* Confidence threshold.
* True positives.
* False positives.
* False negatives.
* mAP conceptual.
* Precision/Recall en detección.

Pregunta central:

```txt id="wncuib"
¿Cómo evalúo si el modelo detectó bien el objeto y no solo acertó la clase?
```

---

### Módulo 6 — Detection Error Analysis

Analizar errores de detección.

Incluye:

* Objetos no detectados.
* Cajas mal ubicadas.
* Confianza baja.
* Clases confundidas.
* Detecciones duplicadas.
* Problemas por iluminación, oclusión o tamaño.

Pregunta central:

```txt id="g13kvg"
¿Qué tipo de errores visuales comete el detector?
```

---

### Módulo 7 — Retail Detection Report

Traducir resultados a un reporte aplicado.

Incluye:

* Objetos detectados.
* Conteo visual si aplica.
* Casos correctos.
* Casos fallidos.
* Limitaciones del dataset.
* Usos posibles en retail.

Pregunta central:

```txt id="qs2e7a"
¿Cómo convierto detecciones visuales en información útil para retail?
```

---

## 🧪 Labs

### tec-labs

* `tec-bounding-box-foundations-lab`
* `tec-object-detection-dataset-lab`
* `tec-yolo-inference-lab`
* `tec-iou-map-concept-lab`
* `tec-detection-error-analysis-lab`
* `tec-retail-detection-report-lab`

---

## 📊 Métricas / señales de análisis

Métricas y señales posibles:

* IoU.
* mAP conceptual.
* Precision.
* Recall.
* Confidence score.
* Número de objetos detectados.
* Objetos no detectados.
* Falsos positivos.
* Falsos negativos.
* Errores de localización.
* Errores de clasificación.
* Calidad de anotaciones.

Importante:

```txt id="29yu1n"
En object detection no basta con saber qué objeto hay.
También importa dónde está y con qué confianza fue detectado.
```

---

## 📌 Próximos pasos

* Elegir dataset o muestra de imágenes retail.
* Revisar clases.
* Revisar o crear anotaciones.
* Visualizar bounding boxes.
* Probar detector preentrenado.
* Ejecutar inferencia.
* Guardar imágenes con detecciones.
* Revisar confidence scores.
* Entender IoU.
* Estudiar mAP conceptualmente.
* Analizar errores.
* Documentar limitaciones.
* Escribir reporte retail.
* Grabar demo o explicación corta.
* Actualizar LinkedIn y CV.

---

## ✅ Entregable final

Al terminar este proyecto debe existir:

* Dataset o muestra visual preparada.
* Anotaciones revisadas o creadas.
* Bounding boxes visualizadas.
* Detector preentrenado probado.
* Imágenes con detecciones.
* Scores de confianza.
* Explicación de IoU y mAP.
* Análisis de errores.
* Reporte aplicado a retail.
* README técnico.
* Labs documentados.
* Conclusión sobre límites del detector.

---

## 🧭 Regla final

```txt id="lj31s3"
Clasificar una imagen dice qué hay.
Detectar objetos dice qué hay y dónde está.

En visión real, localizar importa tanto como reconocer.
```

Este proyecto no busca crear un detector industrial completo.

Busca entender la base práctica de object detection y su valor en sistemas visuales reales.
