"""
Configuration management for OSTicket API v2

Reads configuration from OSTicket's ost-config.php and environment variables.
"""

import os
import re
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
import structlog

logger = structlog.get_logger()

def parse_osticket_config() -> dict:
    """Parse OSTicket configuration from ost-config.php"""
    config = {}
    config_path = os.path.join(
        os.path.dirname(__file__),
        "../../../osTicket/include/ost-config.php"
    )
    
    if not os.path.exists(config_path):
        logger.warning("OSTicket config file not found", path=config_path)
        return config
    
    try:
        with open(config_path, 'r') as f:
            content = f.read()
            
        # Extract database configuration
        patterns = {
            'DBHOST': r"define\s*\(\s*['\"]DBHOST['\"]\s*,\s*['\"]([^'\"]+)['\"]",
            'DBNAME': r"define\s*\(\s*['\"]DBNAME['\"]\s*,\s*['\"]([^'\"]+)['\"]",
            'DBUSER': r"define\s*\(\s*['\"]DBUSER['\"]\s*,\s*['\"]([^'\"]+)['\"]",
            'DBPASS': r"define\s*\(\s*['\"]DBPASS['\"]\s*,\s*['\"]([^'\"]+)['\"]",
            'TABLE_PREFIX': r"define\s*\(\s*['\"]TABLE_PREFIX['\"]\s*,\s*['\"]([^'\"]*)['\"]",
            'SECRET_SALT': r"define\s*\(\s*['\"]SECRET_SALT['\"]\s*,\s*['\"]([^'\"]+)['\"]",
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, content)
            if match:
                config[key] = match.group(1)
                logger.debug(f"Found OSTicket config: {key}")
            else:
                logger.warning(f"OSTicket config not found: {key}")
                
    except Exception as e:
        logger.error("Failed to parse OSTicket config", error=str(e))
    
    return config

class Settings(BaseSettings):
    """Application settings"""
    
    # Database settings (from OSTicket config)
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 3306
    DATABASE_NAME: str = "osticket"
    DATABASE_USER: str = "osticket"
    DATABASE_PASSWORD: str = ""
    TABLE_PREFIX: str = "ost_"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Redis (for caching and sessions)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Application
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        
        @classmethod
        def customise_sources(cls, init_settings, env_settings, file_secret_settings):
            # Load OSTicket config first, then override with env vars
            osticket_config = parse_osticket_config()
            
            def osticket_settings(settings_cls):
                config_mapping = {
                    'DATABASE_HOST': osticket_config.get('DBHOST', 'localhost'),
                    'DATABASE_NAME': osticket_config.get('DBNAME', 'osticket'),
                    'DATABASE_USER': osticket_config.get('DBUSER', 'osticket'),
                    'DATABASE_PASSWORD': osticket_config.get('DBPASS', ''),
                    'TABLE_PREFIX': osticket_config.get('TABLE_PREFIX', 'ost_'),
                    'SECRET_KEY': osticket_config.get('SECRET_SALT', 'your-secret-key-here'),
                }
                return config_mapping
            
            return (
                init_settings,
                osticket_settings,
                env_settings,
                file_secret_settings,
            )
    
    @field_validator('ALLOWED_HOSTS', mode='before')
    @classmethod
    def parse_hosts(cls, v):
        if isinstance(v, str):
            # Handle JSON-like string format
            if v.startswith('[') and v.endswith(']'):
                import json
                try:
                    return json.loads(v)
                except json.JSONDecodeError:
                    pass
            # Handle comma-separated string
            return [host.strip() for host in v.split(',') if host.strip()]
        return v
    
    @property
    def DATABASE_URL(self) -> str:
        """Construct database URL for SQLAlchemy"""
        return (
            f"mysql+pymysql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
            f"?charset=utf8mb4"
        )

# Global settings instance
settings = Settings()

# Log configuration summary (without sensitive data)
logger.info(
    "Configuration loaded",
    database_host=settings.DATABASE_HOST,
    database_name=settings.DATABASE_NAME,
    table_prefix=settings.TABLE_PREFIX,
    debug=settings.DEBUG,
    log_level=settings.LOG_LEVEL,
)