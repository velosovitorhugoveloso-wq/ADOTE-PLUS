import requests

BASE = "http://127.0.0.1:5000"

def testar(nome, metodo, url, **kwargs):
    try:
        r = requests.request(metodo, BASE + url, timeout=5, **kwargs)
        print(f"\n{'='*55}\n{nome}\n{metodo} {url}\nStatus: {r.status_code}\n{r.text}")
    except requests.RequestException as e:
        print(f"\n{nome}: ERRO DE CONEXÃO -> {e}")

testar("SAÚDE", "GET", "/api/health")
testar("ANIMAIS", "GET", "/api/animais")
testar("INDICADORES", "GET", "/api/indicadores")
testar("PEDIDOS", "GET", "/api/pedidos")
testar("APOIOS", "GET", "/api/apoios/indicadores")

# Cria um pedido real no banco usando os IDs de teste 1 e 1.
testar(
    "CRIAR PEDIDO",
    "POST",
    "/api/pedidos",
    json={
        "usuario_id": 1,
        "animal_id": 1,
        "telefone": "(31) 99999-0000",
        "mensagem": "Gostaria de iniciar o processo de adoção da Teca.",
        "experiencia_com_animais": "Sim",
        "tipo_moradia": "Casa",
        "possui_outros_animais": False
    }
)

# Cria uma visita real no banco.
testar(
    "CRIAR VISITA",
    "POST",
    "/api/visitas",
    json={
        "animal_id": 1,
        "usuario_id": 1,
        "data_visita": "2026-08-20",
        "horario": "14:00",
        "observacao": "Visita de teste."
    }
)

# Registra um apoio real no banco.
testar(
    "REGISTRAR APOIO",
    "POST",
    "/api/apoios",
    json={
        "usuario_id": 1,
        "ong_id": 1,
        "valor": 50.00,
        "forma": "PIX"
    }
)
