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
    - **Windows (PowerShell):**
      ```powershell
      .\coeqwal-venv\Scripts\Activate.ps1
      ```
    - **macOS/Linux:**
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

### Database Setup (SQLite)

The application uses a SQLite database (`analysis_platform.db`) for managing sessions, document metadata, and chat history.

**No manual setup is required.** The database file and its tables will be automatically created on the first launch of the FastAPI backend.

---

**Important Notes:**

- **Preprocessed Policies:** JSON reports in `server/policy_analyses/preprocessed/` are read directly from the file system and are not stored in the database. They remain available even if the database is reset.
- **Database Reset:** To reset all application data, simply delete `server/analysis_platform.db`. A new, empty database will be created automatically on the next server startup.

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

## Code Quality & Formatting Setup

This project uses **ESLint** for linting and **Prettier** for code formatting to ensure consistent code style across the team. The configuration is already set up and ready to use.

### What's Included

- ✅ **Prettier** - Automatic code formatting for JavaScript, TypeScript, Svelte, CSS, and JSON files
- ✅ **ESLint** - Code linting with Svelte and TypeScript support
- ✅ **VS Code integration** - Automatic formatting on save
- ✅ **Pre-configured rules** - Consistent formatting rules for the entire team

### Setup for New Team Members

1. **Install recommended VS Code extensions** (you'll be prompted when opening the project):
   - Prettier - Code formatter
   - ESLint
   - Svelte for VS Code
   - Tailwind CSS IntelliSense

2. **VS Code will automatically**:
   - Format your code when you save files
   - Show linting errors and warnings
   - Use the project's formatting configuration

### Available Commands

```bash
# Check if code is properly formatted
npm run format:check

# Format all files automatically
npm run format

# Check for linting errors
npm run lint

# Fix auto-fixable linting errors
npm run lint:fix
```

### Team Workflow

1. **Before committing**: Run `npm run format` and `npm run lint:fix` to ensure consistent code style
2. **During development**: VS Code will automatically format files on save
3. **Code reviews**: All code should be consistently formatted, making reviews easier

### Configuration Files

The following files control code quality and are already configured:

- `.prettierrc` - Prettier formatting rules
- `.eslintrc.json` - ESLint linting rules
- `.vscode/settings.json` - VS Code workspace settings
- `.vscode/extensions.json` - Recommended extensions

**Note**: These configuration files ensure everyone on the team follows the same code style conventions automatically.
