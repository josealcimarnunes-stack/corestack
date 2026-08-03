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
from core.hardware_scanner import get_hardware_info, escolher_modelo_ia
from core.license import validar_licenca_com_popup  # <--- ESSA É A QUE ABRE O POPUP


def verificar_ollama():
    """Verifica se Ollama está instalado"""
    try:
        resultado = subprocess.run(
            ["ollama", "--version"], capture_output=True, text=True, timeout=5
        )
        return resultado.returncode == 0
    except:
        return False


def instalar_ollama():
    """Instala Ollama automaticamente"""
    sistema = platform.system()
    print(f"🔄 Instalando Ollama no {sistema}...")

    if sistema == "Windows":
        url = "https://ollama.com/download/OllamaSetup.exe"
        arquivo = "OllamaSetup.exe"

        print("📥 Baixando Ollama...")
        response = requests.get(url, stream=True)
        with open(arquivo, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print("🚀 Executando instalador...")
        subprocess.run([arquivo, "/S"], shell=True)
        os.remove(arquivo)

    elif sistema in ["Linux", "Darwin"]:
        subprocess.run("curl -fsSL https://ollama.com/install.sh | sh", shell=True)

    else:
        print(f"❌ Sistema {sistema} não suportado!")
        return False

    time.sleep(5)
    subprocess.Popen(["ollama", "serve"], shell=True)
    time.sleep(3)
    print("✅ Ollama instalado!")
    return True


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
        print("⏳ Download em andamento...")
        return True
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


def instalar_tudo():
    """Fluxo completo de instalação"""
    print("=" * 60)
    print("🤖 WEBSTRUCT ANALYZER - INSTALAÇÃO AUTÔNOMA")
    print("=" * 60)

    # ⭐ 1. LICENÇA COM POPUP (AQUI ESTÁ A CORREÇÃO!)
    print("\n[1/4] 🔐 VERIFICANDO LICENÇA...")

    # 🔥 CHAMA A FUNÇÃO QUE ABRE O POPUP
    if not validar_licenca_com_popup():
        print("❌ Licença inválida. Sistema bloqueado.")
        sys.exit(1)

    # 2. Hardware
    print("\n[2/4] 🖥️ ESCANEANDO HARDWARE...")
    hardware = get_hardware_info()
    modelo = escolher_modelo_ia(hardware)

    # 3. Ollama
    print("\n[3/4] 🤖 VERIFICANDO OLLAMA...")
    if not verificar_ollama():
        print("⚠️ Ollama não encontrado. Instalando...")
        if not instalar_ollama():
            print("❌ Falha ao instalar Ollama")
            sys.exit(1)
    else:
        print("✅ Ollama já instalado")

    # 4. Modelo
    print("\n[4/4] 📥 BAIXANDO MODELO...")
    if not baixar_modelo(modelo):
        print("⚠️ Falha no download, tentando modelo leve...")
        if not baixar_modelo("gemma2:2b"):
            print("❌ Não foi possível baixar nenhum modelo")
            sys.exit(1)

    # Salva o modelo escolhido
    with open(".modelo_escolhido", "w") as f:
        f.write(modelo)

    print("\n" + "=" * 60)
    print("✅ INSTALAÇÃO CONCLUÍDA COM SUCESSO!")
    print(f"🤖 Modelo: {modelo}")
    print("🌐 Dashboard: http://127.0.0.1:5000")
    print("=" * 60)

    return modelo


if __name__ == "__main__":
    instalar_tudo()
