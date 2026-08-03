"""
🖥️ HARDWARE SCANNER - Detecta placa de vídeo, RAM, processador
"""

import platform
import subprocess
import re
import os


def get_hardware_info():
    """Coleta informações do hardware do usuário"""
    info = {
        "sistema": platform.system(),
        "ram_gb": 0,
        "cpu": "",
        "cpu_cores": 0,
        "gpu": "",
        "has_gpu": False,
        "gpu_memory": 0,
    }

    sistema = info["sistema"]

    if sistema == "Windows":
        info = _detectar_windows(info)
    elif sistema == "Linux":
        info = _detectar_linux(info)
    elif sistema == "Darwin":
        info = _detectar_mac(info)

    # ⭐ SE NÃO DETECTOU NADA, USA FALLBACK
    if info["ram_gb"] == 0:
        info["ram_gb"] = 8  # Fallback seguro
        print("⚠️ Não foi possível detectar a RAM. Usando fallback: 8 GB")

    if info["cpu_cores"] == 0:
        info["cpu_cores"] = 4
        print("⚠️ Não foi possível detectar os núcleos. Usando fallback: 4")

    return info


def _detectar_windows(info):
    """Detecta hardware no Windows usando múltiplas estratégias"""

    # ⭐ ESTRATÉGIA 1: wmi (se estiver instalado)
    try:
        import wmi

        w = wmi.WMI()

        for ram in w.Win32_ComputerSystem():
            if ram.TotalPhysicalMemory:
                info["ram_gb"] = round(int(ram.TotalPhysicalMemory) / (1024**3), 1)

        for cpu in w.Win32_Processor():
            if cpu.Name:
                info["cpu"] = cpu.Name
            if cpu.NumberOfCores:
                info["cpu_cores"] = cpu.NumberOfCores

        for gpu in w.Win32_VideoController():
            if gpu.Name and "Microsoft" not in gpu.Name:
                info["gpu"] = gpu.Name
                info["has_gpu"] = True
                if hasattr(gpu, "AdapterRAM") and gpu.AdapterRAM:
                    info["gpu_memory"] = round(gpu.AdapterRAM / (1024**3), 1)
                break

        if info["ram_gb"] > 0:
            return info
    except:
        pass

    # ⭐ ESTRATÉGIA 2: WMIC (comando nativo do Windows)
    try:
        # RAM
        result = subprocess.run(
            ["wmic", "memorychip", "get", "Capacity"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        for linha in result.stdout.splitlines():
            if linha.strip().isdigit():
                info["ram_gb"] = round(int(linha) / (1024**3), 1)
                break

        # CPU
        result = subprocess.run(
            ["wmic", "cpu", "get", "Name,NumberOfCores"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        linhas = result.stdout.splitlines()
        if len(linhas) >= 2:
            partes = linhas[1].split()
            if partes:
                info["cpu"] = " ".join(partes[:-1]) if len(partes) > 1 else partes[0]
                if len(partes) > 0:
                    try:
                        info["cpu_cores"] = int(partes[-1])
                    except:
                        pass

        # GPU
        result = subprocess.run(
            ["wmic", "path", "win32_videocontroller", "get", "name"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        for linha in result.stdout.splitlines():
            linha = linha.strip()
            if linha and "Microsoft" not in linha and "Video Controller" not in linha:
                info["gpu"] = linha
                info["has_gpu"] = True
                break

        if info["ram_gb"] > 0:
            return info
    except:
        pass

    # ⭐ ESTRATÉGIA 3: systeminfo (fallback)
    try:
        result = subprocess.run(
            ["systeminfo"], capture_output=True, text=True, timeout=10
        )
        for linha in result.stdout.splitlines():
            if "Memória Física" in linha or "Physical Memory" in linha:
                partes = re.findall(r"[\d,.]+", linha)
                if partes:
                    info["ram_gb"] = round(float(partes[0].replace(",", ".")), 1)
                    break
    except:
        pass

    return info


def _detectar_linux(info):
    """Detecta hardware no Linux"""
    try:
        with open("/proc/meminfo", "r") as f:
            for linha in f:
                if "MemTotal" in linha:
                    kb = int(re.search(r"\d+", linha).group())
                    info["ram_gb"] = round(kb / (1024**2), 1)
                    break
    except:
        pass

    try:
        result = subprocess.run(["lscpu"], capture_output=True, text=True)
        for linha in result.stdout.splitlines():
            if "Model name" in linha:
                info["cpu"] = linha.split(":")[1].strip()
            if "CPU(s)" in linha and ":" in linha:
                info["cpu_cores"] = int(linha.split(":")[1].strip())
    except:
        pass

    try:
        result = subprocess.run(["lspci", "-nn"], capture_output=True, text=True)
        for linha in result.stdout.splitlines():
            if "VGA" in linha or "3D" in linha:
                info["gpu"] = linha
                info["has_gpu"] = True
                break
    except:
        pass

    return info


def _detectar_mac(info):
    """Detecta hardware no Mac"""
    try:
        result = subprocess.run(
            ["sysctl", "-n", "hw.memsize"], capture_output=True, text=True
        )
        bytes_ram = int(result.stdout.strip())
        info["ram_gb"] = round(bytes_ram / (1024**3), 1)
    except:
        pass

    try:
        result = subprocess.run(
            ["sysctl", "-n", "machdep.cpu.brand_string"], capture_output=True, text=True
        )
        info["cpu"] = result.stdout.strip()
    except:
        pass

    try:
        result = subprocess.run(
            ["sysctl", "-n", "hw.ncpu"], capture_output=True, text=True
        )
        info["cpu_cores"] = int(result.stdout.strip())
    except:
        pass

    try:
        result = subprocess.run(
            ["system_profiler", "SPDisplaysDataType"], capture_output=True, text=True
        )
        if "Chipset Model" in result.stdout:
            info["has_gpu"] = True
            for linha in result.stdout.splitlines():
                if "Chipset Model" in linha:
                    info["gpu"] = linha.split(":")[1].strip()
                    break
    except:
        pass

    return info


def classificar_pc(hardware):
    """Classifica o PC e retorna uma mensagem personalizada"""
    ram = hardware.get("ram_gb", 0)
    has_gpu = hardware.get("has_gpu", False)
    cores = hardware.get("cpu_cores", 0)

    if ram >= 32 and has_gpu and cores >= 8:
        classe = "🚀 PC NAVE DA GALÁXIA!"
        mensagem = "Caramba! Esse PC é uma máquina de guerra! Vai rodar TUDO no máximo!"
        icone = "🚀"
        modelo_sugerido = "llama3.2:latest"

    elif ram >= 16 and has_gpu and cores >= 6:
        classe = "⚡ PC Top de Linha!"
        mensagem = "PC brabo! Vai rodar a IA com folga e ainda sobra potência!"
        icone = "⚡"
        modelo_sugerido = "gemma2:9b"

    elif ram >= 12 and cores >= 4:
        classe = "💪 PC Médio"
        mensagem = "PC equilibrado! Vai rodar a IA tranquilo, sem sufoco."
        icone = "💪"
        modelo_sugerido = "gemma2:2b"

    elif ram >= 8 and cores >= 2:
        classe = "🖥️ PC Legal"
        mensagem = "PC honesto! Vai rodar a IA levinha sem problemas."
        icone = "🖥️"
        modelo_sugerido = "gemma2:2b"

    else:
        classe = "🔄 PC Básico"
        mensagem = "PC mais simples, mas dá conta do recado com a IA leve!"
        icone = "🔄"
        modelo_sugerido = "gemma2:2b"

    return {
        "classe": classe,
        "mensagem": mensagem,
        "icone": icone,
        "modelo_sugerido": modelo_sugerido,
    }


def mostrar_diagnostico(hardware):
    """Mostra um diagnóstico completo e divertido do PC"""
    classificacao = classificar_pc(hardware)

    print("\n" + "=" * 60)
    print("🔧 DIAGNÓSTICO DO PC")
    print("=" * 60)

    print(f"\n{classificacao['icone']} {classificacao['classe']}")
    print(f"   {classificacao['mensagem']}")

    print("\n📊 ESPECIFICAÇÕES DETECTADAS:")
    print(f"   💾 RAM: {hardware.get('ram_gb', 0)} GB")
    print(f"   🖥️ GPU: {'✅ Sim' if hardware.get('has_gpu', False) else '❌ Não'}")
    if hardware.get("has_gpu", False):
        print(f"   🎮 GPU: {hardware.get('gpu', 'N/A')[:50]}")
    print(f"   🧠 CPU: {hardware.get('cpu', 'N/A')[:50]}")
    print(f"   🔢 Núcleos: {hardware.get('cpu_cores', 0)}")

    print(f"\n🎯 MODELO RECOMENDADO: {classificacao['modelo_sugerido']}")
    print("=" * 60)

    return classificacao


# ============================================
# TESTE
# ============================================
if __name__ == "__main__":
    hardware = get_hardware_info()
    mostrar_diagnostico(hardware)
