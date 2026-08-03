"""
🤖 INSTALADOR AUTOMÁTICO - Ollama + IA
Verifica licença e instala Ollama se necessário
"""

import os
import sys
import subprocess
import platform
import requests
import json
from licence_checker import verificar_licenca


def verificar_ollama_instalado() -> bool:
    """Verifica se o Ollama está instalado"""
    try:
        resultado = subprocess.run(
            ["ollama", "--version"], capture_output=True, text=True, timeout=5
        )
        return resultado.returncode == 0
    except:
        return False


def instalar_ollama_windows():
    """Instala Ollama no Windows"""
    print("🔄 Baixando Ollama para Windows...")
    url = "https://ollama.com/download/OllamaSetup.exe"
    arquivo = "OllamaSetup.exe"

    # Baixa o instalador
    response = requests.get(url, stream=True)
    with open(arquivo, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    print("🚀 Executando instalador...")
    subprocess.run([arquivo, "/S"], shell=True)  # /S = instalação silenciosa
    os.remove(arquivo)
    print("✅ Ollama instalado!")


def instalar_ollama_linux():
    """Instala Ollama no Linux"""
    print("🔄 Instalando Ollama no Linux...")
    subprocess.run("curl -fsSL https://ollama.com/install.sh | sh", shell=True)
    print("✅ Ollama instalado!")


def instalar_ollama_mac():
    """Instala Ollama no Mac"""
    print("🔄 Instalando Ollama no Mac...")
    subprocess.run("curl -fsSL https://ollama.com/install.sh | sh", shell=True)
    print("✅ Ollama instalado!")


def baixar_modelo_ia(modelo: str = "llama3.2"):
    """Baixa o modelo de IA do Ollama"""
    print(f"🔄 Baixando modelo {modelo}... (pode levar alguns minutos)")

    try:
        subprocess.run(
            ["ollama", "pull", modelo],
            capture_output=True,
            text=True,
            timeout=600,  # 10 minutos
        )
        print(f"✅ Modelo {modelo} baixado com sucesso!")
        return True
    except subprocess.TimeoutExpired:
        print("⏳ O download está demorando mais que o esperado...")
        return False
    except Exception as e:
        print(f"❌ Erro ao baixar modelo: {e}")
        return False


def instalar_ia_autonomo():
    """
    Instalação autônoma: verifica licença, instala Ollama e baixa modelo
    """
    print("=" * 60)
    print("🤖 INSTALADOR AUTÔNOMO - IA LOCAL")
    print("=" * 60)

    # 1. VERIFICA LICENÇA
    if not verificar_licenca():
        print("❌ Licença inválida! Instalação cancelada.")
        return False

    print("✅ Licença verificada!")

    # 2. VERIFICA OLLAMA
    if verificar_ollama_instalado():
        print("✅ Ollama já está instalado!")
    else:
        print("⚠️ Ollama não encontrado. Instalando...")
        sistema = platform.system()

        if sistema == "Windows":
            instalar_ollama_windows()
        elif sistema == "Linux":
            instalar_ollama_linux()
        elif sistema == "Darwin":
            instalar_ollama_mac()
        else:
            print("❌ Sistema não suportado!")
            return False

    # 3. ESCOLHE O MODELO
    modelos = [
        "llama3.2",  # 3B, rápido, português
        "mistral",  # 7B, bom em geral
        "phi3",  # 3.8B, eficiente
    ]

    print("\n📋 Modelos disponíveis:")
    for i, m in enumerate(modelos):
        print(f"  {i+1}. {m}")

    print("\n🔄 Baixando modelo padrão: llama3.2...")

    if not baixar_modelo_ia("llama3.2"):
        print("⚠️ Falha ao baixar llama3.2, tentando mistral...")
        if not baixar_modelo_ia("mistral"):
            print("❌ Falha ao baixar modelo. Tente manualmente:")
            print("   ollama pull llama3.2")
            return False

    print("\n✅ INSTALAÇÃO CONCLUÍDA COM SUCESSO!")
    print("🤖 IA pronta para usar!")
    return True


if __name__ == "__main__":
    instalar_ia_autonomo()
