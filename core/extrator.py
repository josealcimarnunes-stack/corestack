def processar_todas_coletas():
    """
    Processa todas as coletas e retorna os produtos extraídos
    """
    print("\n" + "=" * 60)
    print("📦 PROCESSANDO TODAS AS COLETAS")
    print("=" * 60)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, url, nome_site FROM coletas ORDER BY id DESC")
    coletas = cursor.fetchall()
    conn.close()

    print(f"📊 Total de coletas: {len(coletas)}")

    resultados = []

    for item in coletas:
        id_coleta = item[0]
        url = item[1]
        nome_site = item[2]

        print(f"\n📄 Processando: {nome_site} (ID: {id_coleta})")

        # Pega o HTML
        resultado = obter_html_por_id(id_coleta)
        if not resultado:
            continue

        html = resultado[0]

        # Extrai produtos
        produtos = extrair_produtos_do_html(html)

        # Salva no banco
        salvar_produtos(id_coleta, url, nome_site, produtos)

        resultados.append(produtos)

    return resultados


def salvar_produtos(coleta_id: int, url: str, nome_site: str, produtos: list):
    """
    Salva os produtos extraídos no banco
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    for p in produtos:
        cursor.execute(
            """
            INSERT INTO produtos (coleta_id, url, nome_site, titulo, preco_texto, preco_valor, imagem, link)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                coleta_id,
                url,
                nome_site,
                p.get("titulo", ""),
                p.get("preco_texto", ""),
                p.get("preco_valor"),
                p.get("imagem", ""),
                p.get("link", ""),
            ),
        )

    conn.commit()
    conn.close()
    print(f"✅ {len(produtos)} produtos salvos para {nome_site}")
