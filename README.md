# Call Center Analytics App

A FastAPI web application for call center analytics, built for deployment on Databricks Apps.

## Technologies Used

- **FastAPI**: High-performance web framework for building APIs
- **Uvicorn**: ASGI server for running the FastAPI application
- **Python-dotenv**: Environment variable management for configuration

## Getting Started

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables:

   - Copy `example.env` to `.env`
   - Fill in your actual Databricks credentials

3. Run the application:

   ```bash
   python app.py
   ```

   Or use uvicorn directly:

   ```bash
   uvicorn app:app --reload --port 8000
   ```

4. Open your browser to `http://localhost:8000`

## Why These Technologies?

- **FastAPI**: Modern, fast, and type-safe Python web framework with automatic API documentation
- **Databricks Apps**: Provides managed hosting and integration with Databricks services
- **Environment Variables**: Secure configuration management for credentials and settings
