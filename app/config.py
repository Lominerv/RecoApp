import os
from pathlib import Path


#путь до проекта
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

#путь до БД
DB_PATH = os.path.join(BASE_DIR, 'reco_database.db')

#Папка с ресурсами
ASSETS_DIR= os.path.join(BASE_DIR, "assets")

#Папка с пласенхолдеерами
PLACEHOLDERS = os.path.join(ASSETS_DIR, 'placeholders')

#Папка с иконками в ресурсах
ICONS_DIR = os.path.join(ASSETS_DIR, "icons")

def icon_path(name: str) -> str:
    return os.path.join(ICONS_DIR, name)