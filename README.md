# 🕋 Inara Travel - Intelligent Travel Platform

![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![OpenAI](https://img.shields.io/badge/RAG_AI-412991?style=for-the-badge&logo=openai&logoColor=white)

> **Inara Travel Capstone** adalah platform travel umrah/wisata modern yang mengintegrasikan website pemesanan paket dengan **AI Chatbot** cerdas untuk melayani calon jamaah secara otomatis (24/7).

---

## 🏗️ Architecture Overview

Project ini dibangun menggunakan arsitektur modular yang terbagi menjadi tiga komponen utama:

1.  **Frontend (Client Side):** Single Page Application (SPA) yang responsif dan cepat.
2.  **Backend Module 1 (AI Chatbot):** Layanan cerdas berbasis RAG (Retrieval-Augmented Generation) untuk menjawab pertanyaan user via WhatsApp/Web Chat.
3.  **Backend Module 2 (Core System):** API untuk manajemen paket wisata, review, dan data pelanggan.

---

## 🌟 Fitur Unggulan

### 🤖 1. AI-Powered Assistant (RAG)
Tidak seperti chatbot biasa, asisten virtual Inara Travel menggunakan teknologi **RAG (Retrieval-Augmented Generation)** dengan **ChromaDB**.
* **Context Aware:** Bot memahami detail paket wisata yang tersedia di database.
* **WhatsApp Integration:** Menangani pertanyaan leads langsung dari WhatsApp.
* **Automated Q&A:** Menjawab pertanyaan seputar harga, jadwal, dan fasilitas secara instan.

### 📦 2. Travel Management System
* **Katalog Paket:** Tampilan paket umrah/wisata dengan detail itinerary.
* **Review System:** User dapat memberikan ulasan layanan.
* **Lead Capture:** Integrasi data calon jamaah potensial.

### 🎨 3. Modern User Interface
* Dibangun dengan **React + TypeScript + Vite**.
* Desain responsif dan estetik menggunakan **Tailwind CSS**.
* Komponen UI interaktif (Floating Chat Widget, Hero Section, dll).

---

## 🛠️ Tech Stack

### Frontend
* **Framework:** React (Vite)
* **Language:** TypeScript
* **Styling:** Tailwind CSS, Shadcn UI
* **State Management:** React Hooks

### Backend & AI
* **Core Language:** Python
* **AI Framework:** LangChain / LlamaIndex (Logic RAG)
* **Vector Database:** ChromaDB (untuk penyimpanan knowledge base AI)
* **Database:** PostgreSQL / SQLite
* **Infrastructure:** Docker & Docker Compose

---

## 🚀 Cara Instalasi (Local Development)

Pastikan Anda sudah menginstall [Docker](https://www.docker.com/) dan [Node.js](https://nodejs.org/).

### 1. Clone Repository
```bash
git clone [https://github.com/alfarros/inara-travel-capstone.git](https://github.com/alfarros/inara-travel-capstone.git)
cd inara-travel-capstone
```

### 2. Menjalankan Backend (via Docker)
```bash
cd backend
docker-compose up --build
```

### 3. Menjalankan Frontend
```bash
cd frontend
npm install
npm run dev
```

Untuk lebih lanjut bisa lihat di Web :
https://inara-travel.vercel.app/
