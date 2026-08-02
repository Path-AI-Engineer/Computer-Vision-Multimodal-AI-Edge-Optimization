# Retired placeholder

The original Project 22 placeholder was superseded by
[`22-document-vision-ocr-extractor`](../22-document-vision-ocr-extractor/README.md).

No implementation or release evidence belongs in this directory. It remains only because
the managed Windows workspace prevented deletion of the tracked placeholder during the
Project 22 migration.

## 🧠 Descripción

Lab técnico para entender los fundamentos de **video understanding**.

Este proyecto continúa el:

```txt
21-object-detection-retail-lab
```

pero cambia el enfoque:

```txt
Antes:
detectar objetos en imágenes individuales

Ahora:
procesar video como una secuencia de frames
```

Este proyecto pertenece al:

```txt
Plan 4 — Computer Vision, Multimodal AI & Edge Optimization
```

y forma parte del conjunto:

```txt
Percepción Visual, Multimodalidad e Inferencia Ligera
```

La idea central es entender que un video no es solo una imagen grande.

Un video es una secuencia temporal de imágenes.

```txt
video = frames + tiempo + movimiento + cambios
```

---

## 🎯 Objetivo

Crear un lab para procesar video, extraer frames, aplicar inferencia por frame y construir una interpretación básica de eventos simples.

El objetivo técnico es aprender:

* Qué es un frame.
* Qué significa FPS.
* Cómo extraer frames.
* Cómo aplicar modelos visuales por frame.
* Cómo agregar resultados en el tiempo.
* Cómo detectar eventos simples.
* Cuáles son las limitaciones de analizar video frame por frame.

---

## 👤 Usuario objetivo

* AI Engineer en formación.
* Estudiante de Computer Vision.
* Persona interesada en video AI.
* Futuro constructor de sistemas de vigilancia inteligente.
* Futuro constructor de visión para robótica.
* Futuro constructor de agentes multimodales.
* Reclutador técnico interesado en percepción visual temporal.

---

## 🧱 Arquitectura esperada

```txt
Video
   ↓
Carga del archivo
   ↓
Extracción de frames
   ↓
Preprocessing
   ↓
Inferencia por frame
   ↓
Agregación temporal
   ↓
Eventos simples
   ↓
Reporte técnico
```

---

## 🔁 Flujo técnico

```txt
video.mp4
   ↓
read video
   ↓
extract frames
   ↓
resize / normalize
   ↓
frame-level model
   ↓
predictions per frame
   ↓
temporal aggregation
   ↓
simple event detection
   ↓
video report
```

---

## 🧩 Módulos

### Módulo 1 — Video Loading

Cargar un archivo de video y entender sus propiedades.

Incluye:

* Formato del video.
* Duración.
* FPS.
* Número total de frames.
* Resolución.
* Lectura frame por frame.

Pregunta central:

```txt
¿Qué información técnica necesito entender antes de procesar un video?
```

---

### Módulo 2 — Frame Extraction

Extraer frames desde un video.

Incluye:

* Lectura secuencial.
* Guardado de frames.
* Muestreo cada N frames.
* Reducción de costo computacional.
* Organización de frames.

Pregunta central:

```txt
¿Cómo convierto un video en imágenes procesables?
```

---

### Módulo 3 — Frame-Level Inference

Aplicar un modelo visual sobre frames individuales.

Incluye:

* Clasificación por frame.
* Detección por frame si aplica.
* Scores.
* Predicciones.
* Visualización de resultados.

Pregunta central:

```txt
¿Qué puede entender el modelo si analiza cada frame por separado?
```

---

### Módulo 4 — Temporal Aggregation

Agregar resultados a través del tiempo.

Incluye:

* Conteo de predicciones.
* Promedio de scores.
* Detección de cambios.
* Frecuencia de eventos.
* Resultados por segmento temporal.

Pregunta central:

```txt
¿Cómo convierto predicciones por frame en una conclusión sobre el video?
```

---

### Módulo 5 — Simple Event Detection

Detectar eventos simples dentro del video.

Incluye:

* Presencia de objeto.
* Aparición/desaparición.
* Cambio de clase dominante.
* Movimiento básico si aplica.
* Señales temporales simples.

Pregunta central:

```txt
¿Qué evento simple puedo detectar usando frames y tiempo?
```

---

### Módulo 6 — Video Limitations Report

Documentar las limitaciones del análisis.

Incluye:

* Analizar frames no es entender acción completa.
* Pérdida de contexto temporal.
* Costo computacional.
* Problemas de FPS.
* Oclusiones.
* Cambios de iluminación.
* Necesidad futura de modelos espacio-temporales.

Pregunta central:

```txt
¿Qué no puede entender bien un sistema que analiza video frame por frame?
```

---

## 🧪 Labs

### tec-labs

* `tec-video-loading-lab`
* `tec-video-frame-extraction-lab`
* `tec-frame-level-inference-lab`
* `tec-temporal-aggregation-lab`
* `tec-simple-video-event-lab`
* `tec-video-limitations-lab`

---

## 📊 Métricas / señales de análisis

Señales posibles:

* Número de frames procesados.
* FPS original.
* FPS procesado.
* Tiempo de procesamiento.
* Predicciones por frame.
* Frecuencia de eventos.
* Frames con detección positiva.
* Cambios por segmento temporal.
* Latencia aproximada.
* Calidad visual de frames anotados.

Importante:

```txt
Procesar frames no significa entender completamente una acción.
El tiempo agrega significado.
```

---

## 📌 Próximos pasos

* Elegir un video corto.
* Revisar duración, FPS y resolución.
* Extraer frames.
* Guardar muestra de frames.
* Aplicar preprocessing.
* Usar un modelo visual por frame.
* Guardar predicciones.
* Agregar resultados temporalmente.
* Detectar un evento simple.
* Crear reporte del video.
* Documentar limitaciones.
* Grabar demo o explicación corta.
* Actualizar LinkedIn y CV.

---

## ✅ Entregable final

Al terminar este proyecto debe existir:

* Video de prueba.
* Frames extraídos.
* Pipeline de procesamiento.
* Inferencia por frame.
* Resultados agregados.
* Evento simple detectado.
* Frames o clip anotado si aplica.
* README técnico.
* Labs documentados.
* Reporte de limitaciones.

---

## 🧭 Regla final

```txt
Un video no es una imagen.
Es una secuencia visual en el tiempo.

Si ignoro el tiempo, pierdo parte del significado.
```

Este proyecto no busca dominar video AI avanzado.

Busca construir la primera base para entender cómo se procesa video en sistemas de visión.
