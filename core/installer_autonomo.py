"""
🤖 INSTALADOR AUTÔNOMO - WebStruct Analyzer
Gerencia licença, hardware e instalação da IA
"""

import os
import sys
import time
import subprocess
import platform
import requests
import urllib.request  # ⭐ ADICIONADO!
from core.hardware_scanner import get_hardware_info, mostrar_diagnostico
from core.license import validar_licenca_com_popup


def verificar_ollama():
    """Verifica se Ollama está instalado"""
    try:
        resultado = subprocess.run(
            ["ollama", "--version"], capture_output=True, text=True, timeout=5
        )
        return resultado.returncode == 0
    except:
        return False


def instalar_ollama_windows():
    """Instala Ollama no Windows (USANDO O MESMO MÉTODO DO INICIAR_SISTEMA.PY)"""
    import tempfile

    print("📥 Baixando Ollama para Windows...")
    url = "https://ollama.com/download/OllamaSetup.exe"

    temp_dir = tempfile.gettempdir()
    caminho_instalador = os.path.join(temp_dir, "OllamaSetup.exe")

    try:
        urllib.request.urlretrieve(url, caminho_instalador)
        print("✅ Download concluído!")
    except Exception as e:
        print(f"❌ Erro ao baixar: {e}")
        return False

    print("🚀 Instalando Ollama em segundo plano...")
    try:
        subprocess.run(
            [
                caminho_instalador,
                "/VERYSILENT",
                "/SUPPRESSMSGBOXES",
                "/NORESTART",
                "/SP-",
            ],
            check=True,
            timeout=180,
        )

        if os.path.exists(caminho_instalador):
            os.remove(caminho_instalador)

        time.sleep(5)

        if verificar_ollama():
            print("✅ Ollama instalado com sucesso!")
            return True
        else:
            print("⚠️ Ollama pode estar instalando em segundo plano...")
            return True

    except Exception as e:
        print(f"❌ Erro na instalação: {e}")
        return False


def instalar_ollama_linux():
    """Instala Ollama no Linux"""
    print("🔄 Instalando Ollama no Linux...")
    try:
        subprocess.run(
            "curl -fsSL https://ollama.com/install.sh | sh", shell=True, timeout=180
        )
        print("✅ Ollama instalado!")
        return True
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


def instalar_ollama_mac():
    """Instala Ollama no Mac"""
    print("🔄 Instalando Ollama no Mac...")
    try:
        subprocess.run(
            "curl -fsSL https://ollama.com/install.sh | sh", shell=True, timeout=180
        )
        print("✅ Ollama instalado!")
        return True
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


def instalar_ollama():
    """Instala Ollama automaticamente (detecta SO)"""
    sistema = platform.system()
    print(f"🔄 Instalando Ollama no {sistema}...")

    if sistema == "Windows":
        return instalar_ollama_windows()
    elif sistema == "Linux":
        return instalar_ollama_linux()
    elif sistema == "Darwin":
        return instalar_ollama_mac()
    else:
        print(f"❌ Sistema {sistema} não suportado!")
        return False


def baixar_modelo(modelo: str):
    """Baixa o modelo de IA escolhido"""
    print(f"\n📥 Baixando modelo {modelo}...")
    print("⏳ Isso pode levar alguns minutos...")

    try:
        resultado = subprocess.run(
            ["ollama", "pull", modelo], capture_output=True, text=True, timeout=600
        )
        if resultado.returncode == 0:
            print(f"✅ Modelo {modelo} instalado!")
            return True
        else:
            print(f"❌ Erro: {resultado.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("⏳ Download em andamento em segundo plano...")
        return True
    except Exception as e:
        print(f"❌ Erro ao baixar modelo: {e}")
        return False


def instalar_tudo():
    """Fluxo completo de instalação (totalmente automático)"""
    print("=" * 60)
    print("🤖 WEBSTRUCT ANALYZER - INSTALAÇÃO AUTÔNOMA")
    print("=" * 60)

    print("\n[1/4] 🔐 VERIFICANDO LICENÇA...")
    if not validar_licenca_com_popup():
        print("❌ Licença inválida. Sistema bloqueado.")
        sys.exit(1)

    print("\n[2/4] 🖥️ ESCANEANDO HARDWARE...")
    hardware = get_hardware_info()
    classificacao = mostrar_diagnostico(hardware)
    modelo = classificacao["modelo_sugerido"]

    print("\n[3/4] 🤖 VERIFICANDO OLLAMA...")
    if not verificar_ollama():
        print("⚠️ Ollama não encontrado. Instalando automaticamente...")
        if not instalar_ollama():
            print("❌ Falha ao instalar Ollama")
            sys.exit(1)
        if not verificar_ollama():
            print("⚠️ Ollama pode estar instalando. Continuando...")
    else:
        print("✅ Ollama já está instalado")

    print("\n[4/4] 📥 BAIXANDO MODELO...")
    if not baixar_modelo(modelo):
        print(f"⚠️ Falha ao baixar {modelo}, tentando modelo leve...")
        if not baixar_modelo("gemma2:2b"):
            print("❌ Não foi possível baixar nenhum modelo")
            sys.exit(1)

    with open(".modelo_escolhido", "w", encoding="utf-8") as f:
        f.write(modelo)

    print("\n🧪 Testando IA...")
    try:
        import requests

        payload = {
            "model": modelo,
            "prompt": "Diga 'Olá! Estou pronta!' em português",
            "stream": False,
        }
        response = requests.post(
            "http://localhost:11434/api/generate", json=payload, timeout=30
        )
        if response.status_code == 200:
            resposta = response.json().get("response", "")
            print(f"🤖 IA diz: {resposta}")
        else:
            print(f"⚠️ IA instalada, mas não respondeu ao teste.")
    except Exception as e:
        print(f"⚠️ Teste da IA falhou: {e}")

    print("\n" + "=" * 60)
    print("✅ INSTALAÇÃO CONCLUÍDA!")
    print(f"🤖 Modelo: {modelo}")
    print(f"📊 Classificação: {classificacao['classe']}")
    print("🌐 Dashboard: http://127.0.0.1:5000")
    print("=" * 60)

    return modelo


if __name__ == "__main__":
    instalar_tudo()
