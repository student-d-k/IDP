
# Igudziu dalinimosi platforma (IDP)

# kaip pradeti projekta

C:\Users\..\codeacademy\IDP> python.exe -m pip install --upgrade pip

poetry init

poetry install

poetry shell
man dar reikia paleisti rankiniu budu .\scripts\activate.ps1

pip install sqlalchemy

pip install alembic

alembic init migrations

env.py:
from model.idp_classes import Base
target_metadata = Base.metadata

alembic.ini:
sqlalchemy.url = sqlite:///data/idp.db

# github

https://github.com/student-d-k/IDP
