# Data Cleaning Web Application

A modern web application for cleaning production data, built with Flask (backend) and React + shadcn/UI (frontend).

## Features

- **File Upload**: Drag-and-drop or browse to upload CSV, Excel, or Parquet files
- **Data Cleaning**: Configure cleaning parameters (RPM max, efficiency range, spindles, etc.)
- **Data Preview**: View uploaded and processed files with pagination
- **File Management**: Download, delete, and manage all your files
- **Database Storage**: All file metadata is stored in SQLite for persistence

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm

### Installation

```bash
# From the project root
cd web

# Install backend dependencies
pip install -r backend/requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### Running the Application

**Option 1: Using the start script**

```bash
./start.sh
```

**Option 2: Manual start (for development)**

Terminal 1 - Backend:
```bash
cd backend
python app.py
```

Terminal 2 - Frontend:
```bash
cd frontend
npm run dev
```

### Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:5000/api

## GitHub Codespaces

This project is configured to work seamlessly with GitHub Codespaces.

1. Open the repository in GitHub
2. Click "Code" → "Codespaces" → "Create codespace on main"
3. Wait for the environment to initialize
4. Run `cd web && ./start.sh`
5. The frontend URL will automatically open in your browser

## Project Structure

```
web/
├── backend/
│   ├── app.py           # Flask application
│   ├── config.py        # Configuration
│   ├── models.py        # SQLAlchemy models
│   ├── requirements.txt # Python dependencies
│   ├── uploads/         # Uploaded files (created at runtime)
│   └── outputs/         # Processed files (created at runtime)
├── frontend/
│   ├── src/
│   │   ├── components/  # UI components
│   │   │   └── ui/      # shadcn/UI components
│   │   ├── lib/         # Utilities and API client
│   │   ├── pages/       # Page components
│   │   ├── App.tsx      # Main app component
│   │   └── main.tsx     # Entry point
│   ├── index.html
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.ts
├── start.sh             # Start script
└── README.md
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/files` | List all files |
| GET | `/api/files?category=input` | List input files |
| GET | `/api/files?category=output` | List output files |
| GET | `/api/files/:id` | Get file details |
| GET | `/api/files/:id/data` | Get file data (paginated) |
| GET | `/api/files/:id/download` | Download file |
| POST | `/api/upload` | Upload a file |
| POST | `/api/process/:id` | Process/clean a file |
| DELETE | `/api/files/:id` | Delete a file |

## Configuration Options

When processing a file, you can configure:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `rpm_max` | 10000 | Maximum RPM threshold |
| `efficiency_min` | 75 | Minimum efficiency % |
| `efficiency_max` | 100 | Maximum efficiency % |
| `spindles_per_side` | 84 | Spindles per machine |
| `shift_hours` | 8 | Shift duration in hours |
| `drop_multi_style_shifts` | true | Remove multi-style shifts |
| `output_format` | csv | Output file format |

## Tech Stack

### Backend
- **Flask** - Web framework
- **Flask-SQLAlchemy** - Database ORM
- **Flask-CORS** - Cross-origin requests
- **Pandas** - Data processing

### Frontend
- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **shadcn/UI** - Component library
- **React Router** - Routing
- **Axios** - HTTP client
- **Lucide React** - Icons

## Screenshots

### Data Cleaning Page
Upload files and configure cleaning parameters.

### Data Files Page
View, preview, and manage all uploaded and processed files.

## Development

### Backend Development

```bash
cd backend
FLASK_ENV=development python app.py
```

### Frontend Development

```bash
cd frontend
npm run dev
```

### Build for Production

```bash
cd frontend
npm run build
```

## License

MIT
