import os
from pathlib import Path

class Config:

    PROJECT_ROOT = Path(__file__).resolve().parent # 项目根目录

    # 环境配置：dev=开发环境, prd=生产环境
    ENVIRONMENT = os.getenv("ENV", "dev").lower()
    # ENVIRONMENT = os.getenv("ENV", "prd").lower()

    # ==================== S3配置 ====================
    # 开发环境S3配置
    S3_DEV_ENDPOINT = "http://s3sdossuat.smb956101.com"
    S3_DEV_ACCESS_KEY = "32M159U46FMEH2ZC"
    S3_DEV_SECRET_KEY = "JAPmQFysplHJVqV985c6kSiJK-E="
    S3_DEV_BUCKET = "pucms"

    # 生产环境S3配置
    S3_PRD_ENDPOINT = "http://s3sdoss.smb956101.com:80"
    S3_PRD_ACCESS_KEY = "89259813DUB9CCQ0"
    S3_PRD_SECRET_KEY = "CAjkWFobpiDJlu4GGQOUT6om6fs="
    S3_PRD_BUCKET = "pucms"

    # LLM 配置
    LLM_CONFIG = {
            "current_env": "prd",
            "base_url": "http://lmsgw.lms.smb956101.com",
            "model": "Qwen3-32B",
            "authorization": "sk-DTTukLBmHxVb9KP-_rthVw"
    }

    @property
    def S3_ENDPOINT(self):
        return self.S3_PRD_ENDPOINT if self.ENVIRONMENT == "prd" else self.S3_DEV_ENDPOINT

    @property
    def S3_ACCESS_KEY(self):
        return self.S3_PRD_ACCESS_KEY if self.ENVIRONMENT == "prd" else self.S3_DEV_ACCESS_KEY

    @property
    def S3_SECRET_KEY(self):
        return self.S3_PRD_SECRET_KEY if self.ENVIRONMENT == "prd" else self.S3_DEV_SECRET_KEY

    @property
    def S3_BUCKET(self):
        return self.S3_PRD_BUCKET if self.ENVIRONMENT == "prd" else self.S3_DEV_BUCKET


config = Config()