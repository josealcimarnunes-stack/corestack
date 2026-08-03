"""
📦 MODELOS - WebStruct Analyzer
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base
import datetime


class Coleta(Base):
    """Tabela de coletas de HTML"""

    __tablename__ = "coletas"

    id = Column(Integer, primary_key=True, index=True)
    site = Column(String(100), nullable=False)
    url = Column(String(500), nullable=False)
    html = Column(Text, nullable=False)
    tamanho_kb = Column(Float, default=0)
    data_criacao = Column(DateTime, default=datetime.datetime.now)

    # ⭐ Relacionamento com produtos
    produtos = relationship(
        "Produto", back_populates="coleta", cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "site": self.site,
            "url": self.url,
            "tamanho_kb": self.tamanho_kb,
            "data": (
                self.data_criacao.strftime("%Y-%m-%d %H:%M:%S")
                if self.data_criacao
                else ""
            ),
            "total_produtos": len(self.produtos) if self.produtos else 0,
        }


class Produto(Base):
    """Tabela de produtos extraídos do HTML"""

    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    coleta_id = Column(Integer, ForeignKey("coletas.id"), nullable=False)

    # ⭐ Dados do produto
    nome = Column(String(300), nullable=True)
    preco_texto = Column(String(50), nullable=True)
    preco_valor = Column(Float, nullable=True)
    seletor = Column(String(500), nullable=True)
    link = Column(String(500), nullable=True)
    produto_id = Column(String(100), nullable=True)
    arvore_json = Column(Text, nullable=True)

    data_criacao = Column(DateTime, default=datetime.datetime.now)

    # ⭐ Relacionamento com coleta
    coleta = relationship("Coleta", back_populates="produtos")

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "preco_texto": self.preco_texto,
            "preco_valor": self.preco_valor,
            "seletor": self.seletor,
            "link": self.link,
            "produto_id": self.produto_id,
            "data": (
                self.data_criacao.strftime("%Y-%m-%d %H:%M:%S")
                if self.data_criacao
                else ""
            ),
        }
