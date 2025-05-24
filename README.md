## 🔧 Setup Instructions

### ⚙️ Run Locally with Python (Recommended for Development)

1. **Create and activate a virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
````

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Streamlit app:**

   ```bash
   streamlit run main.py
   ```

---

### 🐳 Run with Docker (Recommended for Deployment)

1. **Build the Docker image (no cache):**

   ```bash
   docker compose build --no-cache
   ```

2. **Start the application:**

   ```bash
   docker compose up
   ```

---

## 📂 Project Structure

```
├── main.py                 # Streamlit dashboard
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker setup
├── docker-compose.yml      # Docker Compose configuration
├── assets/                 # Static assets (images, data files, etc.)
└── README.md               # Project documentation
```

---

## ✅ Features




## 📋 Notes



---

## 📬 Contact

