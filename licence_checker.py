import socket
import json
import urllib.request
import sys
import time


def obter_nome_maquina():
    return socket.gethostname()


def verificar_licenca():
    hostname_atual = obter_nome_maquina()
    print(f"🔒 Verificando licença para a máquina: [{hostname_atual}]...")

    # Adicionamos o timestamp (?t=...) no final da URL para burlar o cache do GitHub
    url_com_bypass_cache = f"https://raw.githubusercontent.com/josealcimarnunes-stack/licencas-WEBSTRUCT_ANALYZER-/main/licencas.json?t={int(time.time())}"

    try:
        req = urllib.request.Request(
            url_com_bypass_cache, headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            conteudo = response.read().decode("utf-8")
            dados = json.loads(conteudo)

            if isinstance(dados, list):
                maquinas_autorizadas = dados
            elif isinstance(dados, dict):
                maquinas_autorizadas = dados.get("maquinas", dados.get("licencas", []))
            else:
                maquinas_autorizadas = []

            if hostname_atual in maquinas_autorizadas or "*" in maquinas_autorizadas:
                print("✅ Licença válida! Acesso liberado.")
                return True
            else:
                print(
                    f"❌ ACESSO NEGADO: A máquina '{hostname_atual}' não possui licença ativa."
                )
                return False

    except json.JSONDecodeError as e:
        print(
            f"⚠️ ERRO DE SINTAXE NO JSON: O arquivo no GitHub contém erro na linha {e.lineno}."
        )
        return False
    except Exception as e:
        print(f"⚠️ Erro ao validar licença remota: {e}")
        return False


if __name__ == "__main__":
    if not verificar_licenca():
        sys.exit(1)
