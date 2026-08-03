import requests
import json
from core.database import listar_coletas

OLLAMA_URL = "http://localhost:11434/api/generate"
MODELO_OLLAMA = "gemma2:9b"


def obter_contexto_produtos() -> str:
    """
    Busca os produtos do banco e monta um contexto para a IA
    """
    coletas = listar_coletas(10)  # Últimas 10 coletas
    if not coletas:
        return "Nenhum produto foi coletado ainda."

    contexto = "AQUI ESTÃO OS PRODUTOS COLETADOS:\n\n"

    for coleta in coletas:
        contexto += f"📦 COLETA #{coleta.id} - {coleta.site} - {coleta.url}\n"
        contexto += f"   Data: {coleta.data_criacao.strftime('%Y-%m-%d %H:%M')}\n"
        contexto += f"   Tamanho: {coleta.tamanho_kb} KB\n"

        # Se tiver produtos extraídos (futuro)
        if hasattr(coleta, "produtos_json") and coleta.produtos_json:
            try:
                produtos = json.loads(coleta.produtos_json)
                if produtos:
                    contexto += f"   Produtos encontrados: {len(produtos)}\n"
                    for p in produtos[:5]:
                        nome = p.get("nome", "N/A")
                        preco = p.get("preco_texto", "N/A")
                        contexto += f"      - {nome}: {preco}\n"
            except:
                pass

        contexto += "\n"

    return contexto


def falar_com_ia(prompt_usuario: str) -> str:
    """
    Envia um prompt para a IA com o contexto do banco
    """
    # ⭐ 1. Pega o contexto do banco
    contexto = obter_contexto_produtos()

    # ⭐ 2. Monta o prompt completo
    prompt_completo = f"""
Você é um assistente especializado em análise de dados de e-commerce.
Você tem acesso aos seguintes dados coletados:

{contexto}

Responda APENAS com base nos dados fornecidos.
Se não souber, diga "Não encontrei essa informação no banco de dados."
Seja direto e objetivo.

Pergunta do usuário: {prompt_usuario}

Resposta:"""

    # ⭐ 3. Envia para a IA
    payload = {
        "model": MODELO_OLLAMA,
        "prompt": prompt_completo,
        "stream": False,
        "options": {"temperature": 0.7, "num_ctx": 4096},
    }

    try:
        print(f"🧠 Enviando pergunta para IA: {prompt_usuario[:50]}...")
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)

        if response.status_code == 200:
            resposta = response.json().get("response", "Erro: Resposta vazia.")
            print(f"✅ IA respondeu: {resposta[:100]}...")
            return resposta
        else:
            return f"❌ Erro na IA: Status {response.status_code}"

    except requests.exceptions.ConnectionError:
        return "❌ Erro: Ollama não está rodando. Execute 'ollama serve'."
    except requests.exceptions.Timeout:
        return "⏳ A IA demorou muito para responder. Tente novamente."
    except Exception as e:
        return f"❌ Erro ao consultar IA: {str(e)}"
