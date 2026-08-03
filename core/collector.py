"""
🕷️ COLLECTOR - Coleta HTML com janela miniatura (quase invisível)
"""

import random
import time
from playwright.sync_api import sync_playwright

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
]


def aplicar_mascara_stealth(page):
    """Aplica máscara anti-detecção"""
    script = """
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    window.navigator.chrome = { runtime: {} };
    Object.defineProperty(navigator, 'languages', { get: () => ['pt-BR', 'pt', 'en-US', 'en'] });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
    Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 8 });
    Object.defineProperty(navigator, 'deviceMemory', { get: () => 8 });
    """
    page.add_init_script(script)


def coletar_html(url: str) -> str:
    """
    Coleta o HTML da página com JANELA MINIATURA no canto da tela
    """
    ua = random.choice(USER_AGENTS)
    print(f"🌐 User-Agent: {ua[:50]}...")

    # Delay inicial (simula humano)
    time.sleep(random.uniform(1, 3))

    with sync_playwright() as p:
        # ⭐ JANELA MINIATURA (400x300) no canto inferior direito
        browser = p.chromium.launch(
            headless=False,
            args=[
                "--window-position=1500,700",  # ⭐ POSIÇÃO: canto inferior direito
                "--window-size=400,300",  # ⭐ TAMANHO: 400x300 (mini)
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-infobars",
                "--disable-notifications",
                "--disable-popup-blocking",
            ],
        )

        # ⭐ VIEWPORT DO TAMANHO DA JANELA
        page = browser.new_page(viewport={"width": 400, "height": 300})
        aplicar_mascara_stealth(page)

        try:
            print(f"🚀 Coletando: {url}")

            # ⭐ VAI PARA A URL
            page.goto(url, timeout=60000, wait_until="domcontentloaded")

            # ⭐ DELAY CURTO (simula carregamento)
            time.sleep(3)

            # ⭐ PEGA O HTML
            html = page.content()
            tamanho_kb = round(len(html) / 1024, 2)
            print(f"✅ HTML capturado: {tamanho_kb} KB")

            return html

        except Exception as e:
            print(f"❌ Erro: {e}")
            return None

        finally:
            browser.close()
            print("🔒 Navegador fechado.")
