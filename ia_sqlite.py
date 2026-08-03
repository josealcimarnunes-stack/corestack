"""
🧠 IA + SQLITE - Pergunte ao seu banco de dados!
"""

import sqlite3
import subprocess
import json
import re
from core.database import DB_NAME


def obter_esquema_banco() -> str:
    """Retorna o esquema do banco em texto"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Pega todas as tabelas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tabelas = cursor.fetchall()

    esquema = "ESQUEMA DO BANCO DE DADOS:\n\n"

    for tabela in tabelas:
        nome = tabela[0]
        cursor.execute(f"PRAGMA table_info({nome})")
        colunas = cursor.fetchall()

        esquema += f"TABELA: {nome}\n"
        for col in colunas:
            esquema += f"  - {col[1]} ({col[2]})\n"
        esquema += "\n"

    conn.close()
    return esquema


def obter_dados_exemplo(limite: int = 5) -> str:
    """Pega alguns dados de exemplo do banco"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    dados = "DADOS DE EXEMPLO:\n\n"

    # Produtos
    try:
        cursor.execute(f"""
            SELECT nome_site, titulo, preco_texto, preco_valor, data_criacao
            FROM produtos
            ORDER BY id DESC
            LIMIT {limite}
        """)
        produtos = cursor.fetchall()

        dados += "ÚLTIMOS PRODUTOS:\n"
        for p in produtos:
            dados += f"  Site: {p[0]}, Produto: {p[1][:50]}, Preço: {p[2]}, Valor: {p[3]}, Data: {p[4]}\n"
    except:
        pass

    # Coletas
    try:
        cursor.execute(f"""
            SELECT id, url, nome_site, data_criacao
            FROM coletas
            ORDER BY id DESC
            LIMIT {limite}
        """)
        coletas = cursor.fetchall()

        dados += "\nÚLTIMAS COLETAS:\n"
        for c in coletas:
            dados += f"  ID: {c[0]}, Site: {c[2]}, URL: {c[1][:60]}, Data: {c[3]}\n"
    except:
        pass

    conn.close()
    return dados


def perguntar_ia(pergunta: str, modelo: str = "llama3.2") -> str:
    """
    Faz uma pergunta para a IA sobre os dados do banco
    """
    print(f"\n🧠 Pergunta: {pergunta}")

    # 1. Pega o esquema e dados
    esquema = obter_esquema_banco()
    dados = obter_dados_exemplo()

    # 2. Monta o prompt
    prompt = f"""
Você é um assistente especializado em análise de dados de e-commerce.
Você tem acesso a um banco SQLite com dados de produtos e coletas.

{esquema}

{dados}

Responda APENAS com base nos dados fornecidos.
Se não souber, diga "Não encontrei essa informação no banco de dados."

Pergunta do usuário: {pergunta}

Resposta:"""

    print("⏳ Consultando IA...")

    # 3. Chama o Ollama
    try:
        resultado = subprocess.run(
            ["ollama", "run", modelo, prompt],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if resultado.returncode == 0:
            resposta = resultado.stdout.strip()
            print(f"✅ Resposta: {resposta[:200]}...")
            return resposta
        else:
            return f"❌ Erro na IA: {resultado.stderr}"

    except subprocess.TimeoutExpired:
        return "⏳ A consulta demorou muito. Tente uma pergunta mais simples."
    except Exception as e:
        return f"❌ Erro ao consultar IA: {e}"


def perguntar_sobre_precos(produto: str = None) -> str:
    """Pergunta específica sobre preços"""
    if produto:
        return perguntar_ia(
            f"Qual foi a variação de preço do '{produto}' nos últimos dias?"
        )
    else:
        return perguntar_ia("Quais produtos tiveram maior variação de preço?")


def perguntar_sobre_coletas() -> str:
    """Pergunta sobre as coletas"""
    return perguntar_ia("Quantas páginas foram coletadas e de quais sites?")


# ============================================
# CLI - CHAT COM A IA
# ============================================


def chat():
    """Modo chat interativo com a IA"""
    print("=" * 60)
    print("🧠 CHAT COM IA - Pergunte sobre seus dados")
    print("=" * 60)
    print("\nDigite 'sair' para encerrar.")
    print("Exemplo: 'Qual foi o preço mais alto?'")
    print("Exemplo: 'Quantos produtos foram coletados?'")
    print("Exemplo: 'Mostre os produtos mais caros'\n")

    while True:
        pergunta = input("❓ Você: ").strip()

        if pergunta.lower() in ["sair", "exit", "quit"]:
            print("👋 Até logo!")
            break

        if not pergunta:
            continue

        resposta = perguntar_ia(pergunta)
        print(f"\n🤖 IA: {resposta}\n")


if __name__ == "__main__":
    chat()
