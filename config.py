# config.py
import yaml
from pydantic import BaseModel, EmailStr
from typing import List
from datetime import time


class EmailConfig(BaseModel):
    email: EmailStr
    password: str


class Config(BaseModel):
    email_config: EmailConfig
    receive_email: List[EmailStr]
    wencai_query: List[str]
    execution_time: time


def load_config(file_path: str) -> Config:
    """加载配置并返回 Config 对象"""
    with open(file_path, "r", encoding="utf-8") as file:
        config_data = yaml.safe_load(file)
    return Config(**config_data)


# 加载配置文件
config = load_config("./conf/config.yaml")
