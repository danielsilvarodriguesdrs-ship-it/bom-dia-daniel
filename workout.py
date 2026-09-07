INK, SOFT, CLAY, GREY = "#2E2C27", "#6B6A63", "#C6613F", "#B4B3A8"


def _svg(inner, label):
    return (f'<svg viewBox="0 0 150 130" xmlns="http://www.w3.org/2000/svg" '
            f'aria-label="{label}">{inner}</svg>')


def ic_squat():
    return _svg(f'''
<circle cx="75" cy="22" r="8" fill="none" stroke="{INK}" stroke-width="2.4"/>
<line x1="40" y1="40" x2="110" y2="40" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>
<circle cx="40" cy="40" r="7" fill="none" stroke="{INK}" stroke-width="2.4"/>
<circle cx="110" cy="40" r="7" fill="none" stroke="{INK}" stroke-width="2.4"/>
<line x1="75" y1="30" x2="75" y2="70" stroke="{INK}" stroke-width="2.6"/>
<path d="M75 70 L58 88 L58 112" fill="none" stroke="{CLAY}" stroke-width="5" stroke-linecap="round"/>
<path d="M75 70 L92 88 L92 112" fill="none" stroke="{CLAY}" stroke-width="5" stroke-linecap="round"/>''',
                "Agachamento")


def ic_legpress():
    return _svg(f'''
<line x1="18" y1="112" x2="132" y2="112" stroke="{GREY}" stroke-width="2"/>
<line x1="30" y1="112" x2="120" y2="46" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>
<circle cx="46" cy="98" r="8" fill="none" stroke="{INK}" stroke-width="2.4"/>
<line x1="46" y1="98" x2="70" y2="82" stroke="{INK}" stroke-width="2.6"/>
<path d="M70 82 L88 74 L104 58" fill="none" stroke="{CLAY}" stroke-width="5" stroke-linecap="round"/>''',
                "Leg press")


def ic_legext():
    return _svg(f'''
<line x1="30" y1="70" x2="70" y2="70" stroke="{INK}" stroke-width="3"/>
<line x1="30" y1="70" x2="30" y2="112" stroke="{INK}" stroke-width="2.4"/>
<line x1="30" y1="70" x2="24" y2="40" stroke="{INK}" stroke-width="2.4"/>
<circle cx="24" cy="32" r="8" fill="none" stroke="{INK}" stroke-width="2.4"/>
<path d="M70 70 L104 62" fill="none" stroke="{CLAY}" stroke-width="5" stroke-linecap="round"/>''',
                "Cadeira extensora")


def ic_legcurl():
    return _svg(f'''
<line x1="20" y1="92" x2="118" y2="92" stroke="{GREY}" stroke-width="2"/>
<line x1="28" y1="84" x2="92" y2="84" stroke="{INK}" stroke-width="3"/>
<circle cx="30" cy="76" r="8" fill="none" stroke="{INK}" stroke-width="2.4"/>
<path d="M92 84 Q112 84 110 60" fill="none" stroke="{CLAY}" stroke-width="5" stroke-linecap="round"/>''',
                "Mesa flexora")


def ic_calf():
    return _svg(f'''
<circle cx="75" cy="24" r="8" fill="none" stroke="{INK}" stroke-width="2.4"/>
<line x1="75" y1="32" x2="75" y2="66" stroke="{INK}" stroke-width="2.6"/>
<line x1="75" y1="66" x2="68" y2="92" stroke="{INK}" stroke-width="2.6"/>
<line x1="75" y1="66" x2="82" y2="92" stroke="{INK}" stroke-width="2.6"/>
<path d="M68 92 Q64 102 66 106" fill="none" stroke="{CLAY}" stroke-width="5" stroke-linecap="round"/>
<path d="M82 92 Q86 102 84 106" fill="none" stroke="{CLAY}" stroke-width="5" stroke-linecap="round"/>''',
                "Panturrilha")


def ic_curl():
    return _svg(f'''
<circle cx="75" cy="24" r="8" fill="none" stroke="{INK}" stroke-width="2.4"/>
<line x1="75" y1="32" x2="75" y2="78" stroke="{INK}" stroke-width="2.6"/>
<path d="M75 46 L60 62" stroke="{CLAY}" stroke-width="5.5" stroke-linecap="round"/>
<path d="M75 46 L90 62" stroke="{CLAY}" stroke-width="5.5" stroke-linecap="round"/>
<line x1="52" y1="46" x2="98" y2="46" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>''',
                "Rosca direta")


def ic_pushdown():
    return _svg(f'''
<line x1="112" y1="8" x2="112" y2="40" stroke="{GREY}" stroke-width="2"/>
<line x1="104" y1="40" x2="120" y2="40" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>
<circle cx="60" cy="26" r="8" fill="none" stroke="{INK}" stroke-width="2.4"/>
<line x1="60" y1="34" x2="60" y2="80" stroke="{INK}" stroke-width="2.6"/>
<path d="M60 48 L84 56" stroke="{CLAY}" stroke-width="5.5" stroke-linecap="round"/>
<path d="M84 56 L112 42" stroke="{INK}" stroke-width="2.6" stroke-linecap="round"/>''',
                "Tríceps na polia")


def ic_hammer():
    return _svg(f'''
<circle cx="75" cy="24" r="8" fill="none" stroke="{INK}" stroke-width="2.4"/>
<line x1="75" y1="32" x2="75" y2="80" stroke="{INK}" stroke-width="2.6"/>
<path d="M75 46 L60 60" stroke="{INK}" stroke-width="2.8" stroke-linecap="round"/>
<path d="M60 60 L64 40" stroke="{CLAY}" stroke-width="5.5" stroke-linecap="round"/>
<path d="M75 46 L90 60" stroke="{INK}" stroke-width="2.8" stroke-linecap="round"/>
<path d="M90 60 L86 40" stroke="{CLAY}" stroke-width="5.5" stroke-linecap="round"/>''',
                "Rosca martelo")


def ic_bench():
    return _svg(f'''
<line x1="18" y1="96" x2="120" y2="96" stroke="{GREY}" stroke-width="2"/>
<line x1="34" y1="88" x2="96" y2="88" stroke="{INK}" stroke-width="3"/>
<circle cx="40" cy="80" r="8" fill="none" stroke="{INK}" stroke-width="2.4"/>
<path d="M70 88 L70 54" stroke="{INK}" stroke-width="2.6"/>
<line x1="50" y1="54" x2="90" y2="54" stroke="{CLAY}" stroke-width="5" stroke-linecap="round"/>
<circle cx="50" cy="54" r="6" fill="none" stroke="{INK}" stroke-width="2.2"/>
<circle cx="90" cy="54" r="6" fill="none" stroke="{INK}" stroke-width="2.2"/>''',
                "Supino")


def ic_fly():
    return _svg(f'''
<circle cx="75" cy="26" r="8" fill="none" stroke="{INK}" stroke-width="2.4"/>
<line x1="75" y1="34" x2="75" y2="82" stroke="{INK}" stroke-width="2.6"/>
<path d="M75 50 Q52 50 44 60" fill="none" stroke="{CLAY}" stroke-width="5" stroke-linecap="round"/>
<path d="M75 50 Q98 50 106 60" fill="none" stroke="{CLAY}" stroke-width="5" stroke-linecap="round"/>
<line x1="40" y1="58" x2="40" y2="70" stroke="{INK}" stroke-width="3.4" stroke-linecap="round"/>
<line x1="110" y1="58" x2="110" y2="70" stroke="{INK}" stroke-width="3.4" stroke-linecap="round"/>''',
                "Crucifixo")


def ic_pulldown():
    return _svg(f'''
<line x1="40" y1="10" x2="110" y2="10" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>
<line x1="55" y1="10" x2="62" y2="40" stroke="{INK}" stroke-width="2.4"/>
<line x1="95" y1="10" x2="88" y2="40" stroke="{INK}" stroke-width="2.4"/>
<circle cx="75" cy="50" r="8" fill="none" stroke="{INK}" stroke-width="2.4"/>
<path d="M62 40 L75 58" stroke="{CLAY}" stroke-width="5" stroke-linecap="round"/>
<path d="M88 40 L75 58" stroke="{CLAY}" stroke-width="5" stroke-linecap="round"/>
<line x1="75" y1="58" x2="75" y2="96" stroke="{INK}" stroke-width="2.6"/>''',
                "Puxada")


def ic_row():
    return _svg(f'''
<circle cx="42" cy="40" r="8" fill="none" stroke="{INK}" stroke-width="2.4"/>
<path d="M42 48 L80 60" stroke="{INK}" stroke-width="2.6"/>
<path d="M80 60 L58 60" stroke="{CLAY}" stroke-width="5" stroke-linecap="round"/>
<line x1="56" y1="54" x2="56" y2="66" stroke="{INK}" stroke-width="3.4" stroke-linecap="round"/>
<path d="M80 60 L96 96" stroke="{INK}" stroke-width="2.6"/>''',
                "Remada")


def ic_press():
    return _svg(f'''
<circle cx="75" cy="40" r="8" fill="none" stroke="{INK}" stroke-width="2.4"/>
<line x1="75" y1="48" x2="75" y2="96" stroke="{INK}" stroke-width="2.6"/>
<path d="M75 56 L58 40" stroke="{CLAY}" stroke-width="5.5" stroke-linecap="round"/>
<path d="M75 56 L92 40" stroke="{CLAY}" stroke-width="5.5" stroke-linecap="round"/>
<line x1="50" y1="30" x2="66" y2="30" stroke="{INK}" stroke-width="3.4" stroke-linecap="round"/>
<line x1="84" y1="30" x2="100" y2="30" stroke="{INK}" stroke-width="3.4" stroke-linecap="round"/>''',
                "Desenvolvimento")


def ic_lateral():
    return _svg(f'''
<circle cx="75" cy="34" r="8" fill="none" stroke="{INK}" stroke-width="2.4"/>
<line x1="75" y1="42" x2="75" y2="92" stroke="{INK}" stroke-width="2.6"/>
<path d="M75 54 L48 52" stroke="{CLAY}" stroke-width="5.5" stroke-linecap="round"/>
<path d="M75 54 L102 52" stroke="{CLAY}" stroke-width="5.5" stroke-linecap="round"/>
<line x1="42" y1="48" x2="54" y2="56" stroke="{INK}" stroke-width="3.4" stroke-linecap="round"/>
<line x1="96" y1="56" x2="108" y2="48" stroke="{INK}" stroke-width="3.4" stroke-linecap="round"/>''',
                "Elevação lateral")


def ic_shrug():
    return _svg(f'''
<circle cx="75" cy="30" r="8" fill="none" stroke="{INK}" stroke-width="2.4"/>
<path d="M55 46 Q75 36 95 46" fill="none" stroke="{CLAY}" stroke-width="5.5" stroke-linecap="round"/>
<line x1="55" y1="46" x2="53" y2="92" stroke="{INK}" stroke-width="2.6"/>
<line x1="95" y1="46" x2="97" y2="92" stroke="{INK}" stroke-width="2.6"/>
<line x1="47" y1="92" x2="59" y2="92" stroke="{INK}" stroke-width="3.4" stroke-linecap="round"/>
<line x1="91" y1="92" x2="103" y2="92" stroke="{INK}" stroke-width="3.4" stroke-linecap="round"/>''',
                "Encolhimento")


def ic_bike():
    return _svg(f'''
<circle cx="45" cy="92" r="18" fill="none" stroke="{INK}" stroke-width="2.6"/>
<circle cx="105" cy="92" r="18" fill="none" stroke="{INK}" stroke-width="2.6"/>
<path d="M45 92 L72 92 L88 60 L60 60" fill="none" stroke="{INK}" stroke-width="2.6" stroke-linejoin="round"/>
<line x1="72" y1="92" x2="88" y2="60" stroke="{CLAY}" stroke-width="3"/>
<circle cx="72" cy="92" r="4" fill="{CLAY}"/>
<line x1="88" y1="60" x2="98" y2="52" stroke="{INK}" stroke-width="2.6" stroke-linecap="round"/>''',
                "Pedal")


def ic_stretch():
    return _svg(f'''
<circle cx="55" cy="34" r="8" fill="none" stroke="{INK}" stroke-width="2.4"/>
<path d="M55 42 Q70 70 95 78" fill="none" stroke="{CLAY}" stroke-width="4.5" stroke-linecap="round"/>
<path d="M55 42 L50 80" stroke="{INK}" stroke-width="2.6"/>
<path d="M95 78 L108 74" stroke="{INK}" stroke-width="2.6" stroke-linecap="round"/>''',
                "Alongamento")


def ic_rdl():
    return _svg(f'''
<circle cx="60" cy="24" r="8" fill="none" stroke="{INK}" stroke-width="2.4"/>
<path d="M60 32 L60 60 L90 96" fill="none" stroke="{INK}" stroke-width="2.6" stroke-linecap="round"/>
<line x1="70" y1="88" x2="110" y2="104" stroke="{CLAY}" stroke-width="5" stroke-linecap="round"/>
<circle cx="70" cy="88" r="6" fill="none" stroke="{INK}" stroke-width="2.2"/>
<circle cx="110" cy="104" r="6" fill="none" stroke="{INK}" stroke-width="2.2"/>
<line x1="60" y1="60" x2="52" y2="104" stroke="{INK}" stroke-width="2.6"/>''',
                "Levantamento terra romeno")


def ic_reverse_fly():
    return _svg(f'''
<circle cx="75" cy="26" r="8" fill="none" stroke="{INK}" stroke-width="2.4"/>
<line x1="75" y1="34" x2="75" y2="82" stroke="{INK}" stroke-width="2.6"/>
<path d="M75 50 Q52 46 42 34" fill="none" stroke="{CLAY}" stroke-width="5" stroke-linecap="round"/>
<path d="M75 50 Q98 46 108 34" fill="none" stroke="{CLAY}" stroke-width="5" stroke-linecap="round"/>
<line x1="38" y1="28" x2="46" y2="40" stroke="{INK}" stroke-width="3.4" stroke-linecap="round"/>
<line x1="112" y1="28" x2="104" y2="40" stroke="{INK}" stroke-width="3.4" stroke-linecap="round"/>''',
                "Crucifixo inverso")


def ic_glute():
    return _svg(f'''
<line x1="24" y1="100" x2="126" y2="100" stroke="{GREY}" stroke-width="2"/>
<circle cx="40" cy="88" r="8" fill="none" stroke="{INK}" stroke-width="2.4"/>
<path d="M40 96 L40 100 L70 100" fill="none" stroke="{INK}" stroke-width="2.6"/>
<path d="M70 100 Q95 100 95 78" fill="none" stroke="{CLAY}" stroke-width="5.5" stroke-linecap="round"/>
<line x1="40" y1="100" x2="40" y2="118" stroke="{INK}" stroke-width="2.6"/>''',
                "Elevação de quadril / glúteos")


# Divisão semanal do Protocolo Base (hipertrofia, força e composição corporal):
# Treinos A-E intercalados conforme a semana, com quinta e domingo como descanso.
PLANOS = {
    0: {"nome": "Treino A — Peito & Tríceps", "alvos": ["chest", "triceps", "delts"], "dur": "~55 min",
        "ex": [("Supino reto (barra/máquina)", "3x6-10", "Peitoral", ic_bench),
               ("Supino inclinado c/ halteres", "3x8-12", "Peitoral superior", ic_bench),
               ("Crucifixo / crossover", "3x10-15", "Peitoral (abertura)", ic_fly),
               ("Desenvolvimento complementar", "3x8-12", "Deltoides", ic_press),
               ("Tríceps na polia", "3x8-12", "Tríceps", ic_pushdown),
               ("Tríceps acima da cabeça", "3x10-15", "Tríceps (cabeça longa)", ic_pushdown)]},
    1: {"nome": "Treino B — Costas & Bíceps", "alvos": ["lats", "biceps", "forearm"], "dur": "~55 min",
        "ex": [("Puxada alta / barra assistida", "3x6-10", "Dorsais", ic_pulldown),
               ("Remada baixa", "3x8-12", "Costas (meio)", ic_row),
               ("Remada unilateral", "3x8-12", "Costas", ic_row),
               ("Pulldown braço estendido", "3x10-15", "Dorsais", ic_pulldown),
               ("Rosca direta", "3x8-12", "Bíceps", ic_curl),
               ("Rosca alternada / martelo", "3x10-15", "Bíceps & antebraço", ic_hammer)]},
    2: {"nome": "Treino C — Pernas completas", "alvos": ["quads", "glutes", "hamstrings", "calves"], "dur": "~55 min",
        "ex": [("Agachamento / leg press", "3x6-10", "Quadríceps & glúteos", ic_squat),
               ("Cadeira extensora", "3x10-15", "Quadríceps (pico)", ic_legext),
               ("Mesa flexora", "3x8-12", "Isquiotibiais", ic_legcurl),
               ("Levantamento terra romeno", "3x8-12", "Posterior de coxa", ic_rdl),
               ("Panturrilha", "4x10-15", "Gastrocnêmio & sóleo", ic_calf),
               ("Complementar de glúteos", "3x10-15", "Glúteos", ic_glute)]},
    3: {"nome": "Descanso / atividade leve", "alvos": [], "dur": "20-30 min",
        "ex": [("Mobilidade de quadril/ombro", "8-10 min", "Amplitude", ic_stretch),
               ("Alongamento posterior", "5 min", "Cadeia posterior", ic_stretch),
               ("Caminhada leve", "15-20 min", "Recuperação", ic_stretch)]},
    4: {"nome": "Treino D — Ombros, Peito & Braços", "alvos": ["delts", "chest", "biceps", "triceps"], "dur": "~50 min",
        "ex": [("Desenvolvimento (halteres/máquina)", "3x6-10", "Deltoides", ic_press),
               ("Elevação lateral", "3x10-15", "Deltoide lateral", ic_lateral),
               ("Crucifixo inverso", "3x10-15", "Deltoide posterior", ic_reverse_fly),
               ("Supino inclinado", "3x8-12", "Peitoral superior", ic_bench),
               ("Rosca bíceps", "3x10-12", "Bíceps", ic_curl),
               ("Tríceps na polia", "3x10-12", "Tríceps", ic_pushdown)]},
    5: {"nome": "Treino E — Pernas & Costas complementar", "alvos": ["quads", "lats", "calves"], "dur": "~55 min",
        "ex": [("Leg press", "3x8-12", "Quadríceps & glúteos", ic_legpress),
               ("Agachamento / hack squat", "3x8-12", "Quadríceps", ic_squat),
               ("Mesa flexora", "3x10-15", "Isquiotibiais", ic_legcurl),
               ("Remada", "3x8-12", "Costas", ic_row),
               ("Puxada", "3x8-12", "Dorsais", ic_pulldown),
               ("Panturrilha", "3x10-15", "Gastrocnêmio & sóleo", ic_calf)]},
    6: {"nome": "Descanso", "alvos": [], "dur": "dia todo",
        "ex": [("Descanso total", "-", "Recuperação completa", ic_stretch)]},
}


def treino_do_dia(d):
    return PLANOS[d.weekday()]


_REGIOES = {
    "chest": ("f", [(52, 60, 9, 6), (74, 60, 9, 6)]),
    "delts": ("f", [(44, 54, 6, 6), (82, 54, 6, 6)]),
    "biceps": ("f", [(40, 74, 5, 10), (86, 74, 5, 10)]),
    "forearm": ("f", [(37, 98, 4, 10), (89, 98, 4, 10)]),
    "quads": ("f", [(50, 120, 7, 20), (76, 120, 7, 20)]),
    "traps": ("b", [(63, 52, 14, 7)]),
    "lats": ("b", [(50, 74, 8, 14), (76, 74, 8, 14)]),
    "triceps": ("b", [(40, 74, 5, 11), (86, 74, 5, 11)]),
    "glutes": ("b", [(56, 100, 9, 7), (70, 100, 9, 7)]),
    "hamstrings": ("b", [(52, 124, 7, 16), (74, 124, 7, 16)]),
    "calves": ("b", [(52, 160, 5, 12), (74, 160, 5, 12)]),
}


def _silhueta(cx_off):
    return (f'''
<circle cx="{cx_off + 63}" cy="34" r="9" fill="none" stroke="{INK}" stroke-width="2"/>
<path d="M{cx_off + 48} 46 Q{cx_off + 63} 42 {cx_off + 78} 46 L{cx_off + 80} 92
         Q{cx_off + 63} 98 {cx_off + 46} 92 Z" fill="none" stroke="{INK}" stroke-width="2"/>
<line x1="{cx_off + 46}" y1="50" x2="{cx_off + 34}" y2="92" stroke="{INK}" stroke-width="2"/>
<line x1="{cx_off + 80}" y1="50" x2="{cx_off + 92}" y2="92" stroke="{INK}" stroke-width="2"/>
<path d="M{cx_off + 52} 92 L{cx_off + 50} 175 M{cx_off + 74} 92 L{cx_off + 76} 175"
      stroke="{INK}" stroke-width="2" fill="none"/>''')


def mapa_muscular(alvos):
    front, back = "", ""
    for nome, (lado, elips) in _REGIOES.items():
        cor = CLAY if nome in alvos else GREY
        op = "0.9" if nome in alvos else "0.18"
        for (cx, cy, rx, ry) in elips:
            e = f'<ellipse cx="{{cx}}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{cor}" opacity="{op}"/>'
            if lado == "f":
                front += e.format(cx=cx)
            else:
                back += e.format(cx=cx + 147)
    return (f'<svg viewBox="0 0 300 200" xmlns="http://www.w3.org/2000/svg" '
            f'aria-label="Mapa muscular do dia">'
            f'<text x="63" y="14" font-size="11" fill="{SOFT}" text-anchor="middle" '
            f'font-family="-apple-system,sans-serif">Frente</text>'
            f'<text x="210" y="14" font-size="11" fill="{SOFT}" text-anchor="middle" '
            f'font-family="-apple-system,sans-serif">Costas</text>'
            f'{_silhueta(0)}{front}{_silhueta(147)}{back}</svg>')
