"""Plano alimentar base (Protocolo hipertrofia/força) com substituições
intercaladas por dia da semana, pra não ficar repetitivo — conforme o
próprio protocolo recomenda (arroz<->macarrão<->batata<->mandioca<->pão<->
tapioca, frango<->carne<->peixe<->ovos, frutas variando)."""

CARBOS = [
    ("Arroz cozido", "150-200 g"),
    ("Macarrão cozido", "150-200 g"),
    ("Batata cozida", "200-250 g"),
    ("Mandioca cozida", "200-250 g"),
]
PAO_TAPIOCA = [("Pão", "50-70 g"), ("Tapioca", "60-80 g")]
PROTEINAS = ["Frango grelhado", "Carne magra", "Peixe grelhado", "Ovos (3-4 unidades)"]
FRUTAS = ["Banana", "Maçã", "Mamão", "Laranja", "Manga"]

PRE_TREINO_OPCOES = [
    ["Banana: 100-120 g", "Aveia: 30-40 g", "Iogurte: 170 g"],
    ["Pão: 50-70 g", "Ovos: 2 unidades", "Fruta: 100-150 g"],
    ["Arroz: 150-200 g", "Feijão: 100-150 g", "Frango: 100-150 g (se o treino for horas depois)"],
]


def _rot(lista, d, offset=0):
    return lista[(d.weekday() + offset) % len(lista)]


def dieta_do_dia(d):
    carbo_almoco, qtd_almoco = _rot(CARBOS, d, 0)
    carbo_jantar, qtd_jantar = _rot(CARBOS, d, 1)
    pao_nome, pao_qtd = _rot(PAO_TAPIOCA, d, 0)
    proteina = _rot(PROTEINAS, d, 0)
    fruta_cafe = _rot(FRUTAS, d, 0)
    fruta_lanche = _rot(FRUTAS, d, 1)

    return {
        "cafe": [
            "Ovos: 2-3 unidades (100-150 g)",
            f"{pao_nome}: {pao_qtd}",
            f"{fruta_cafe}: 80-120 g",
            "Aveia: 20-30 g",
            "Leite: 200-250 ml",
        ],
        "lanche": [
            "Iogurte natural: 170-200 g",
            f"{fruta_lanche}: 100-150 g",
            "Aveia: 20-30 g",
        ],
        "almoco": [
            f"{carbo_almoco}: {qtd_almoco}",
            "Feijão cozido: 100-150 g",
            f"{proteina}: 100-150 g",
            "Legumes: 100-150 g",
            "Verduras: à vontade",
            "Azeite: um fio para complementar",
        ],
        "pre_treino": _rot(PRE_TREINO_OPCOES, d, 0),
        "pos_treino": [
            "Arroz: 150-200 g", "Feijão: 100-150 g",
            f"{proteina}: 100-150 g", "Legumes/verduras: 100-150 g",
            "(se a refeição completa ainda estiver distante, o whey já utilizado pode compor a alimentação do dia, sem precisar ser imediato)",
        ],
        "jantar": [
            f"{carbo_jantar}: {qtd_jantar}",
            "Feijão: 100-150 g",
            f"{proteina}: 100-150 g",
            "Legumes/verduras: 100-150 g",
        ],
        "ceia": ["Leite (200-250 ml) ou iogurte (170-200 g), com fruta se desejar"],
    }
