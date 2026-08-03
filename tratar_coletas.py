"""
🧹 SCRIPT DE ENXUGAMENTO E TRATAMENTO DE COLETAS (Blindado contra NoneType)
"""

from core.database import SessionLocal
from core.models import Coleta, Produto
from core.destrinchador import Destrinchador


def processar_coletas_pendentes():
    print("=" * 60)
    print("🧹 INICIANDO TRATAMENTO DAS COLETAS DO BANCO (BLINDADO)")
    print("=" * 60)

    db = SessionLocal()
    try:
        coletas = db.query(Coleta).order_by(Coleta.id.desc()).all()
        print(f"📊 Total de coletas encontradas no SQLite: {len(coletas)}")

        if not coletas:
            print("⚠️ Nenhuma coleta encontrada para tratar.")
            return

        destrinchador = Destrinchador()
        total_produtos_salvos = 0

        for coleta in coletas:
            print(
                f"\n🔍 Processando Coleta ID #{coleta.id} | Site: {coleta.site} | URL: {coleta.url}"
            )

            if not coleta.html:
                print("   ⚠️ HTML vazio nesta coleta. Pulando...")
                continue

            # Extrai os produtos usando o HTML bruto salvo no banco
            produtos_extraidos = destrinchador.extrair_produtos(coleta.html, coleta.url)

            if not produtos_extraidos:
                print("   ⚠️ Nenhum produto extraído deste HTML.")
                continue

            contador_novos = 0
            for p in produtos_extraidos:
                # Garante que p não é None e é um dicionário
                if not p or not isinstance(p, dict):
                    continue

                nome_prod = str(p.get("nome") or "Produto sem nome")[:300]
                link_prod = str(p.get("link") or "")[:500]
                preco_texto = str(p.get("preco_texto") or "")
                preco_valor = p.get("preco_valor")
                seletor = str(p.get("seletor") or "")

                # Converte preco_valor para float se possível, senão None
                try:
                    preco_valor = (
                        float(preco_valor) if preco_valor is not None else None
                    )
                except (ValueError, TypeError):
                    preco_valor = None

                # Evita duplicatas checando se o produto já existe para esta coleta
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
                        seletor=seletor,
                        link=link_prod,
                    )
                    db.add(novo_produto)
                    contador_novos += 1

            db.commit()
            print(f"   ✅ {contador_novos} novos produtos salvos para esta coleta.")
            total_produtos_salvos += contador_novos

        print("\n" + "=" * 60)
        print(f"🎉 TRATAMENTO CONCLUÍDO COM SUCESSO!")
        print(f"📦 Total geral de produtos novos salvos: {total_produtos_salvos}")
        print("=" * 60)

    except Exception as e:
        db.rollback()
        print(f"❌ Erro crítico durante o tratamento: {e}")
        import traceback

        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    processar_coletas_pendentes()
