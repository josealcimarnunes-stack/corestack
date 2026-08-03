"""
📦 MODELOS - WebStruct Analyzer (Estrutura Definitiva)
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base
import datetime
import json


class Coleta(Base):
    """Tabela de coletas (HTML bruto)"""

    __tablename__ = "coletas"

    id = Column(Integer, primary_key=True, index=True)
    site = Column(String(100), nullable=False)
    url = Column(String(500), nullable=False)
    html = Column(Text, nullable=False)
    tamanho_kb = Column(Float, default=0)
    data_criacao = Column(DateTime, default=datetime.datetime.now)

    # ⭐ Relacionamento com containers
    containers = relationship(
        "Container", back_populates="coleta", cascade="all, delete-orphan"
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
            "total_containers": len(self.containers) if self.containers else 0,
        }


class Container(Base):
    """
    ⭐ TABELA PRINCIPAL: Cada produto é um CONTAINER completo!
    Guarda o HTML + LISTA DE TODOS OS ELEMENTOS DENTRO
    """

    __tablename__ = "containers"

    id = Column(Integer, primary_key=True, index=True)
    coleta_id = Column(Integer, ForeignKey("coletas.id"), nullable=False)

    # ⭐ O CONTAINER INTEIRO
    container_html = Column(Text, nullable=True)
    seletor_container = Column(String(500), nullable=True)

    # ⭐ DADOS EXTRAÍDOS (para busca rápida)
    nome = Column(String(300), nullable=True)
    preco_texto = Column(String(50), nullable=True)
    preco_valor = Column(Float, nullable=True)
    link = Column(String(500), nullable=True)
    produto_id = Column(String(100), nullable=True)

    # ⭐ ⭐ ⭐ LISTA DE TODOS OS ELEMENTOS DENTRO DO CONTAINER ⭐ ⭐ ⭐
    elementos_json = Column(Text, nullable=True)  # LISTA COMPLETA

    data_criacao = Column(DateTime, default=datetime.datetime.now)

    # ⭐ Relacionamento com coleta
    coleta = relationship("Coleta", back_populates="containers")

    def get_elementos(self):
        """Retorna a lista de elementos dentro do container"""
        if self.elementos_json:
            return json.loads(self.elementos_json)
        return []

    def set_elementos(self, elementos: list):
        """Salva a lista de elementos como JSON"""
        self.elementos_json = json.dumps(elementos, ensure_ascii=False)

    def buscar_elemento_por_seletor(self, seletor: str):
        """Busca um elemento dentro do container pelo seletor"""
        for elem in self.get_elementos():
            if elem.get("seletor") == seletor:
                return elem
        return None

    def buscar_elemento_por_tag_classe(self, tag: str, classe: str):
        """Busca um elemento dentro do container por tag + classe"""
        for elem in self.get_elementos():
            if elem.get("tag") == tag and classe in elem.get("class", ""):
                return elem
        return None

    def buscar_elemento_por_texto(self, texto_parcial: str):
        """Busca um elemento dentro do container por parte do texto"""
        texto_parcial = texto_parcial.lower()
        for elem in self.get_elementos():
            if texto_parcial in elem.get("texto", "").lower():
                return elem
        return None

    def to_dict(self):
        elementos = self.get_elementos()
        return {
            "id": self.id,
            "nome": self.nome,
            "preco": self.preco_texto,
            "preco_valor": self.preco_valor,
            "seletor_container": self.seletor_container,
            "link": self.link,
            "produto_id": self.produto_id,
            "total_elementos": len(elementos),
            "elementos": elementos[:20] if elementos else [],
            "data": (
                self.data_criacao.strftime("%Y-%m-%d %H:%M:%S")
                if self.data_criacao
                else ""
            ),
        }
