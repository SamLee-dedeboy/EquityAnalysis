## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/SamLee-dedeboy/EquityAnalysis
```

### 2. Navigate into the Project Folder

```bash
cd eqflow-fullstack
```

This changes your current directory to the root of the project.


## Run the Project

You will run **frontend** and **backend** in **two separate terminal windows**.


### **Terminal 1 — Frontend (Svelte)**

1.  **Install frontend dependencies**  
    (Make sure you are in the project root: `eqflow-fullstack/`)
    ```bash
    npm install
    ``` 

2.  **Start the development server:**
    ```bash
    npm run dev
    ```

The frontend dev server will start (usually at [http://localhost:5173](http://localhost:5173)).

---

### **Terminal 2 — Backend (FastAPI)**

1.  **Go into the server folder:**
    ```bash
    cd server
    ```
    This moves you into the directory containing the Python backend code.

2.  **Create and activate a virtual environment** (named `coeqwal-venv`):

    ```bash
    python -m venv coeqwal-venv
    ```
    This creates a new isolated Python environment for your backend dependencies.

    **Activate on:**
    -   **Windows (PowerShell):**
        ```powershell
        .\coeqwal-venv\Scripts\Activate.ps1
        ```
    -   **macOS/Linux:**
        ```bash
        source coeqwal-venv/bin/activate
        ```

3.  **Install backend dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    This command installs all Python packages listed in `requirements.txt`

4.  **Configure environment variables**:

    Create a `.env` file inside the `server/` folder:
    ```bash
    touch .env
    ```
    This command creates an empty file named `.env`.

    Add your OpenAI API key to `.env`:
    ```ini
    OPENAI_API_KEY="sk-YOUR_ACTUAL_OPENAI_API_KEY_HERE"
    ```
    **Important:** Replace `"sk-YOUR_ACTUAL_OPENAI_API_KEY_HERE"` with your actual OpenAI API key. This key is necessary for the AI analysis features.

5.  **Run the backend server**:

    With your virtual environment activated:
    ```bash
    uvicorn main:app --host 127.0.0.1 --port 8000 --reload
    ```
    This starts the FastAPI backend server. The `--reload` flag ensures the server automatically restarts on code changes.

The backend will now be running on:  
[http://127.0.0.1:8000](http://127.0.0.1:8000)  


### Folder Structure
```bash
eqflow-fullstack/
├── public/                 # Static Assets (e.g., images)
├── src/                    # Svelte Frontend Source Code
│   ├── routes/              # SvelteKit routing
│   ├── lib/                 # components and modules
│   └── app.html
│
├── server/                  # Python Backend (FastAPI application)
│   ├── main.py               # Backend entrypoint and API definitions
│   ├── core/                 # Core backend logic (OpenAI interaction, RAG system, config)
│   ├── models/               # models for API data validation
│   ├── policy_analyses/      # Storage for generated JSON analysis results (preprocessed and user uploads)
│   ├── requirements.txt      # Python dependencies
│   └── .env                  # Environment variables (e.g., API keys)
│
├── package.json              # Frontend dependencies and scripts
├── README.md                 # Project documentation
└── vite.config.js            # Frontend build configuration
```