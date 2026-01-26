# Call Center Analytics App

A FastAPI web application for call center analytics, built for deployment on Databricks Apps with Lakebase integration.

## Technologies Used

- **FastAPI**: High-performance web framework for building APIs
- **Uvicorn**: ASGI server for running the FastAPI application
- **Python-dotenv**: Environment variable management for configuration
- **Databricks SDK**: Integration with Databricks services and Lakebase
- **PostgreSQL (psycopg2)**: Database connectivity via Lakebase autoscaling PostgreSQL

## Getting Started

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables:

   - Copy `example.env` to `.env`
   - Fill in your actual Databricks credentials:
     - `DATABRICKS_HOST`
     - `DATABRICKS_CLIENT_ID`
     - `DATABRICKS_CLIENT_SECRET`
     - `LAKEBASE_INSTANCE_NAME`
     - `LAKEBASE_DB_NAME`

3. Run the application:

   ```bash
   python app.py
   ```

   Or use uvicorn directly:

   ```bash
   uvicorn app:app --reload --port 8000
   ```

4. Open your browser to `http://localhost:8000`

## Features

- **Lakebase Connection**: Singleton service for efficient database connections with automatic token refresh
- **Token Management**: Automatic renewal of database credentials every 59 minutes
- **Database Testing**: Built-in connection test via the web UI

## API Endpoints

- `GET /` - Main application page
- `GET /api/test-db` - Test Lakebase connection and return current database time

## Why These Technologies?

- **FastAPI**: Modern, fast, and type-safe Python web framework with automatic API documentation
- **Databricks Apps**: Provides managed hosting and integration with Databricks services
- **Databricks Lakebase**: Autoscaling PostgreSQL serving layer that bridges Lakehouse and operational apps
- **Singleton Pattern**: Efficient connection pooling with automatic token refresh
- **Environment Variables**: Secure configuration management for credentials and settings
