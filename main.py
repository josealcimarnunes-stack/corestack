"""
🚀 WEBSTRUCT ANALYZER PRO - Ponto de entrada principal
"""

import os
import sys
import time
from core.installer_autonomo import instalar_tudo
from flask import Flask, render_template, request, jsonify, redirect, url_for, Response
from core.database import (
    init_db,
    listar_coletas,
    salvar_coleta,
    obter_html_por_id,
    deletar_coleta,
)
from core.collector import coletar_html
from core.garimpeiro import destrinchar_e_salvar

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


@app.route("/")
def index():
    """Página principal do dashboard"""
    try:
        coletas = listar_coletas(20)

        coletas_formatadas = []
        for c in coletas:
            coletas_formatadas.append(
                {
                    "id": c.id,
                    "url": c.url,
                    "nome_site": c.site,  # ⭐ CORRIGIDO: site em vez de nome_site
                    "tamanho_kb": (
                        round(c.tamanho_kb, 2) if hasattr(c, "tamanho_kb") else 0
                    ),
                    "data": (
                        c.data_criacao.strftime("%Y-%m-%d %H:%M:%S")
                        if c.data_criacao
                        else ""
                    ),
                }
            )

        total_coletas = len(coletas)

        print(f"📊 Dashboard carregado: {total_coletas} coletas encontradas")
        for c in coletas_formatadas:
            print(f"   - #{c['id']} {c['nome_site']} - {c['url']}")

        return render_template(
            "index.html",
            coletas=coletas_formatadas,
            total_coletas=total_coletas,
            total_produtos=0,
            alertas_nao_lidos=0,
        )
    except Exception as e:
        print(f"❌ Erro ao carregar dashboard: {e}")
        import traceback

        traceback.print_exc()
        return render_template(
            "index.html",
            coletas=[],
            total_coletas=0,
            total_produtos=0,
            alertas_nao_lidos=0,
        )


@app.route("/coletar", methods=["POST"])
def coletar():
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

        site = url.split("//")[1].split("/")[0].replace("www.", "").split(".")[0]
        produtos = destrinchar_e_salvar(coleta_id, site)

        return jsonify(
            {"sucesso": True, "coleta_id": coleta_id, "produtos": len(produtos)}
        )

    except Exception as e:
        print(f"❌ Erro na coleta: {e}")
        import traceback

        traceback.print_exc()
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


@app.route("/deletar/<int:coleta_id>")
def deletar(coleta_id):
    deletar_coleta(coleta_id)
    return redirect(url_for("index"))


@app.route("/api/alertas", methods=["GET"])
def get_alertas():
    return jsonify({"alertas": []})


# ⭐ ⭐ ⭐ ROTA DA IA (AQUI, ANTES DO if __name__!) ⭐ ⭐ ⭐
@app.route("/ia/perguntar", methods=["POST"])
def ia_perguntar():
    """Rota para perguntar à IA"""
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


# ============================================
# PONTO DE ENTRADA
# ============================================
if __name__ == "__main__":
    print("\n🌐 Dashboard: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(host="127.0.0.1", port=5000, debug=False)
