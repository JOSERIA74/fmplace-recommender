# FM Place Recommender

**FP&A Tool Recommendation API & Configuration**

Este repositorio contiene todo lo necesario para generar recomendaciones personalizadas de herramientas FP&A basadas en las respuestas de un usuario.

---

## 📁 Estructura del repositorio
├── config_recomendador.xlsx # Excel maestro: Tools, Questions, Scores, Weights, Justifications

├── excel_to_json.py # Convierte el Excel en JSON de configuración

├── main.py # API Flask con endpoint /recommend

├── auto_analysis.py # Script de análisis/optimización de pesos (PCA, clusters)

├── requirements.txt # Dependencias Python

├── .gitignore # Ignora JSONs generados, imágenes, pycache, etc.

├── .github/ # Workflows de CI:

│ └── workflows/

│ ├── generate-json.yml # CI para rama main → regenera JSONs

│ └── generate-json-dev.yml # CI para rama dev → regenera JSONs

└── README.md # Este fichero

---

## 🚀 Flujo End-to-End

1. **Fillout Form** → Make (webhook)  
2. Make → **Repl “dev”** (`/recommend`) → top_1/top_2/top_3  
3. Make → descarga JSON (`metadata.json`, `justifications.json`) de la rama `dev`  
4. Make → llama al **Assistant Dev** → devuelve HTML  
5. Make → envía **email** con HTML + botón CTA  

En producción, reemplaza URL de Repl, rama de GitHub (`main`) y Assistant ID por los de prod.

---

## ⚙️ Instalación y uso local

```bash
# 1. Instala dependencias
pip install -r requirements.txt

# 2. Genera los JSON de configuración
python excel_to_json.py

# 3. Arranca la API
python main.py
# → Escucha en http://127.0.0.1:3000

# 4. Prueba un POST
curl -X POST http://127.0.0.1:3000/recommend \
  -H "Content-Type: application/json" \
  -d '{"q1_size":2, "q2_budget":7, …, "q13_implementation":58}'
  
🔄 CI/CD
Rama main:

Al hacer push a main, .github/workflows/generate-json.yml regenera y commitea los JSONs.

Repl Prod vinculado a main se actualiza automáticamente.

Rama dev:

Al hacer push a dev, .github/workflows/generate-json-dev.yml regenera los JSONs en dev.

Repl Dev vinculado a dev se actualiza para pruebas.

📝 Cómo contribuir
Crea una rama desde dev:

git checkout dev
git pull
git checkout -b feature/tu-descripcion
Haz tus cambios en Excel, código (*.py), prompt o email template.

Genera localmente los JSON (python excel_to_json.py) para probar.

Edita este README.md si cambias estructura o pasos.

Commit y push:

git add .
git commit -m "docs: actualiza README con nueva estructura"
git push -u origin feature/tu-descripcion
Abre PR a dev, revisa la CI y pruebas en Repl Dev + Make Dev.

Si todo OK, merge a dev → luego merge dev→main para prod.

© 2025 FM Place. All rights reserved.