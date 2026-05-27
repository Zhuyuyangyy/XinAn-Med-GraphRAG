from dataclasses import dataclass

@dataclass
class Settings:
    app_name: str = "XinAn-Med-GraphRAG"
    version: str = "0.1.0"
    port: int = 8024

settings = Settings()
