# How to Run the Report Analyzer Application

This document provides instructions on how to set up and run the backend and frontend of the Report Analyzer application.

## Prerequisites

- Python 3.8+
- Node.js 16+
- npm / yarn

## Backend Setup

1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    ```

3.  **Activate the virtual environment:**
    -   On Windows:
        ```bash
        .\venv\Scripts\activate
        ```
    -   On macOS/Linux:
        ```bash
        source venv/bin/activate
        ```

4.  **Install the required Python packages:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Set the Groq API key:**
    Create a `.env` file in the `backend` directory and add your Groq API key:
    ```
    GROQ_API_KEY="your_groq_api_key_here"
    ```
    Alternatively, you can set it as an environment variable.

6.  **Run the backend server:**
    ```bash
    python main.py
    ```
    The backend server will start on `http://localhost:8000`. You can access the API documentation at `http://localhost:8000/api/docs`.

## Frontend Setup

1.  **Navigate to the frontend directory:**
    ```bash
    cd frontend
    ```

2.  **Install the required Node.js packages:**
    ```bash
    npm install
    ```
    or if you use yarn:
    ```bash
    yarn
    ```

3.  **Run the frontend development server:**
    ```bash
    npm run dev
    ```
    The frontend application will be available at `http://localhost:5173`. The application is configured to proxy API requests to the backend server.
