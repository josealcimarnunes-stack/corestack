"""
🚀 WEBSTRUCT ANALYZER PRO - Ponto de entrada principal
COM DESTRINCHADOR E ESTEIRA INTEGRados
"""

import os
import sys
import time
from flask import Flask, render_template, request, jsonify, redirect, url_for, Response
from sqlalchemy import func
from core.installer_autonomo import instalar_tudo
from core.database import (
    init_db,
    listar_coletas,
    salvar_coleta,
    obter_html_por_id,
    deletar_coleta,
    contar_produtos,
    SessionLocal,
)
from core.collector import coletar_html
from core.destrinchador import Destrinchador
from core.models import Coleta, Produto

# ============================================
# 1. ⭐ EXECUTA A INSTALAÇÃO AUTÔNOMA (LICENÇA + IA)
# ============================================
print("\n" + "=" * 60)
print("🚀 WEBSTRUCT ANALYZER PRO")
print("=" * 60)

modelo_escolhido = instalar_tudo()

print(f"\n✅ Sistema liberado! IA carregada: {modelo_escolhido}")

# ============================================
# 1.5 ⭐ INICIALIZA O BANCO DE DADOS
# ============================================
print("\n📦 Inicializando banco de dados...")
init_db()
print("✅ Banco de dados pronto!")

# ============================================
# 2. INICIA O FLASK (DASHBOARD)
# ============================================
app = Flask(__name__)


@app.route("/processar-esteira", methods=["POST"])
def processar_esteira():
    try:
        print("\n⚡ Processando esteira de tratamento...")
        db = SessionLocal()
        try:
            coletas = (
                db.query(Coleta)
                .outerjoin(Produto)
                .group_by(Coleta.id)
                .having(
                    func.count(Produto.id) == 0
                )  # <--- Alterado de db.func para func
                .all()
            )

            destrinchador = Destrinchador()
            total_produtos = 0
            for coleta in coletas:
                produtos = destrinchador.extrair_produtos(coleta.html, coleta.url)
                for p in produtos:
                    produto = Produto(
                        coleta_id=coleta.id,
                        nome=p.get("nome", "")[:300],
                        preco_texto=p.get("preco_texto", ""),
                        preco_valor=p.get("preco_valor"),
                        seletor=p.get("seletor", ""),
                        link=p.get("link", "")[:500],
                        imagem=p.get("imagem", "")[:500],
                    )
                    db.add(produto)
                db.commit()
                total_produtos += len(produtos)

            print(f"✅ Esteira finalizada! {total_produtos} produtos processados.")
        finally:
            db.close()
    except Exception as e:
        print(f"❌ Erro na esteira: {e}")

    return redirect(url_for("index"))


@app.route("/")
def index():
    """Página principal do dashboard"""
    try:
        coletas = listar_coletas(20)
        total_produtos = contar_produtos()

        coletas_formatadas = []
        for c in coletas:
            db = SessionLocal()
            try:
                qtd_produtos = (
                    db.query(Produto).filter(Produto.coleta_id == c.id).count()
                )
            finally:
                db.close()

            coletas_formatadas.append(
                {
                    "id": c.id,
                    "url": c.url,
                    "nome_site": c.site,
                    "tamanho_kb": (
                        round(c.tamanho_kb, 2) if hasattr(c, "tamanho_kb") else 0
                    ),
                    "data": (
                        c.data_criacao.strftime("%Y-%m-%d %H:%M:%S")
                        if c.data_criacao
                        else ""
                    ),
                    "total_produtos": qtd_produtos,
                }
            )

        return render_template(
            "index.html",
            coletas=coletas_formatadas,
            total_coletas=len(coletas),
            total_produtos=total_produtos,
            alertas_nao_lidos=0,
        )
    except Exception as e:
        print(f"❌ Erro: {e}")
        return render_template(
            "index.html",
            coletas=[],
            total_coletas=0,
            total_produtos=0,
            alertas_nao_lidos=0,
        )


@app.route("/coletar", methods=["POST"])
def coletar():
    """Coleta uma URL e extrai produtos"""
    url = request.form.get("url")
    if not url:
        return jsonify({"erro": "URL inválida"}), 400

    try:
        print(f"\n📥 Coletando: {url}")
        html = coletar_html(url)
        if not html:
            return jsonify({"erro": "Falha ao capturar HTML"}), 500

        coleta_id = salvar_coleta(url, html)
        print(f"✅ Coleta salva com ID: {coleta_id}")

        total = 0
        try:
            destrinchador = Destrinchador()
            produtos = destrinchador.extrair_produtos(html, url)

            db = SessionLocal()
            try:
                for p in produtos:
                    produto = Produto(
                        coleta_id=coleta_id,
                        nome=p.get("nome", "")[:300],
                        preco_texto=p.get("preco_texto", ""),
                        preco_valor=p.get("preco_valor"),
                        seletor=p.get("seletor", ""),
                        link=p.get("link", "")[:500],
                        imagem=p.get("imagem", "")[:500],
                    )
                    db.add(produto)
                db.commit()
                total = len(produtos)
                print(f"✅ {total} produtos extraídos e salvos!")
            finally:
                db.close()

        except Exception as e:
            print(f"⚠️ Erro na extração: {e}")

        return jsonify({"sucesso": True, "coleta_id": coleta_id, "produtos": total})

    except Exception as e:
        print(f"❌ Erro na coleta: {e}")
        return jsonify({"erro": str(e)}), 500


@app.route("/destrinchar", methods=["POST"])
def destrinchar_todas():
    try:
        print("\n🔍 Iniciando destrinchamento em massa...")
        db = SessionLocal()
        try:
            coletas = (
                db.query(Coleta)
                .outerjoin(Produto)
                .group_by(Coleta.id)
                .having(db.func.count(Produto.id) == 0)
                .all()
            )

            if not coletas:
                return jsonify(
                    {
                        "sucesso": True,
                        "mensagem": "Todas as coletas já foram processadas!",
                        "total": 0,
                    }
                )

            destrinchador = Destrinchador()
            total_produtos = 0
            processadas = []

            for coleta in coletas:
                produtos = destrinchador.extrair_produtos(coleta.html, coleta.url)

                for p in produtos:
                    produto = Produto(
                        coleta_id=coleta.id,
                        nome=p.get("nome", "")[:300],
                        preco_texto=p.get("preco_texto", ""),
                        preco_valor=p.get("preco_valor"),
                        seletor=p.get("seletor", ""),
                        link=p.get("link", "")[:500],
                        imagem=p.get("imagem", "")[:500],
                    )
                    db.add(produto)

                db.commit()
                total_produtos += len(produtos)
                processadas.append(
                    {
                        "coleta_id": coleta.id,
                        "site": coleta.site,
                        "produtos": len(produtos),
                    }
                )

            return jsonify(
                {
                    "sucesso": True,
                    "total_coletas": len(coletas),
                    "total_produtos": total_produtos,
                    "detalhes": processadas,
                }
            )
        finally:
            db.close()
    except Exception as e:
        print(f"❌ Erro no destrinchamento: {e}")
        return jsonify({"erro": str(e)}), 500


@app.route("/destrinchar/<int:coleta_id>", methods=["POST"])
def destrinchar_especifica(coleta_id):
    try:
        db = SessionLocal()
        try:
            coleta = db.query(Coleta).filter(Coleta.id == coleta_id).first()
            if not coleta:
                return jsonify({"erro": "Coleta não encontrada"}), 404

            db.query(Produto).filter(Produto.coleta_id == coleta_id).delete()

            destrinchador = Destrinchador()
            produtos = destrinchador.extrair_produtos(coleta.html, coleta.url)

            for p in produtos:
                produto = Produto(
                    coleta_id=coleta_id,
                    nome=p.get("nome", "")[:300],
                    preco_texto=p.get("preco_texto", ""),
                    preco_valor=p.get("preco_valor"),
                    seletor=p.get("seletor", ""),
                    link=p.get("link", "")[:500],
                    imagem=p.get("imagem", "")[:500],
                )
                db.add(produto)

            db.commit()

            return jsonify(
                {
                    "sucesso": True,
                    "coleta_id": coleta_id,
                    "site": coleta.site,
                    "produtos": len(produtos),
                }
            )
        finally:
            db.close()
    except Exception as e:
        print(f"❌ Erro: {e}")
        return jsonify({"erro": str(e)}), 500


@app.route("/ver/renderizado/<int:coleta_id>")
def ver_renderizado(coleta_id):
    resultado = obter_html_por_id(coleta_id)
    if resultado:
        return Response(resultado[0], mimetype="text/html")
    return "Coleta não encontrada", 404


@app.route("/ver/codigo/<int:coleta_id>")
def ver_codigo(coleta_id):
    resultado = obter_html_por_id(coleta_id)
    if resultado:
        return Response(resultado[0], mimetype="text/plain")
    return "Coleta não encontrada", 404


@app.route("/ver/produtos/<int:coleta_id>")
def ver_produtos(coleta_id):
    db = SessionLocal()
    try:
        produtos = db.query(Produto).filter(Produto.coleta_id == coleta_id).all()
        if not produtos:
            return jsonify({"mensagem": "Nenhum produto encontrado"}), 404

        return jsonify(
            {
                "coleta_id": coleta_id,
                "total": len(produtos),
                "produtos": [
                    {
                        "id": p.id,
                        "nome": p.nome,
                        "preco_texto": p.preco_texto,
                        "preco_valor": p.preco_valor,
                        "link": p.link,
                        "imagem": p.imagem,
                        "seletor": p.seletor,
                    }
                    for p in produtos
                ],
            }
        )
    finally:
        db.close()


@app.route("/deletar/<int:coleta_id>")
def deletar(coleta_id):
    deletar_coleta(coleta_id)
    return redirect(url_for("index"))


@app.route("/ia/perguntar", methods=["POST"])
def ia_perguntar():
    try:
        data = request.get_json() or {}
        pergunta = data.get("pergunta", "")
        if not pergunta:
            return jsonify({"erro": "Pergunta vazia"}), 400

        from core.ia_ollama import falar_com_ia

        resposta = falar_com_ia(pergunta)

        return jsonify({"sucesso": True, "pergunta": pergunta, "resposta": resposta})
    except Exception as e:
        print(f"❌ Erro na IA: {e}")
        return jsonify({"erro": str(e)}), 500


@app.route("/api/alertas", methods=["GET"])
def get_alertas():
    return jsonify({"alertas": []})


# ============================================
# PONTO DE ENTRADA
# ============================================
if __name__ == "__main__":
    print("\n🌐 Dashboard: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(host="127.0.0.1", port=5000, debug=False)
