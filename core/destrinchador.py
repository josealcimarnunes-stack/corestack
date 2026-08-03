"""
🔍 DESTRINCHADOR - Extrai produtos do HTML salvo no SQLite
"""

import re
from bs4 import BeautifulSoup
from core.database import SessionLocal
from core.models import Coleta, Produto
from urllib.parse import urljoin


class Destrinchador:
    """Extrai produtos de HTML de e-commerce"""

    def __init__(self):
        self.padroes = {
            "nomes_comuns": [
                "product-title",
                "product-name",
                "produto-nome",
                "item-name",
                "title",
                "nome-produto",
                "product-item-title",
                "product-title-link",
            ],
            "precos_comuns": [
                "price",
                "product-price",
                "preco",
                "valor",
                "product-price-value",
                "price-amount",
                "preco-por",
                "current-price",
                "price-value",
            ],
            "imagens_comuns": [
                "product-image",
                "product-img",
                "image",
                "img",
                "product-photo",
                "item-image",
                "product-picture",
            ],
            "links_comuns": [
                "product-link",
                "product-url",
                "link",
                "href",
                "product-item-link",
                "product-title-link",
            ],
        }

    def extrair_produtos(self, html, url_base):
        """
        Extrai produtos do HTML

        Args:
            html: HTML da página
            url_base: URL base para links relativos

        Returns:
            list: Lista de dicionários com produtos
        """
        soup = BeautifulSoup(html, "html.parser")

        # ⭐ 1. TENTA ENCONTRAR CONTAINERS DE PRODUTOS
        containers = self._encontrar_containers(soup)

        if not containers:
            print("⚠️ Nenhum container de produto encontrado")
            return []

        print(f"🔍 Encontrados {len(containers)} containers de produtos")

        # ⭐ 2. EXTRAI DADOS DE CADA CONTAINER
        produtos = []
        for i, container in enumerate(containers):
            produto = self._extrair_dados_container(container, url_base)

            if produto and produto.get("nome"):
                # Adiciona índice para referência
                produto["indice"] = i + 1
                produtos.append(produto)
                print(
                    f"   ✅ {produto['nome'][:40]}... - {produto.get('preco_texto', 'N/A')}"
                )

        print(f"📦 Total de produtos extraídos: {len(produtos)}")
        return produtos

    def _encontrar_containers(self, soup):
        """Encontra containers de produtos no HTML"""
        containers = []

        # ⭐ ESTRATÉGIA 1: Classes comuns de produto
        padroes_container = [
            "product-item",
            "product-card",
            "product",
            "item",
            "produto",
            "product-container",
            "product-box",
            "product-list-item",
            "product-grid-item",
            "product-card-container",
            "product-wrapper",
        ]

        for classe in padroes_container:
            # Procura por divs com essas classes
            elementos = soup.find_all("div", class_=re.compile(classe, re.I))
            elementos += soup.find_all("li", class_=re.compile(classe, re.I))
            elementos += soup.find_all("article", class_=re.compile(classe, re.I))

            for el in elementos:
                if el not in containers:
                    containers.append(el)

        # ⭐ ESTRATÉGIA 2: Tags com atributos data-*
        for tag in soup.find_all(["div", "li", "article"]):
            if tag.get("data-product") or tag.get("data-item") or tag.get("data-id"):
                if tag not in containers:
                    containers.append(tag)

        # ⭐ ESTRATÉGIA 3: Links de produtos (fallback)
        if not containers:
            links = soup.find_all(
                "a", href=re.compile(r"/(produto|product|item|p-|/p/)")
            )
            for link in links:
                # Pega o container pai
                pai = link.find_parent(["div", "li", "article"])
                if pai and pai not in containers:
                    containers.append(pai)

        # ⭐ LIMITA A 100 CONTAINERS (segurança)
        return containers[:100]

    def _extrair_dados_container(self, container, url_base):
        """Extrai dados de um container específico"""
        dados = {}

        # ⭐ 1. EXTRAI NOME
        dados["nome"] = self._extrair_nome(container)

        # ⭐ 2. EXTRAI PREÇO
        dados["preco_texto"], dados["preco_valor"] = self._extrair_preco(container)

        # ⭐ 3. EXTRAI IMAGEM
        dados["imagem"] = self._extrair_imagem(container, url_base)

        # ⭐ 4. EXTRAI LINK
        dados["link"] = self._extrair_link(container, url_base)

        # ⭐ 5. SELETOR (pra saber onde foi encontrado)
        dados["seletor"] = self._gerar_seletor(container)

        return dados

    def _extrair_nome(self, container):
        """Extrai o nome do produto"""
        # Tenta encontrar pela classe
        for padrao in self.padroes["nomes_comuns"]:
            elemento = container.find(class_=re.compile(padrao, re.I))
            if elemento:
                nome = elemento.get_text(strip=True)
                if nome and len(nome) > 2:
                    return nome

        # Tenta encontrar por tag
        for tag in ["h1", "h2", "h3", "h4", "h5"]:
            elemento = container.find(tag)
            if elemento:
                nome = elemento.get_text(strip=True)
                if nome and len(nome) > 2:
                    return nome

        # Tenta qualquer texto dentro do container
        texto = container.get_text(strip=True)
        if texto and len(texto) < 200:
            # Pega a primeira linha
            linhas = texto.split("\n")
            for linha in linhas:
                linha = linha.strip()
                if linha and len(linha) > 3 and not linha.startswith(("R$", "$", "€")):
                    return linha[:100]

        return None

    def _extrair_preco(self, container):
        """Extrai o preço do produto"""
        # Tenta encontrar pela classe
        for padrao in self.padroes["precos_comuns"]:
            elemento = container.find(class_=re.compile(padrao, re.I))
            if elemento:
                texto = elemento.get_text(strip=True)
                preco = self._limpar_preco(texto)
                if preco["texto"]:
                    return preco["texto"], preco["valor"]

        # Tenta encontrar padrões de preço no texto
        texto = container.get_text()

        # Padrões de preço brasileiro
        padroes = [
            r"R\$\s*([\d,.]+)",  # R$ 99,90
            r"R\$\s*([\d.]+,\d{2})",  # R$ 99,90
            r"([\d.]+,\d{2})",  # 99,90
            r"\$\s*([\d,.]+)",  # $99.90
            r"€\s*([\d,.]+)",  # €99,90
            r"(\d+\.\d{2})",  # 99.90
        ]

        for padrao in padroes:
            match = re.search(padrao, texto)
            if match:
                preco_str = match.group(1)
                preco_texto = f"R$ {preco_str}" if "R$" not in texto else texto
                preco_valor = self._converter_para_float(preco_str)
                if preco_valor:
                    return preco_texto, preco_valor

        return None, None

    def _extrair_imagem(self, container, url_base):
        """Extrai a URL da imagem"""
        # Tenta encontrar pela classe
        for padrao in self.padroes["imagens_comuns"]:
            elemento = container.find(class_=re.compile(padrao, re.I))
            if elemento:
                # Tenta src, data-src, etc
                for attr in ["src", "data-src", "data-original", "content"]:
                    url = elemento.get(attr)
                    if url:
                        return urljoin(url_base, url)

        # Tenta qualquer imagem dentro do container
        img = container.find("img")
        if img:
            for attr in ["src", "data-src", "data-original"]:
                url = img.get(attr)
                if url:
                    return urljoin(url_base, url)

        return None

    def _extrair_link(self, container, url_base):
        """Extrai o link do produto"""
        # Tenta encontrar pela classe
        for padrao in self.padroes["links_comuns"]:
            elemento = container.find(class_=re.compile(padrao, re.I))
            if elemento and elemento.name == "a":
                href = elemento.get("href")
                if href:
                    return urljoin(url_base, href)

        # Tenta qualquer link dentro do container
        link = container.find("a", href=True)
        if link:
            href = link.get("href")
            if href:
                return urljoin(url_base, href)

        return None

    def _limpar_preco(self, texto):
        """Limpa e formata o texto do preço"""
        if not texto:
            return {"texto": None, "valor": None}

        # Remove espaços extras
        texto = texto.strip()

        # Tenta encontrar um valor numérico
        match = re.search(r"[\d,.]+", texto)
        if match:
            valor_str = match.group()
            valor = self._converter_para_float(valor_str)
            if valor:
                return {"texto": texto, "valor": valor}

        return {"texto": texto, "valor": None}

    def _converter_para_float(self, valor_str):
        """Converte string de preço para float"""
        if not valor_str:
            return None

        # Limpa
        valor_str = valor_str.replace("R$", "").replace("$", "").replace("€", "")
        valor_str = valor_str.strip()

        # Caso brasileiro: 1.234,56
        if "," in valor_str and "." in valor_str:
            # Última vírgula é decimal
            partes = valor_str.rsplit(",", 1)
            valor_str = partes[0].replace(".", "") + "." + partes[1]
        elif "," in valor_str:
            valor_str = valor_str.replace(",", ".")

        try:
            return float(valor_str)
        except:
            return None

    def _gerar_seletor(self, elemento):
        """Gera um seletor CSS para o elemento"""
        if not elemento:
            return None

        # Tenta gerar um seletor simples
        classes = elemento.get("class", [])
        if classes:
            return f"{elemento.name}.{'.'.join(classes)}"

        # Fallback
        return elemento.name


def destrinchar_todas_coletas(limite=None):
    """
    Processa todas as coletas e extrai produtos

    Args:
        limite: Número máximo de coletas para processar

    Returns:
        dict: Estatísticas do processamento
    """
    print("\n" + "=" * 60)
    print("🔍 DESTRINCHANDO TODAS AS COLETAS")
    print("=" * 60)

    db = SessionLocal()
    try:
        # Busca coletas
        query = db.query(Coleta).order_by(Coleta.id.desc())
        if limite:
            query = query.limit(limite)

        coletas = query.all()
        print(f"📊 {len(coletas)} coletas encontradas")

        destrinchador = Destrinchador()
        total_produtos = 0
        resultados = []

        for coleta in coletas:
            print(f"\n📄 Processando: {coleta.site} (ID: {coleta.id})")

            # Extrai produtos do HTML
            produtos = destrinchador.extrair_produtos(coleta.html, coleta.url)

            if produtos:
                # Salva produtos no banco
                for p in produtos:
                    # Verifica se já existe (evita duplicatas)
                    existente = (
                        db.query(Produto)
                        .filter(
                            Produto.coleta_id == coleta.id,
                            Produto.nome == p.get("nome", ""),
                            Produto.link == p.get("link", ""),
                        )
                        .first()
                    )

                    if not existente:
                        produto = Produto(
                            coleta_id=coleta.id,
                            nome=p.get("nome", "")[:300],
                            preco_texto=p.get("preco_texto", ""),
                            preco_valor=p.get("preco_valor"),
                            seletor=p.get("seletor", ""),
                            link=p.get("link", "")[:500],
                            imagem=p.get("imagem", "")[:500],
                        )
                        db.add(produto)

                db.commit()
                print(f"✅ {len(produtos)} produtos salvos")
                total_produtos += len(produtos)
                resultados.append(
                    {
                        "coleta_id": coleta.id,
                        "site": coleta.site,
                        "produtos": len(produtos),
                    }
                )
            else:
                print("⚠️ Nenhum produto encontrado")

        print("\n" + "=" * 60)
        print(f"📊 RESULTADO FINAL:")
        print(f"   Total de coletas processadas: {len(coletas)}")
        print(f"   Total de produtos extraídos: {total_produtos}")
        print("=" * 60)

        return {
            "total_coletas": len(coletas),
            "total_produtos": total_produtos,
            "resultados": resultados,
        }

    finally:
        db.close()


def destrinchar_coleta_especifica(coleta_id):
    """
    Processa uma coleta específica

    Args:
        coleta_id: ID da coleta

    Returns:
        list: Produtos extraídos
    """
    db = SessionLocal()
    try:
        coleta = db.query(Coleta).filter(Coleta.id == coleta_id).first()
        if not coleta:
            print(f"❌ Coleta {coleta_id} não encontrada")
            return []

        print(f"\n🔍 Destrinchando coleta {coleta_id} - {coleta.site}")

        destrinchador = Destrinchador()
        produtos = destrinchador.extrair_produtos(coleta.html, coleta.url)

        # Salva no banco
        for p in produtos:
            produto = Produto(
                coleta_id=coleta.id,
                nome=p.get("nome", "")[:300],
                preco_texto=p.get("preco_texto", ""),
                preco_valor=p.get("preco_valor"),
                seletor=p.get("seletor", ""),
                link=p.get("link", "")[:500],
                imagem=p.get("imagem", "")[:500],
            )
            db.add(produto)

        db.commit()
        print(f"✅ {len(produtos)} produtos salvos")

        return produtos

    finally:
        db.close()


# ============================================
# TESTE
# ============================================
if __name__ == "__main__":
    print("🔍 TESTE DO DESTRINCHADOR")
    print("=" * 60)

    # Processa as últimas 5 coletas
    resultado = destrinchar_todas_coletas(5)

    # Mostra alguns produtos
    db = SessionLocal()
    try:
        produtos = db.query(Produto).order_by(Produto.id.desc()).limit(10).all()
        print("\n📋 ÚLTIMOS PRODUTOS EXTRAÍDOS:")
        for p in produtos:
            print(f"   🛒 {p.nome[:50]}")
            print(f"      Preço: {p.preco_texto}")
            print(f"      Link: {p.link[:50] if p.link else 'N/A'}...")
            print()
    finally:
        db.close()


def extrair_produtos_do_html(html, url_base):
    """
    Função rápida para extrair produtos de um HTML

    Args:
        html: String com o HTML
        url_base: URL base para links relativos

    Returns:
        list: Lista de dicionários com produtos
    """
    destrinchador = Destrinchador()
    return destrinchador.extrair_produtos(html, url_base)
