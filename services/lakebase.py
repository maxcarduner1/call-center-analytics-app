"""
Lakebase singleton service for connecting to Databricks Lakebase via PostgreSQL protocol.
"""
import os
import uuid
import psycopg2
from datetime import datetime, timedelta
from typing import Optional, List, Tuple, Any
from databricks.sdk import WorkspaceClient


class Lakebase:
    """Singleton service for Lakebase database connections."""
    
    _instance: Optional['Lakebase'] = None
    _connection: Optional[psycopg2.extensions.connection] = None
    _connection_time: Optional[datetime] = None
    _db_user = "mc-call-center-vibing"  # Group name, hardcoded as specified
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def _create_connection(self) -> psycopg2.extensions.connection:
        """Create a new connection to Lakebase with a fresh token."""
        # Initialize Databricks client
        w = WorkspaceClient(
            client_id=os.getenv("DATABRICKS_CLIENT_ID"),
            client_secret=os.getenv("DATABRICKS_CLIENT_SECRET")
        )
        
        instance_name = os.getenv("LAKEBASE_INSTANCE_NAME")
        db_name = os.getenv("LAKEBASE_DB_NAME")
        
        # Generate database credential
        cred = w.database.generate_database_credential(
            request_id=str(uuid.uuid4()), 
            instance_names=[instance_name]
        )
        
        # Get instance details
        instance = w.database.get_database_instance(name=instance_name)
        
        # Create connection
        conn = psycopg2.connect(
            host=instance.read_write_dns,
            dbname=db_name,
            user=self._db_user,
            password=cred.token,
            sslmode="require",
        )
        
        return conn
    
    def _is_connection_expired(self) -> bool:
        """Check if the connection is older than 59 minutes."""
        if self._connection_time is None:
            return True
        
        elapsed = datetime.now() - self._connection_time
        return elapsed > timedelta(minutes=59)
    
    def _ensure_connection(self) -> None:
        """Ensure a valid connection exists, creating or refreshing as needed."""
        if self._connection is None or self._is_connection_expired():
            # Close old connection if it exists
            if self._connection is not None:
                try:
                    self._connection.close()
                except Exception:
                    pass
            
            # Create new connection
            self._connection = self._create_connection()
            self._connection_time = datetime.now()
    
    def query(self, sql: str) -> List[Tuple[Any, ...]]:
        """
        Execute a SQL query and return the results.
        
        Args:
            sql: SQL query string to execute
            
        Returns:
            List of tuples representing the query results
            
        Raises:
            Exception: If the query fails
        """
        # Ensure we have a valid connection
        self._ensure_connection()
        
        # Execute query
        with self._connection.cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
            self._connection.commit()
            return rows
