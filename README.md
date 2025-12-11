
```
inara-travel-capstone
├─ backend
│  ├─ .dockerignore
│  ├─ db_schema.sql
│  ├─ docker-compose.yml
│  ├─ dummy_data
│  │  ├─ interactions.csv
│  │  ├─ leads.csv
│  │  ├─ packages.csv
│  │  └─ reviews.csv
│  ├─ module_1_chatbot
│  │  ├─ app
│  │  │  ├─ database.py
│  │  │  ├─ main.py
│  │  │  ├─ rag_logic.py
│  │  │  ├─ schemas.py
│  │  │  ├─ whatsapp_handler.py
│  │  │  └─ __init__.py
│  │  ├─ chroma_db
│  │  │  ├─ b6a303a9-0b88-43f2-8e8d-266f9351e48e
│  │  │  │  ├─ data_level0.bin
│  │  │  │  ├─ header.bin
│  │  │  │  ├─ length.bin
│  │  │  │  └─ link_lists.bin
│  │  │  └─ chroma.sqlite3
│  │  ├─ Dockerfile
│  │  ├─ knowledge_base
│  │  │  ├─ 01_packages.txt
│  │  │  └─ 02_faq.txt
│  │  ├─ requirements.txt
│  │  └─ scripts
│  │     ├─ ingest_knowledge.py
│  │     └─ __init__.py
│  ├─ module_2_packages_reviews
│  │  ├─ app
│  │  │  ├─ database.py
│  │  │  ├─ main.py
│  │  │  ├─ models.py
│  │  │  ├─ schemas.py
│  │  │  └─ __init__.py
│  │  ├─ Dockerfile
│  │  └─ requirements.txt
│  └─ README.md
└─ frontend
   ├─ bun.lockb
   ├─ components.json
   ├─ eslint.config.js
   ├─ index.html
   ├─ package-lock.json
   ├─ package.json
   ├─ postcss.config.js
   ├─ public
   │  ├─ android-chrome-192x192.png
   │  ├─ android-chrome-512x512.png
   │  ├─ apple-touch-icon.png
   │  ├─ assets
   │  │  ├─ feature-nyaman.jpg
   │  │  ├─ feature-sunnah.jpg
   │  │  ├─ feature-terbimbing.jpg
   │  │  ├─ founder-photo.jpg
   │  │  ├─ hero-mosque.jpg
   │  │  └─ jamaah-group.jpg
   │  ├─ favicon.ico
   │  ├─ logo-inara.png
   │  ├─ placeholder.svg
   │  └─ robots.txt
   ├─ README.md
   ├─ src
   │  ├─ App.tsx
   │  ├─ components
   │  │  ├─ About.tsx
   │  │  ├─ FloatingChatWidget.tsx
   │  │  ├─ Footer.tsx
   │  │  ├─ Hero.tsx
   │  │  ├─ Navbar.tsx
   │  │  ├─ Packages.tsx
   │  │  ├─ Partners.tsx
   │  │  ├─ ReviewForm.tsx
   │  │  ├─ Testimonials.tsx
   │  │  ├─ ui
   │  │  │  ..tetap sama
   │  │  └─ WhyChooseUs.tsx
   │  ├─ data
   │  │  ├─ features.ts
   │  │  ├─ partners.ts
   │  │  └─ testimonials.ts
   │  ├─ hooks
   │  │  ├─ use-chat.ts
   │  │  ├─ use-mobile.tsx
   │  │  └─ use-toast.ts
   │  ├─ index.css
   │  ├─ lib
   │  │  ├─ api.ts
   │  │  └─ utils.ts
   │  ├─ main.tsx
   │  ├─ pages
   │  │  ├─ About.tsx
   │  │  ├─ Contact.tsx
   │  │  ├─ Index.tsx
   │  │  ├─ NotFound.tsx
   │  │  ├─ PackageDetail.tsx
   │  │  └─ Packages.tsx
   │  └─ vite-env.d.ts
   ├─ tailwind.config.ts
   ├─ tsconfig.app.json
   ├─ tsconfig.json
   ├─ tsconfig.node.json
   └─ vite.config.ts

```