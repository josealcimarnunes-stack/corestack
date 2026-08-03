"""
🗄️ DATABASE - SQLAlchemy + SQLite
"""

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


def get_data_dir():
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base, "data")
    os.makedirs(data_dir, exist_ok=True)
    return data_dir


def get_db_path():
    return os.path.join(get_data_dir(), "webstruct.db")


DB_PATH = get_db_path()
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False, "timeout": 30},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Cria as tabelas se não existirem"""
    from core.models import Coleta, Produto  # ⭐ SÓ ISSO!

    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Tabelas criadas/verificadas com sucesso!")
        print(f"   📁 Banco: {DB_PATH}")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        return False


def salvar_coleta(url: str, html: str) -> int:
    from core.models import Coleta
    from urllib.parse import urlparse

    db = SessionLocal()
    try:
        parsed = urlparse(url)
        site = parsed.netloc.replace("www.", "").split(".")[0]
        coleta = Coleta(
            site=site, url=url, html=html, tamanho_kb=round(len(html) / 1024, 2)
        )
        db.add(coleta)
        db.commit()
        db.refresh(coleta)
        return coleta.id
    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao salvar coleta: {e}")
        return None
    finally:
        db.close()


def obter_html_por_id(coleta_id: int):
    from core.models import Coleta

    db = SessionLocal()
    try:
        coleta = db.query(Coleta).filter(Coleta.id == coleta_id).first()
        if coleta:
            return (coleta.html, coleta.url, coleta.site)
        return None
    finally:
        db.close()


def listar_coletas(limite=20):
    from core.models import Coleta

    db = SessionLocal()
    try:
        return db.query(Coleta).order_by(Coleta.id.desc()).limit(limite).all()
    finally:
        db.close()


def deletar_coleta(coleta_id: int):
    from core.models import Coleta

    db = SessionLocal()
    try:
        coleta = db.query(Coleta).filter(Coleta.id == coleta_id).first()
        if coleta:
            db.delete(coleta)
            db.commit()
    finally:
        db.close()


def contar_produtos() -> int:
    from core.models import Produto

    db = SessionLocal()
    try:
        return db.query(Produto).count()
    finally:
        db.close()
