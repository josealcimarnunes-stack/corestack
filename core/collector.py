"""
🕷️ COLLECTOR - Playwright Stealth para capturar HTML
"""

import random
import time
from playwright.sync_api import sync_playwright

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
]


def aplicar_mascara_stealth(page):
    script = """
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    window.navigator.chrome = { runtime: {} };
    Object.defineProperty(navigator, 'languages', { get: () => ['pt-BR', 'pt', 'en-US', 'en'] });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
    Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 8 });
    Object.defineProperty(navigator, 'deviceMemory', { get: () => 8 });
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
    """
    page.add_init_script(script)


def coletar_html(url: str) -> str:
    """Coleta o HTML da página usando Playwright"""
    ua = random.choice(USER_AGENTS)
    print(f"🌐 User-Agent: {ua[:50]}...")

    time.sleep(random.uniform(2, 4))

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=[
                "--start-maximized",
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-infobars",
                "--disable-notifications",
                "--disable-popup-blocking",
                "--window-size=1920,1080",
            ],
        )

        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        aplicar_mascara_stealth(page)

        try:
            print(f"🚀 Acessando: {url}")
            page.goto(url, timeout=60000, wait_until="domcontentloaded")
            time.sleep(5)

            # Rolagem humana
            page.evaluate("window.scrollBy(0, 300)")
            time.sleep(2)
            page.evaluate("window.scrollBy(0, 300)")
            time.sleep(2)
            page.evaluate("window.scrollTo(0, 0)")
            time.sleep(2)

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
