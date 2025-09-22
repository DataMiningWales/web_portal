import os
from typing import Optional


class Settings:
    """Simple settings class without pydantic-settings dependency"""
    
    def __init__(self):
        # Neo4j/AuraDB settings
        self.neo4j_uri = os.getenv("NEO4J_URI", "neo4j+s://localhost:7687")
        self.neo4j_username = os.getenv("NEO4J_USERNAME", "neo4j")
        self.neo4j_password = os.getenv("NEO4J_PASSWORD", "password")
        
        # App settings
        self.secret_key = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
        self.algorithm = os.getenv("ALGORITHM", "HS256")
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        
        # Email settings
        self.sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@dataminingwales.org")
        
        # Admin settings
        self.admin_username = os.getenv("ADMIN_USERNAME", "admin")
        self.admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
        
        # Logging
        self.log_level = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()