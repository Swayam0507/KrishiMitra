# 🌾 KrishiMitra (AgriSmart AI) — Intelligent Agriculture Platform

[![GitHub Repository](https://img.shields.io/badge/GitHub-Swayam0507%2FKrishiMitra-181717?style=for-the-badge&logo=github)](https://github.com/Swayam0507/KrishiMitra.git)
[![Python Version](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)](https://pytorch.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

> **Repository URL**: `https://github.com/Swayam0507/KrishiMitra.git`  
> **Domain**: AI / AgriTech / Sustainability  
> **Core Focus**: AI-driven crop disease diagnosis, smart irrigation scheduling, soil-based crop recommendation, GenAI advisory, and real-time IoT microclimate monitoring.

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features & Built Modules](#-key-features--built-modules)
- [System Architecture](#-system-architecture)
- [Repository Structure](#-repository-structure)
- [Quick Start Guide](#-quick-start-guide)
  - [1. Prerequisites](#1-prerequisites)
  - [2. Clone Repository](#2-clone-repository)
  - [3. Core CLI Prediction](#3-core-cli-prediction)
  - [4. Backend Setup (FastAPI)](#4-backend-setup-fastapi)
  - [5. Frontend Setup (React + Vite)](#5-frontend-setup-react--vite)
- [API Reference](#-api-reference)
- [ML Models & Evaluation](#-ml-models--evaluation)
- [Environment Variables](#-environment-variables)
- [License](#-license)

---

## 💡 Overview

**KrishiMitra (AgriSmart AI)** is an integrated end-to-end agricultural intelligence platform designed to empower farmers with actionable insights. Combining Computer Vision, Machine Learning, Generative AI, and IoT Telemetry, KrishiMitra helps optimize crop yields, detect plant diseases early, conserve water, and improve overall soil health.

---

## 🏆 Key Features & Built Modules

| Module | Category | Description | Status |
| :--- | :--- | :--- | :---: |
| **Crop Disease Detection** | **Core CV** | PyTorch ResNet-50 leaf image classifier reporting **Macro-F1 0.864** with Grad-CAM visual explainability maps. | ✅ **Built** |
| **Crop Recommendation** | **ML Engine** | Multi-class predictor determining optimal crops based on NPK, temperature, humidity, pH, and rainfall. | ✅ **Built** |
| **Smart Irrigation Advisor** | **Precision Agri** | Evapotranspiration (ET0) model calculating water volume (Liters) and drip duration (Minutes). | ✅ **Built** |
| **Weather & Microclimate** | **Analytics** | Microclimate station metrics, 7-day agricultural forecasts, and optimal chemical spray windows. | ✅ **Built** |
| **Sustainability Score** | **Eco Index** | Resource efficiency score (0–100) quantifying water conservation, soil preservation, and carbon impact. | ✅ **Built** |
| **GenAI Farmer Assistant** | **Conversational AI** | Grounded multilingual AI chatbot (Google Gemini) for plain-language advisory in regional languages. | ✅ **Built** |
| **IoT Telemetry Stream** | **Hardware / IoT** | Simulated real-time sensor feed monitoring soil moisture, temperature, humidity, and soil pH. | ✅ **Built** |
| **Agentic Advisor** | **Autonomous Agent** | Autonomous decision engine executing continuous sense-reason-act loops for holistic farm management. | ✅ **Built** |

---

## 🏗️ System Architecture

```
                          ┌───────────────────────────────────────────┐
                          │         React 18 + Vite Frontend          │
                          │   (Interactive Dashboards & UI Token Set) │
                          └─────────────────────┬─────────────────────┘
                                                │ REST API / JSON
                                                ▼
                          ┌───────────────────────────────────────────┐
                          │          FastAPI Backend Server           │
                          └───────┬─────────────┬─────────────┬───────┘
                                  │             │             │
         ┌────────────────────────┴─┐    ┌──────┴──────────┐  └────────────────────────┐
         │ PyTorch Computer Vision  │    │ Scikit-learn    │   │  Google Gemini GenAI   │
         │ ResNet-50 Disease Model  │    │ ML Predictors   │   │  Agentic AI Advisor    │
         └──────────────────────────┘    └─────────────────┘   └────────────────────────┘
```

---

## 📁 Repository Structure

```text
KrishiMitra/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── database.py          # Database configuration & ORM
│   │   ├── dependencies.py      # Auth & service dependencies
│   │   └── routes/              # API Route Handlers
│   │       ├── disease.py       # Disease detection endpoint
│   │       ├── crop.py          # Crop recommendation endpoint
│   │       ├── irrigation.py    # Smart irrigation endpoint
│   │       ├── weather.py       # Weather intelligence endpoint
│   │       ├── sustainability.py# Sustainability score endpoint
│   │       ├── assistant.py     # GenAI chatbot endpoint
│   │       └── iot.py           # IoT sensor telemetry endpoint
│   ├── requirements.txt         # Python backend dependencies
│   ├── .env.example             # Backend environment template
│   └── uploads/                 # Temporary directory for image uploads
├── frontend/
│   ├── src/                     # React 18 source code
│   │   ├── components/          # UI Components
│   │   ├── pages/               # Application Page Views
│   │   └── App.jsx              # Main React Router & Layout
│   ├── index.html               # HTML entry point
│   ├── package.json             # Frontend dependencies & scripts
│   └── vite.config.js           # Vite dev server configuration
├── ml/
│   ├── disease/                 # PyTorch Disease Detection Module
│   │   ├── predict.py           # Inference module & predictor class
│   │   ├── model.py             # ResNet-50 backbone definition
│   │   ├── dataset.py           # Data loader pipeline
│   │   ├── train.py             # Model training script
│   │   ├── evaluate.py          # Evaluation & metrics generator
│   │   └── gradcam.py           # Grad-CAM visual heatmaps
│   ├── crop_recommendation/     # Scikit-learn Crop Recommender
│   ├── irrigation/              # Smart Irrigation ET0 calculator
│   └── requirements.txt         # ML environment dependencies
├── docs/                        # Project documentation & specs
├── report/                      # Model benchmark reports & evaluations
├── predict.py                   # Mandatory Single-Command Core CLI Interface
└── README.md                    # Project documentation
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites

- **Python**: `v3.10` or higher
- **Node.js**: `v18.0` or higher
- **Git**: Installed and configured

---

### 2. Clone Repository

```bash
git clone https://github.com/Swayam0507/KrishiMitra.git
cd KrishiMitra
```

---

### 3. Core CLI Prediction (Single-Command Interface)

Run single-command crop disease prediction on any leaf image:

```bash
# Standard CLI Output
python predict.py --image path/to/leaf_image.jpg

# JSON Formatted Output
python predict.py --image path/to/leaf_image.jpg --json
```

**Python API Usage:**
```python
from predict import predict

class_label = predict("path/to/leaf_image.jpg")
print("Predicted Disease Class:", class_label)
```

---

### 4. Backend Setup (FastAPI)

1. Navigate to `backend` directory:
   ```bash
   cd backend
   ```

2. Create & activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```

3. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```bash
   cp .env.example .env
   ```

5. Start the server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   - **Backend Server**: `http://localhost:8000`
   - **Swagger OpenAPI Docs**: `http://localhost:8000/docs`

---

### 5. Frontend Setup (React + Vite)

1. Navigate to `frontend` directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start development server:
   ```bash
   npm run dev
   ```
   - **Frontend App**: `http://localhost:5173`

---

## 🔌 API Reference

| Endpoint | Method | Description |
| :--- | :---: | :--- |
| `/api/disease/predict` | `POST` | Upload image for plant disease diagnosis & confidence score |
| `/api/crop/recommend` | `POST` | Get crop suggestions based on NPK values and climate parameters |
| `/api/irrigation/calculate` | `POST` | Calculate recommended irrigation water volume and drip runtime |
| `/api/weather/forecast` | `GET` | Get 7-day microclimate weather forecast and spray window alert |
| `/api/sustainability/score` | `POST` | Calculate farm resource efficiency index (0–100) |
| `/api/assistant/chat` | `POST` | GenAI grounded advisory response for farmer queries |
| `/api/iot/telemetry` | `GET` | Live stream of IoT telemetry sensor readings |

---

## 📊 ML Models & Evaluation

- **Dataset**: Trained on **PlantVillage** (~54,000 lab images) and validated on **PlantDoc** (real-world field conditions).
- **Backbone Architecture**: ResNet-50 Transfer Learning fine-tuned with PyTorch.
- **Evaluation Metrics**:
  - **Macro-F1 Score**: `0.864` (Baseline `0.740`, **+0.124** improvement)
  - **Overall Accuracy**: `88.2%`
  - **Precision**: `0.871` | **Recall**: `0.858`
- **Explainability**: Integrated Grad-CAM feature heatmaps highlighting leaf lesion areas.

---

## ⚙️ Environment Variables

Create a `.env` file in the `backend/` directory:

```env
PROJECT_NAME="KrishiMitra AgriSmart AI"
SECRET_KEY="your-secret-key-here"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# MongoDB Connection (Optional / Default Fallback Active)
MONGODB_URL="mongodb://localhost:27017"
DATABASE_NAME="krishimitra"

# Generative AI (Optional)
GEMINI_API_KEY="your-gemini-api-key"
```

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for more information.

---

<p align="center">
  <b>Built with ❤️ for Sustainable Agriculture & Smart Farming</b><br>
  <sub>KrishiMitra • <a href="https://github.com/Swayam0507/KrishiMitra.git">GitHub Repository</a></sub>
</p>
