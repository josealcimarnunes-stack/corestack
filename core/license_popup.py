"""
🪟 POPUP DE LICENÇA - Janela amigável com WhatsApp
"""

import tkinter as tk
from tkinter import messagebox
import pyperclip
import sys
import webbrowser


def mostrar_popup_licenca(machine_id: str):
    """
    Mostra uma janela amigável informando que a máquina não tem licença
    """
    root = tk.Tk()
    root.title("🔐 WebStruct Analyzer - Licença")
    root.geometry("520x400")
    root.resizable(False, False)

    # Centraliza a janela
    root.eval("tk::PlaceWindow . center")

    # Cores
    bg_color = "#1e1e2e"
    fg_color = "#cdd6f4"
    accent_color = "#89b4fa"
    error_color = "#f38ba8"
    whatsapp_color = "#25D366"

    root.configure(bg=bg_color)

    # Frame principal
    main_frame = tk.Frame(root, bg=bg_color)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

    # Título
    titulo = tk.Label(
        main_frame,
        text="🔐 Licença Não Encontrada",
        font=("Segoe UI", 16, "bold"),
        fg=error_color,
        bg=bg_color,
    )
    titulo.pack(pady=(0, 10))

    # Mensagem
    mensagem = tk.Label(
        main_frame,
        text="Esta máquina não possui uma licença ativa para o WebStruct Analyzer.",
        font=("Segoe UI", 11),
        fg=fg_color,
        bg=bg_color,
        wraplength=460,
    )
    mensagem.pack(pady=(0, 15))

    # ⭐ FRAME DO MACHINE ID (COM FUNDO DESTAQUE)
    id_frame = tk.Frame(main_frame, bg="#313244", bd=1, relief=tk.SOLID)
    id_frame.pack(fill=tk.X, pady=(0, 15))

    id_label = tk.Label(
        id_frame,
        text=f"🆔 {machine_id}",
        font=("Consolas", 12, "bold"),
        fg=accent_color,
        bg="#313244",
        pady=10,
    )
    id_label.pack()

    # ⭐ INSTRUÇÃO COM WHATSAPP
    instrucao = tk.Label(
        main_frame,
        text="📱 Entre em contato com o suporte no WhatsApp:",
        font=("Segoe UI", 10),
        fg=fg_color,
        bg=bg_color,
    )
    instrucao.pack()

    # ⭐ BOTÃO DO WHATSAPP (CLICÁVEL)
    def abrir_whatsapp():
        # Número do WhatsApp (substitua pelo seu número)
        # Formato: 55 + DDD + Número (sem espaços)
        numero = "5531999999999"  # ⭐ SUBSTITUA PELO SEU NÚMERO AQUI
        mensagem = f"Olá! Preciso de uma licença para o WebStruct Analyzer. Meu Machine ID é: {machine_id}"
        url = f"https://wa.me/{numero}?text={mensagem.replace(' ', '%20')}"
        webbrowser.open(url)

    whatsapp_btn = tk.Button(
        main_frame,
        text="💬 Falar com Suporte no WhatsApp",
        font=("Segoe UI", 11, "bold"),
        bg=whatsapp_color,
        fg="white",
        padx=20,
        pady=10,
        command=abrir_whatsapp,
        cursor="hand2",
        relief=tk.FLAT,
    )
    whatsapp_btn.pack(pady=(10, 15))

    # ⭐ BOTÕES DE AÇÃO
    btn_frame = tk.Frame(main_frame, bg=bg_color)
    btn_frame.pack(fill=tk.X)

    def copiar_id():
        pyperclip.copy(machine_id)
        copiar_btn.config(text="✅ Copiado!", bg="#a6e3a1", fg="#1e1e2e")
        root.after(
            2000,
            lambda: copiar_btn.config(text="📋 Copiar ID", bg="#45475a", fg=fg_color),
        )

    copiar_btn = tk.Button(
        btn_frame,
        text="📋 Copiar ID",
        font=("Segoe UI", 10, "bold"),
        bg="#45475a",
        fg=fg_color,
        padx=20,
        pady=8,
        command=copiar_id,
        cursor="hand2",
    )
    copiar_btn.pack(side=tk.LEFT, padx=(0, 10))

    def fechar():
        root.destroy()
        sys.exit(0)

    fechar_btn = tk.Button(
        btn_frame,
        text="❌ Fechar",
        font=("Segoe UI", 10, "bold"),
        bg="#45475a",
        fg=fg_color,
        padx=20,
        pady=8,
        command=fechar,
        cursor="hand2",
    )
    fechar_btn.pack(side=tk.RIGHT)

    # ⭐ COPIA AUTOMATICAMENTE NA ABERTURA
    pyperclip.copy(machine_id)

    root.focus_force()
    root.mainloop()


def mostrar_erro_conexao():
    """Mostra erro quando não consegue validar a licença"""
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(
        "Erro de Conexão",
        "Não foi possível validar a licença.\n\n"
        "Verifique sua conexão com a internet e tente novamente.",
    )
    root.destroy()
    sys.exit(0)


# ============================================
# TESTE
# ============================================
if __name__ == "__main__":
    mostrar_popup_licenca("1234567890ABCDEF")
