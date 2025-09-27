import requests
import time
import csv

# Variables globales para control de peticiones y cantidad
RATE_LIMIT_PER_MIN = 30
SLEEP_TIME = 60 / RATE_LIMIT_PER_MIN  # segundos entre requests
MAX_COINS = 1000  # cantidad máxima de monedas a extraer

API_KEY = "API_KEY"  # Reemplazar con la API KEY
BASE_URL = "https://api.coingecko.com/api/v3"
HEADERS = {"Accept": "application/json", "x-cg-demo-api-key": API_KEY}

# Categorías permitidas según el proyecto
CATEGORIAS_PERMITIDAS = [
    "Artificial Intelligence (AI)",
    "Videojuegos",
    "Real World Assets (RWA)",
    "Memes"
]

def get_coins_list(per_page=50, page=1):
    url = f"{BASE_URL}/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": per_page,
        "page": page,
        "sparkline": "false"
    }
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json()

def get_coin_details(coin_id):
    url = f"{BASE_URL}/coins/{coin_id}"
    params = {
        "localization": "false",
        "tickers": "true",
        "market_data": "true",
        "community_data": "true",
        "developer_data": "false",
        "sparkline": "false"
    }
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json()

def extract_coin_data(coin):
    coin_id = coin['id']
    details = get_coin_details(coin_id)

    categories = details.get("categories", [])
    if not any(cat in CATEGORIAS_PERMITIDAS for cat in categories):
        return None

    market_data = details.get("market_data", {})
    community_data = details.get("community_data", {})
    platforms = details.get("platforms", {})
    links = details.get("links", {})

    tickers = details.get("tickers", [])
    cex_exchanges = set()
    for ticker in tickers:
        market = ticker.get("market", {})
        if market.get("identifier") and not market.get("identifier").startswith("dex"):
            cex_exchanges.add(market["identifier"])

    volumen_24h = market_data.get("total_volume", {}).get("usd", 0)
    market_cap = market_data.get("market_cap", {}).get("usd", 0)
    porcentaje_volumen_diario = (volumen_24h / market_cap) if market_cap and market_cap > 0 else 0

    contratos = ", ".join([f"{k}: {v}" for k, v in platforms.items() if v])

    blockchain_sites = ", ".join([url for url in links.get("blockchain_site", []) if url])
    explorers = ", ".join([url for url in links.get("explorers", []) if url]) if "explorers" in links else ""

    description = details.get("description", {}).get("en", "").lower()
    public_notice = details.get("public_notice", "").lower() if details.get("public_notice") else ""
    halving_indicator = "sí" if ("halving" in description or "halving" in public_notice) else "no"

    multichain = "sí" if len([v for v in platforms.values() if v]) > 1 else "no"

    data = {
        "id": coin_id,
        "nombre": details.get("name", ""),
        "símbolo": details.get("symbol", ""),
        "categoría": ", ".join(categories) if categories else "Sin categoría",
        "precio_usd": market_data.get("current_price", {}).get("usd", 0),
        "capitalización_usd": market_data.get("market_cap", {}).get("usd", 0),
        "volumen_24h_usd": volumen_24h,
        "porcentaje_volumen_diario": porcentaje_volumen_diario,
        "suministro_circulante": market_data.get("circulating_supply", 0),
        "suministro_total": market_data.get("total_supply", 0),
        "suministro_maximo": market_data.get("max_supply", 0),
        "actividad_comunitaria": sum([
            community_data.get("facebook_likes", 0) or 0,
            community_data.get("twitter_followers", 0) or 0,
            community_data.get("reddit_subscribers", 0) or 0,
            community_data.get("telegram_channel_user_count", 0) or 0
        ]),
        "ranking": market_data.get("market_cap_rank", 0),
        "listado_cex": len(cex_exchanges),
        "contratos": contratos,
        "billeteras": blockchain_sites,
        "exploradores": explorers,
        "halving": halving_indicator,
        "multichain": multichain
    }
    return data

def main():
    all_data = []
    per_page = 50
    page = 1
    total_extracted = 0

    while total_extracted < MAX_COINS:
        coins = get_coins_list(per_page=per_page, page=page)
        if not coins:
            break

        for coin in coins:
            if total_extracted >= MAX_COINS:
                break
            try:
                data = extract_coin_data(coin)
                if data:
                    all_data.append(data)
                    total_extracted += 1
                    print(f"Monedas extraídas: {total_extracted}")
                time.sleep(SLEEP_TIME)
            except Exception as e:
                print(f"Error al procesar {coin['id']}: {e}")

        page += 1

    keys = [
        "id", "nombre", "símbolo", "categoría", "precio_usd", "capitalización_usd",
        "volumen_24h_usd", "porcentaje_volumen_diario", "suministro_circulante",
        "suministro_total", "suministro_maximo", "actividad_comunitaria", "ranking",
        "listado_cex", "contratos", "billeteras", "exploradores", "halving", "multichain"
    ]
    with open("dataset_cripto_completo.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(all_data)

    print(f"Datos guardados en dataset_cripto_completo.csv con {total_extracted} registros.")

if __name__ == "__main__":
    main()