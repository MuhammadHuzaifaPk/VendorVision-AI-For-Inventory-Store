# VendorVision-AI-For-Inventory-Store

## Main Challenge & Track Alignment
This project was developed for the Next Founders Hackathon Hackathon. The primary challenge addressed is the inefficiency and risk inherent in manual supply chain monitoring and supplier procurement workflows.

<img width="1115" height="480" alt="main2" src="https://github.com/user-attachments/assets/96711f01-b949-43cd-8bb5-902669f2037d" />

## Project Description

### The Problem
Inventory managers and procurement teams rely on static spreadsheets and reactive reordering processes. This manual approach creates a significant lag between identifying a low-stock threshold and issuing a purchase order. The specific technical and commercial challenges include High administrative overhead in drafting and routing supplier emails.

### Solution
VendorVision AI is an inventory management backend and dashboard. It ingests inventory data and generates context-aware, supplier-specific procurement emails using AI models. 

### Target Users
* Procurement Managers orchestrating vendor orders.
* Supply Chain Analysts monitoring stock health.

### Impact
By automating threshold monitoring and purchase order drafting, VendorVision AI reduces administrative procurement time, mitigates the financial risk of critical stockouts, and standardizes vendor communication.

## Key Results

* Integrated an AI prompt generation pipeline that structures supplier emails with SKU, unit cost, and negotiated discount parameters.
* Consolidated frontend and backend into a single ASGI deployment via FastAPI static mounts.

## Tech Stack
* **Backend:** Python 3.12, FastAPI, Uvicorn, Pydantic
* **Data Processing:** OpenPyXL, CSV module
* **Frontend:** HTML5, Vanilla JavaScript, CSS3 (Static architecture, no build step)
* **AI Integration:** Configurable LLM endpoint (defaulting to gemini-2.5-flash via API)

<img width="1097" height="352" alt="api2" src="https://github.com/user-attachments/assets/0c8499d0-830b-40d8-9e21-5eca8a636b44" />

## Prerequisites
* Python 3.10 or higher
* pip (Python package manager)
* A modern web browser (Chrome, Firefox, Edge)

## Local Setup Instructions

1. Clone the repository to your local machine:
   git clone [repository_url]
   cd "VendorVision AI"

2. Create and activate a virtual environment:
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate

3. Install backend dependencies:
   pip install -r backend/requirements.txt

4. Start the FastAPI server:
   cd backend
   python main.py

5. Access the application:
   Open a web browser and navigate to: http://127.0.0.1:8000

## Project Structure

VendorVision AI/
├── backend/
│   ├── main.py                 # ASGI application and API routing
│   ├── models/                 # Pydantic schemas and data models
│   ├── services/
│   │   ├── ai_engine.py        # LLM integration and prompt generation
│   └── requirements.txt & .env       # Python dependencies
├── frontend/
│   ├── css/
│   │   ├── styles.css          # Main layout and typography
│   └── js/
│       ├── api.js              # Fetch wrappers for backend communication
│       ├── app.js              # Application state and event listeners
│       └── ui.js               # DOM manipulation and modal logic
└── index.html                  # Main application entry point
