# Modelo Lógico del Mercado de Criptomonedas

Este repositorio contiene los scripts y recursos utilizados para el **Proyecto de la PC2 del curso de Machine Learning**, cuyo objetivo es representar el mercado de criptomonedas mediante un **modelo lógico basado en Teoría de Grafos**, utilizando datos de la API de CoinGecko.

---

## 📌 Contenido del Repositorio
- **extracccion_data_coingecko.py** → Script en Python para extraer automáticamente los datos del mercado cripto desde la API pública de CoinGecko.
- **creacion_visualizacion_grafo.py** → Script para la construcción y visualización de la red de criptomonedas a partir de los datos extraídos.
- **dataset_cripto_completo.csv** → Dataset generado como resultado de la extracción de datos.
- **requirements.txt** → Librerías necesarias para ejecutar los scripts.
- **README.md** → Documento actual.

---

## 🚀 Instalación y Requisitos
Clonar el repositorio:
```bash
git clone https://github.com/usuario/cripto-graph-model.git
cd cripto-graph-model
```

Instalar dependencias:
```bash
pip install -r requirements.txt
```

Librerías principales utilizadas:
- `requests`
- `pandas`
- `networkx`
- `matplotlib`

---

## ⚡ Uso
1. **Extracción de datos**
   Ejecutar:
   ```bash
   python extracccion_data_coingecko.py
   ```
   Esto generará un archivo CSV con la información de los activos.

2. **Creación y visualización del grafo**
   Ejecutar:
   ```bash
   python creacion_visualizacion_grafo.py
   ```
   Este script genera un grafo que representa las relaciones entre proyectos de criptomonedas.

---

## 📊 Objetivo
El proyecto busca analizar y clasificar los proyectos cripto en categorías como **Inteligencia Artificial, Videojuegos, RWA y Memes**, considerando atributos como:
- Capitalización
- Volumen de trading
- Suministro
- Actividad comunitaria  
entre otros indicadores relevantes.
