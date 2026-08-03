"""
⛏️ GARIMPEIRO - Extrai containers e lista de elementos do HTML
"""

import sys
import os
import re
import json
from bs4 import BeautifulSoup
from core.database import SessionLocal, obter_html_por_id
from core.models import Container

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def extrair_preco(texto: str) -> float:
    """Extrai o valor numérico de um texto de preço"""
    if not texto:
        return 0.0
    try:
        # Remove R$, espaços e troca vírgula por ponto
        texto_limpo = texto.replace("R$", "").replace(" ", "").strip()
        texto_limpo = texto_limpo.replace(",", ".")
        # Pega números e pontos
        numeros = re.findall(r"[\d.]+", texto_limpo)
        if numeros:
            # Remove pontos de milhar (se tiver mais de um ponto)
            if numeros[0].count(".") > 1:
                numeros[0] = numeros[0].replace(".", "")
            return float(numeros[0])
    except:
        pass
    return 0.0


def gerar_seletor(elem) -> str:
    """Gera um seletor CSS para o elemento"""
    if elem.get("id"):
        return f"#{elem.get('id')}"
    classes = elem.get("class", [])
    if classes:
        if isinstance(classes, list):
            return f"{elem.name}.{'.'.join(classes[:2])}"
        return f"{elem.name}.{classes.replace(' ', '.')}"
    return elem.name


def extrair_elementos_do_container(container) -> list:
    """
    Extrai a lista de TODOS os elementos dentro de um container
    Retorna uma lista com: tag, class, id, seletor, texto, nivel
    """
    elementos = []

    for elem in container.find_all(recursive=True):
        if not elem.name:
            continue

        # Pega o texto (limitado a 200 caracteres)
        texto = elem.get_text(strip=True)[:200] if elem.get_text(strip=True) else ""

        elemento = {
            "tag": elem.name,
            "class": " ".join(elem.get("class", [])) if elem.get("class") else "",
            "id": elem.get("id", ""),
            "seletor": gerar_seletor(elem),
            "texto": texto,
            "tem_filhos": len(elem.find_all(recursive=False)) > 0,
            "nivel": len(elem.find_parents()),
        }

        # Se for imagem, guarda o src
        if elem.name == "img":
            elemento["src"] = elem.get("src", "")

        # Se for link, guarda o href
        if elem.name == "a":
            elemento["href"] = elem.get("href", "")

        # Se tiver data-product-id, guarda
        if elem.get("data-product-id"):
            elemento["produto_id"] = elem.get("data-product-id")

        elementos.append(elemento)

    return elementos


def destrinchar_e_salvar(coleta_id: int, site: str) -> list:
    """
    ⭐ FUNÇÃO PRINCIPAL: Extrai containers e salva no banco
    """
    resultado = obter_html_por_id(coleta_id)
    if not resultado:
        print("❌ Coleta não encontrada!")
        return []

    html = resultado[0]
    soup = BeautifulSoup(html, "html.parser")

    # ⭐ ENCONTRA OS CONTAINERS DE PRODUTOS
    # Seletores comuns para Magalu e outros sites
    seletores_container = [
        '[data-testid="product-card"]',
        ".sc-bYMlYs",
        ".sc-ftvSup",
        ".sc-dVHjTx",
        "div[data-product-id]",
        ".product-card",
        ".card-product",
        "li[data-product-id]",
        'div[class*="product"]',
        'div[class*="Product"]',
        'div[class*="produto"]',
        'div[class*="card"]',
        'div[class*="item"]',
    ]

    containers = []
    for seletor in seletores_container:
        try:
            encontrados = soup.select(seletor)
            if encontrados:
                containers = encontrados
                print(f"🔍 Encontrados {len(containers)} containers com: {seletor}")
                break
        except:
            continue

    # ⭐ FALLBACK: Busca por imagens
    if not containers:
        imagens = soup.find_all("img", class_=re.compile(r"product|Product|card"))
        if imagens:
            containers = [
                img.find_parent("div") for img in imagens if img.find_parent("div")
            ]
            containers = list(filter(None, containers))
            print(f"🔍 Encontrados {len(containers)} containers via imagens")

    # ⭐ FALLBACK 2: Busca genérica
    if not containers:
        containers = soup.find_all(
            "div", class_=re.compile(r"product|produto|Product|card|item")
        )
        print(f"🔍 Encontrados {len(containers)} containers com busca genérica")

    if not containers:
        print("⚠️ Nenhum container de produto encontrado!")
        return []

    print(f"📦 Processando {len(containers)} containers...")

    db = SessionLocal()
    containers_salvos = []

    try:
        for idx, container in enumerate(containers[:30]):  # Limite de 30 por segurança
            print(f"   🔧 Processando container {idx+1}/{len(containers[:30])}...")

            # ⭐ 1. EXTRAI NOME
            nome = ""
            nome_selectors = [
                '[data-testid="product-title"]',
                "h2",
                "h3",
                "h4",
                ".product-title",
                ".title",
                '[class*="title"]',
                '[class*="name"]',
            ]
            for sel in nome_selectors:
                tag = container.select_one(sel)
                if tag:
                    texto = tag.get_text(strip=True)
                    if texto and len(texto) > 3:
                        nome = texto[:300]
                        break

            # ⭐ 2. EXTRAI PREÇO
            preco_texto = ""
            preco_selectors = [
                '[data-testid="price"]',
                ".price",
                ".preco",
                '[class*="price"]',
                '[class*="preco"]',
                '[class*="Price"]',
                ".product-price",
            ]
            for sel in preco_selectors:
                tag = container.select_one(sel)
                if tag:
                    texto = tag.get_text(strip=True)
                    if texto and any(c.isdigit() for c in texto):
                        preco_texto = texto
                        break

            # ⭐ 3. EXTRAI LINK
            link = ""
            link_tag = container.find("a")
            if link_tag:
                link = link_tag.get("href", "")

            # ⭐ 4. EXTRAI PRODUTO ID
            produto_id = container.get("data-product-id", "")
            if not produto_id and link:
                match = re.search(r"/(\d+)(?:/|$)", link)
                if match:
                    produto_id = match.group(1)

            # ⭐ 5. EXTRAI A LISTA DE ELEMENTOS DENTRO DO CONTAINER
            elementos = extrair_elementos_do_container(container)

            # ⭐ 6. CRIA O OBJETO CONTAINER
            container_obj = Container(
                coleta_id=coleta_id,
                container_html=str(container),
                seletor_container=gerar_seletor(container),
                nome=nome if nome else f"Produto {idx+1}",
                preco_texto=preco_texto,
                preco_valor=extrair_preco(preco_texto),
                link=link,
                produto_id=produto_id,
            )
            container_obj.set_elementos(elementos)

            db.add(container_obj)
            containers_salvos.append(container_obj)

        db.commit()
        print(f"\n✅ {len(containers_salvos)} containers salvos com sucesso!")

        if containers_salvos:
            primeiro = containers_salvos[0]
            total_elementos = len(primeiro.get_elementos())
            print(f"   📊 Média de elementos por container: {total_elementos}")

    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao salvar containers: {e}")
        import traceback

        traceback.print_exc()
    finally:
        db.close()

    return containers_salvos


def processar_coleta(coleta_id: int):
    """Processa uma coleta específica (função de conveniência)"""
    resultado = obter_html_por_id(coleta_id)
    if not resultado:
        print("❌ Coleta não encontrada!")
        return

    url = resultado[1]
    site = resultado[2]

    print(f"\n📄 Processando coleta #{coleta_id}: {site}")
    return destrinchar_e_salvar(coleta_id, site)


def processar_todas_coletas():
    """Processa todas as coletas do banco"""
    from core.models import Coleta

    db = SessionLocal()
    try:
        coletas = db.query(Coleta).order_by(Coleta.id.desc()).all()
        print(f"📊 Total de coletas: {len(coletas)}")

        for coleta in coletas:
            destrinchar_e_salvar(coleta.id, coleta.site)
    finally:
        db.close()


# ============================================
# TESTE RÁPIDO
# ============================================
if __name__ == "__main__":
    from core.database import init_db

    init_db()

    # Pega a última coleta
    from core.models import Coleta

    db = SessionLocal()
    try:
        ultima = db.query(Coleta).order_by(Coleta.id.desc()).first()
        if ultima:
            print(f"\n🧪 Testando com a coleta #{ultima.id}")
            processar_coleta(ultima.id)
        else:
            print("❌ Nenhuma coleta encontrada. Faça uma coleta primeiro!")
    finally:
        db.close()
