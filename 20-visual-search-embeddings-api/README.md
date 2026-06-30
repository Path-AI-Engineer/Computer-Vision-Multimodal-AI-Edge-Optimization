# 20-visual-search-embeddings-api

## 🧠 Descripción

Sistema de búsqueda visual usando **embeddings de imágenes** y una API.

Este proyecto continúa el:

```txt id="aosp4f"
19-transfer-learning-image-classifier
```

pero cambia el enfoque:

```txt id="3jymz9"
Antes:
clasificar una imagen en una categoría

Ahora:
representar imágenes como vectores y buscar imágenes similares
```

Este proyecto pertenece al:

```txt id="n39iwn"
Plan 4 — Computer Vision, Multimodal AI & Edge Optimization
```

y forma parte del conjunto:

```txt id="b60pua"
Percepción Visual, Multimodalidad e Inferencia Ligera
```

La idea central es entender que una imagen puede convertirse en un embedding visual, y que esos embeddings permiten comparar, recuperar y ordenar imágenes por similitud.

---

## 🎯 Objetivo

Crear una API de búsqueda visual donde una imagen de consulta devuelva imágenes similares desde una colección.

El objetivo técnico es aprender:

* Visual embeddings.
* Feature extraction.
* Similarity search.
* Cosine similarity.
* Vector index.
* Image retrieval.
* Ranking visual.
* API para búsqueda por imagen.

---

## 👤 Usuario objetivo

* AI Engineer en formación.
* Equipo de producto.
* Plataforma de e-commerce.
* Sistema de inventario visual.
* Aplicación de búsqueda por imagen.
* Futuro constructor de sistemas multimodales.
* Reclutador técnico interesado en visual search.

---

## 🧱 Arquitectura esperada

```txt id="zj5ps8"
Colección de imágenes
      ↓
Modelo extractor
      ↓
Embeddings visuales
      ↓
Índice vectorial
      ↓
Imagen de consulta
      ↓
Embedding de consulta
      ↓
Similarity search
      ↓
Ranking de resultados
      ↓
FastAPI
```

---

## 🔁 Flujo técnico

```txt id="if5zhv"
image collection
   ↓
preprocessing
   ↓
pretrained model feature extractor
   ↓
visual embeddings
   ↓
vector index
   ↓
query image
   ↓
query embedding
   ↓
cosine similarity
   ↓
top-k similar images
   ↓
API response
```

---

## 🧩 Módulos

### Módulo 1 — Visual Embedding Extraction

Extraer embeddings visuales desde imágenes.

Incluye:

* Modelo preentrenado.
* Imagen como tensor.
* Feature extractor.
* Vector embedding.
* Normalización del vector.
* Guardado de embeddings.

Pregunta central:

```txt id="cf7i5g"
¿Cómo convierto una imagen en un vector comparable?
```

---

### Módulo 2 — Vector Index Basics

Crear una estructura para buscar embeddings.

Incluye:

* Lista de embeddings.
* Metadata de imágenes.
* IDs.
* Almacenamiento simple.
* Índice vectorial básico.
* Preparación para búsqueda.

Pregunta central:

```txt id="2j00iv"
¿Cómo organizo vectores visuales para poder consultarlos?
```

---

### Módulo 3 — Similarity Scoring

Calcular similitud entre imágenes.

Incluye:

* Cosine similarity.
* Distancia.
* Score.
* Ranking.
* Top-K.
* Comparación de resultados.

Pregunta central:

```txt id="dz5utb"
¿Cómo sé qué imágenes se parecen más a una imagen de consulta?
```

---

### Módulo 4 — Image Query Search

Crear el flujo de búsqueda por imagen.

Incluye:

* Cargar imagen query.
* Aplicar preprocessing.
* Extraer embedding.
* Comparar contra colección.
* Retornar imágenes similares.

Pregunta central:

```txt id="ypev91"
¿Qué ocurre desde que subo una imagen hasta que recibo resultados similares?
```

---

### Módulo 5 — Ranking and Retrieval

Ordenar y filtrar resultados.

Incluye:

* Top-K results.
* Scores.
* Metadata.
* Filtrado de duplicados.
* Interpretación del ranking.
* Resultados visuales.

Pregunta central:

```txt id="h5xbba"
¿Cómo presento los resultados más similares de forma útil?
```

---

### Módulo 6 — Visual Search API

Exponer búsqueda visual mediante API.

Incluye:

* Endpoint de búsqueda.
* Upload de imagen.
* Response schema.
* Lista de resultados.
* Scores.
* Paths o IDs de imágenes.
* Manejo de errores.

Pregunta central:

```txt id="su0lhw"
¿Puedo convertir búsqueda visual en un servicio consultable?
```

---

## 🧪 Labs

### tec-labs

* `tec-visual-embeddings-lab`
* `tec-cosine-similarity-visual-lab`
* `tec-vector-index-basics-lab`
* `tec-image-retrieval-lab`
* `tec-topk-ranking-lab`
* `tec-visual-search-api-lab`

---

## 📊 Métricas / señales de análisis

Métricas y señales posibles:

* Top-K accuracy si hay etiquetas.
* Precision@K si hay relevancia.
* Recall@K si hay ground truth.
* Cosine similarity scores.
* Tiempo de búsqueda.
* Tiempo de extracción de embedding.
* Calidad visual percibida.
* Duplicados encontrados.
* Resultados irrelevantes.
* Diversidad de resultados.

Importante:

```txt id="f68i86"
Dos imágenes pueden ser visualmente parecidas sin significar lo mismo.
La similitud visual no siempre equivale a relevancia para el usuario.
```

---

## 📌 Próximos pasos

* Elegir colección de imágenes.
* Preparar metadata.
* Cargar modelo extractor.
* Crear pipeline de preprocessing.
* Extraer embeddings.
* Guardar embeddings.
* Crear índice vectorial simple.
* Implementar cosine similarity.
* Crear función Top-K.
* Probar búsqueda con imágenes query.
* Revisar resultados visuales.
* Crear endpoint en FastAPI.
* Devolver resultados con scores.
* Documentar limitaciones.
* Grabar demo o explicación corta.
* Actualizar LinkedIn y CV.

---

## ✅ Entregable final

Al terminar este proyecto debe existir:

* Colección de imágenes preparada.
* Modelo extractor de embeddings.
* Embeddings visuales generados.
* Índice vectorial básico.
* Función de búsqueda Top-K.
* API de búsqueda visual.
* Resultados con scores.
* Demo local.
* README técnico.
* Labs documentados.
* Reporte de limitaciones.

---

## 🧭 Regla final

```txt id="1x0fj9"
Buscar visualmente no es clasificar.
Es comparar representaciones.

Una imagen se vuelve buscable cuando puedo convertirla en embedding.
```

Este proyecto no busca crear Google Images.

Busca entender cómo funciona la base de la búsqueda visual moderna.
