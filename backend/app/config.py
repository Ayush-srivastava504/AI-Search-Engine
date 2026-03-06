from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    elasticsearch_host: str = "http://localhost:9200"
    redis_url: str = "redis://localhost:6379"
    
    devto_api_url: str = "https://dev.to/api/articles"
    medium_api_url: str = "https://medium.com"
    hackernews_api_url: str = "https://hacker-news.firebaseio.com/v0"
    
    embedding_model: str = "all-MiniLM-L6-v2"
    
    max_snippet_length: int = 200
    default_top_k: int = 10
    
    jwt_secret: str = "your-secret-key"
    
    class Config:
        env_file = ".env"


settings = Settings()