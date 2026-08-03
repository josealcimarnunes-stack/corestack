"""
⚙️ CAMADA DE SERVIÇOS (A Esteira Automática)
Gerencia o processamento das coletas para uso no Flask.
"""

from core.database import SessionLocal
from core.models import Coleta, Produto
from core.destrinchador import Destrinchador


def executar_esteira_tratamento():
    """Varre o banco, destrincha coletas pendentes e salva na tabela de produtos."""
    db = SessionLocal()
    total_novos = 0
    try:
        coletas = db.query(Coleta).order_by(Coleta.id.desc()).all()
        destrinchador = Destrinchador()

        for coleta in coletas:
            if not coleta.html:
                continue

            produtos_extraidos = destrinchador.extrair_produtos(coleta.html, coleta.url)
            if not produtos_extraidos:
                continue

            for p in produtos_extraidos:
                if not p or not isinstance(p, dict):
                    continue

                nome_prod = str(p.get("nome") or "Produto sem nome")[:300]
                link_prod = str(p.get("link") or "")[:500]
                preco_texto = str(p.get("preco_texto") or "")
                seletor_html = str(p.get("seletor") or "")

                preco_valor = p.get("preco_valor")
                try:
                    preco_valor = (
                        float(preco_valor) if preco_valor is not None else None
                    )
                except (ValueError, TypeError):
                    preco_valor = None

                # Evita duplicidade por coleta e nome do produto
                existente = (
                    db.query(Produto)
                    .filter(
                        Produto.coleta_id == coleta.id,
                        Produto.nome == nome_prod,
                    )
                    .first()
                )

                if not existente:
                    novo_produto = Produto(
                        coleta_id=coleta.id,
                        nome=nome_prod,
                        preco_texto=preco_texto,
                        preco_valor=preco_valor,
                        seletor=seletor_html,
                        link=link_prod,
                    )
                    db.add(novo_produto)
                    total_novos += 1

        db.commit()
        return {
            "status": "sucesso",
            "novos_produtos": total_novos,
            "mensagem": f"Esteira executada com sucesso! {total_novos} itens processados.",
        }
    except Exception as e:
        db.rollback()
        return {"status": "erro", "mensagem": str(e)}
    finally:
        db.close()
