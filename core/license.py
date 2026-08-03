# core/license.py
import hashlib
import socket
import uuid
import requests
import datetime
import sys
import os

# ============================================
# URL DO ARQUIVO DE LICENÇAS (LINK RAW)
# ============================================
URL_LICENCAS = "https://raw.githubusercontent.com/josealcimarnunes-stack/licencas-WEBSTRUCT_ANALYZER-/main/licen%C3%A7as_corestack.json"


# ============================================
# GERAR MACHINE ID
# ============================================
def get_machine_id():
    try:
        mac = uuid.getnode()
        hostname = socket.gethostname()
        return hashlib.md5(f"{mac}{hostname}".encode()).hexdigest()
    except:
        try:
            import os

            return hashlib.md5(
                f"{os.getlogin()}{socket.gethostname()}".encode()
            ).hexdigest()
        except:
            return hashlib.md5(socket.gethostname().encode()).hexdigest()


# ============================================
# VALIDAR LICENÇA ONLINE (COM POPUP)
# ============================================
def validar_licenca():
    """
    Valida a licença da máquina no GitHub.
    Retorna: (bool, str) - (sucesso, mensagem)
    """
    machine_id = get_machine_id()

    try:
        response = requests.get(URL_LICENCAS, timeout=5)

        if response.status_code != 200:
            return False, "❌ Erro ao validar licença. Verifique sua internet."

        # ⭐ CARREGA A LISTA DE IDs DO JSON
        try:
            lista_licencas = response.json()
        except:
            return False, "❌ Erro ao ler o arquivo de licenças."

        # ⭐ VERIFICA SE O MACHINE_ID ESTÁ NA LISTA
        if machine_id in lista_licencas:
            return True, f"✅ Licença válida para esta máquina."
        else:
            return False, f"❌ Machine ID não encontrado: {machine_id}"

    except requests.exceptions.ConnectionError:
        return False, "❌ Sem internet. Conecte-se e tente novamente."
    except Exception as e:
        return False, f"❌ Erro ao validar: {e}"


# ============================================
# VALIDAR COM POPUP (SE NÃO TIVER LICENÇA)
# ============================================
def validar_licenca_com_popup():
    """
    Valida licença e mostra popup amigável se não tiver.
    Retorna: bool - True se válida, False se inválida (e já mostrou popup).
    """
    sucesso, mensagem = validar_licenca()

    if sucesso:
        print(f"\n🔐 {mensagem}")
        print(f"📱 Machine ID: {get_machine_id()}")
        return True
    else:
        print(f"\n❌ {mensagem}")

        # Tenta mostrar o popup (se tiver tkinter)
        try:
            from core.license_popup import mostrar_popup_licenca, mostrar_erro_conexao

            if "internet" in mensagem.lower():
                mostrar_erro_conexao()
            else:
                mostrar_popup_licenca(get_machine_id())
        except ImportError:
            print("⚠️ Popup não disponível. Verifique se o tkinter está instalado.")

        return False


# ============================================
# TESTE RÁPIDO
# ============================================
if __name__ == "__main__":
    print("=" * 60)
    print("🔐 SISTEMA DE LICENÇA - WEBSTRUCT")
    print("=" * 60)

    sucesso, mensagem = validar_licenca()
    print(f"\n{mensagem}")
    print(f"📱 Machine ID: {get_machine_id()}")
    print("=" * 60)
