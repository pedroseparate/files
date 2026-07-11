#!/usr/bin/env python3
"""
Insight Engine Simulation — Momentum
Leitura apenas do Firestore momentum-br. Nenhuma escrita.
Simula RN 27/28/29/32/33/34/35/36 + fallback RN37.
RN 30 e RN 31: DISABLED.
"""

import json, ssl, urllib.request, math
from collections import defaultdict, Counter
from datetime import datetime

# ── AUTH ────────────────────────────────────────────────────────────────────
with open('/Users/ernanda/.config/configstore/firebase-tools.json') as f:
    _cfg = json.load(f)
_TOKEN = _cfg['tokens']['access_token']
_CTX = ssl.create_default_context()
_CTX.check_hostname = False
_CTX.verify_mode = ssl.CERT_NONE
_BASE = "https://firestore.googleapis.com/v1/projects/momentum-br/databases/(default)/documents"

def _get(url):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {_TOKEN}"})
    with urllib.request.urlopen(req, context=_CTX) as resp:
        return json.loads(resp.read())

def _v(field):
    """Deserialise Firestore REST value."""
    if not field: return None
    for k, val in field.items():
        if k in ('stringValue', 'booleanValue'): return val
        if k in ('doubleValue', 'integerValue'): return float(val)
        if k == 'nullValue': return None
        if k == 'mapValue':  return {kk: _v(vv) for kk, vv in val.get('fields', {}).items()}
        if k == 'arrayValue': return [_v(i) for i in val.get('values', [])]
    return None

def fetch_all(collection):
    docs, pageToken = [], None
    while True:
        url = f"{_BASE}/{collection}?pageSize=300"
        if pageToken: url += f"&pageToken={pageToken}"
        r = _get(url)
        docs.extend(r.get('documents', []))
        pageToken = r.get('nextPageToken')
        if not pageToken: break
    return docs

# ── LOAD DATA ────────────────────────────────────────────────────────────────
print("Carregando alunos…")
students_raw = fetch_all('students')
students = {}
for doc in students_raw:
    sid = doc['name'].split('/')[-1]
    f = doc['fields']
    students[sid] = {
        'id': sid,
        'name': _v(f.get('name')) or sid,
        'ritmo_estado_atual': _v(f.get('ritmo_estado')),
        'dim_dominante': _v(f.get('dim_dominante')),
        'modelo': _v(f.get('modelo_periodizacao')) or 'linear',
        'mesociclo_inicio': _v(f.get('mesociclo_inicio')),
        'semanas_total': int(_v(f.get('semanas_total')) or 8),
        'scores': _v(f.get('scores')) or {},
    }

print("Carregando sessões…")
sessions_raw = fetch_all('sessions')
sessions_by_student = defaultdict(list)
for doc in sessions_raw:
    f = doc['fields']
    sid = _v(f.get('student_id'))
    if not sid: continue
    exs = _v(f.get('exercicios')) or []
    vol_load = sum(
        float(ex.get('kg') or 0) * float(ex.get('r') or 0) * float(ex.get('s') or 0)
        for ex in exs
        if float(ex.get('kg') or 0) > 0
    )
    sessions_by_student[sid].append({
        'id':             doc['name'].split('/')[-1],
        'date':           _v(f.get('date') or f.get('data')) or '',
        'semana':         int(_v(f.get('semana')) or 0),
        'pse':            float(_v(f.get('pse')) or 0),
        'ic_neural':      float(_v(f.get('ic_neural')) or 0),
        'ic_mecanica':    float(_v(f.get('ic_mecanica')) or 0),
        'ic_metabolica':  float(_v(f.get('ic_metabolica')) or 0),
        'ic_executado':   float(_v(f.get('ic_executado') or _v(f.get('indice_carga')) or 0),),
        'ic_planejado':   float(_v(f.get('ic_planejado')) or 0),
        'ratio_adaptacao': float(_v(f.get('ratio_adaptacao')) or 1.0),
        'tipo':           _v(f.get('tipo')) or '',
        'vol_load':       vol_load,
        'exercicios':     exs,
    })

for sid in sessions_by_student:
    sessions_by_student[sid].sort(key=lambda x: (x['date'], x['semana']))

total_sessions = sum(len(v) for v in sessions_by_student.values())
print(f"  {len(students)} alunos · {total_sessions} sessões")

# ── HELPERS (espelham lógica de momentum-aluno.html) ─────────────────────────

def dim_percentile(history_vals, current_val):
    """Percentil rolante: % de histórico <= current (buildHeroCard: dimPercentile)."""
    if len(history_vals) < 4: return 0.5
    return sum(1 for v in history_vals if v <= current_val) / len(history_vals)

def dim_trend(weekly_avgs):
    """Tendência 4 vs 4 anteriores (buildHeroCard: dimTrend)."""
    if len(weekly_avgs) < 8: return 0.0
    r4, p4 = weekly_avgs[-4:], weekly_avgs[-8:-4]
    ar, ap = sum(r4)/4, sum(p4)/4
    return (ar - ap) / max(ap, 0.001)

def dim_estado(p, t):
    """buildHeroCard: dimEstado."""
    if p <= 0.25 or t <= -0.15: return 'queda'
    if p >= 0.70 and t >= 0.05:  return 'alta'
    return 'estavel'

def ritmo_from_estados(eN, eM, eMet, avg_pse, avg_ratio):
    """
    Mapeamento approximado: dimEstados + PSE/ratio → ritmo_estado.
    Declaração de proxy: não existe função equivalente no app; esta lógica
    é uma interpretação razoável baseada nos estados dimensionais.
    """
    queda = any(e == 'queda' for e in (eN, eM, eMet))
    alta  = any(e == 'alta'  for e in (eN, eM, eMet))
    if queda:
        return 'sobrecarga' if (avg_pse >= 7.5 or avg_ratio < 0.85) else 'baixo'
    if alta: return 'alta'
    return 'estavel'

def calc_streak_at(sessions_sorted):
    """Streak de aderência: sessões consecutivas com gap ≤ 3 dias (buildHeroCard)."""
    dates = sorted(set(s['date'] for s in sessions_sorted if s['date']))
    if not dates: return 0
    dates_desc = list(reversed(dates))
    streak = 1
    for i in range(1, len(dates_desc)):
        try:
            prev = datetime.strptime(dates_desc[i-1], '%Y-%m-%d')
            curr = datetime.strptime(dates_desc[i],   '%Y-%m-%d')
            gap  = (prev - curr).days
        except ValueError:
            break
        if gap <= 3: streak += 1
        else: break
    return streak

# ── WEEKLY AGGREGATION ───────────────────────────────────────────────────────

def build_weekly(sessions):
    """
    Agrega sessões por semana, calcula percentis/tendências/ritmo retroativamente.
    Retorna dict {semana: {métricas}}.
    """
    by_week = defaultdict(list)
    for s in sessions:
        if s['semana'] > 0:
            by_week[s['semana']].append(s)
    if not by_week: return {}

    weeks = sorted(by_week.keys())
    hist_n = []; hist_m = []; hist_met = []; hist_vol = []
    result = {}

    for w in weeks:
        ws = by_week[w]
        avg = lambda key: sum(s[key] for s in ws) / len(ws)

        a_n   = avg('ic_neural')
        a_m   = avg('ic_mecanica')
        a_met = avg('ic_metabolica')
        a_pse = avg('pse')
        a_rat = avg('ratio_adaptacao')
        vol   = sum(s['vol_load'] for s in ws)

        pN   = dim_percentile(hist_n,   a_n)
        pM   = dim_percentile(hist_m,   a_m)
        pMet = dim_percentile(hist_met, a_met)

        hist_n.append(a_n);   hist_m.append(a_m)
        hist_met.append(a_met); hist_vol.append(vol)

        tN   = dim_trend(hist_n)
        tM   = dim_trend(hist_m)
        tMet = dim_trend(hist_met)

        eN   = dim_estado(pN,   tN)
        eM   = dim_estado(pM,   tM)
        eMet = dim_estado(pMet, tMet)

        ritmo = ritmo_from_estados(eN, eM, eMet, a_pse, a_rat)

        # Sessões de força desta semana
        forca_sess = [s for s in ws if 'força' in s['tipo'].lower() or 'forca' in s['tipo'].lower()
                      or any(ex.get('tipo_serie') == 'forca_pura' for ex in s['exercicios'])]

        result[w] = {
            'semana':   w,
            'sessions': ws,
            'n_sess':   len(ws),
            'dates':    [s['date'] for s in ws if s['date']],
            'tipos':    [s['tipo'] for s in ws if s['tipo']],
            'avg_ic_n': a_n, 'avg_ic_m': a_m, 'avg_ic_met': a_met,
            'avg_pse':  a_pse,
            'avg_ratio': a_rat,
            'vol_load': vol,
            'vol_hist': list(hist_vol),
            'pN': pN, 'pM': pM, 'pMet': pMet,
            'tN': tN, 'tM': tM, 'tMet': tMet,
            'eN': eN, 'eM': eM, 'eMet': eMet,
            'ritmo':    ritmo,
            'forca_sess': forca_sess,
            'ic_n_hist':   list(hist_n),
            'ic_m_hist':   list(hist_m),
            'ic_met_hist': list(hist_met),
        }
    return result

# ── RN EVALUATORS ────────────────────────────────────────────────────────────

def rn27(wd, week):
    """Acúmulo neural sustentado: pN ≥ 0.65 por ≥ 3 semanas consecutivas."""
    weeks = sorted(wd.keys())
    idx = weeks.index(week) if week in weeks else -1
    if idx < 2: return None
    last3 = weeks[max(0, idx-2): idx+1]
    if len(last3) < 3: return None
    if not all(wd[w]['pN'] >= 0.65 for w in last3): return None
    # Conta semanas consecutivas totais
    consec = 3
    for i in range(idx-3, -1, -1):
        if wd[weeks[i]]['pN'] >= 0.65: consec += 1
        else: break
    pN = wd[week]['pN']
    R = min(1.0, 0.6 * min(1.0, (pN - 0.65)/0.35) + 0.4 * min(1.0, (consec-3)/5))
    return {'rn': 27, 'name': 'Acúmulo neural sustentado', 'A': 0.3, 'R': R,
            'detail': f'pN={pN:.2f} · {consec} semanas'}

def rn28(wd, week, modelo):
    """Aderência ondulatória [PROXY DUP]: ≥2 tipos distintos em ≥2 semanas."""
    if modelo != 'dup': return None
    weeks = sorted(wd.keys())
    idx = weeks.index(week) if week in weeks else -1
    if idx < 1: return None
    last2 = weeks[max(0, idx-1): idx+1]
    tipos = set(t for w in last2 for t in wd[w]['tipos'])
    n = len(tipos)
    if n < 2: return None
    R = min(1.0, n / 3)
    return {'rn': 28, 'name': 'Aderência ondulatória [PROXY]', 'A': 0.6, 'R': R,
            'detail': f'{n} tipos distintos: {", ".join(sorted(tipos)[:4])}'}

def rn29(wd, week):
    """Crescimento mecânico: VL semanal +5% em 3 semanas consecutivas."""
    weeks = sorted(wd.keys())
    idx = weeks.index(week) if week in weeks else -1
    if idx < 2: return None
    last3 = weeks[max(0, idx-2): idx+1]
    if len(last3) < 3: return None
    vols = [wd[w]['vol_load'] for w in last3]
    if vols[0] <= 0 or vols[1] <= 0: return None
    g1 = (vols[1] - vols[0]) / vols[0]
    g2 = (vols[2] - vols[1]) / vols[1]
    if g1 < 0.05 or g2 < 0.05: return None
    total_g = (vols[2] - vols[0]) / vols[0]
    R = min(1.0, total_g / 0.15)
    return {'rn': 29, 'name': 'Crescimento mecânico', 'A': 0.3, 'R': R,
            'detail': f'{vols[0]:.0f}→{vols[1]:.0f}→{vols[2]:.0f} (+{total_g*100:.1f}%)'}

def rn32(wd, week, all_sessions):
    """Streak de aderência ≥ 7 dias."""
    weeks = sorted(wd.keys())
    idx = weeks.index(week) if week in weeks else -1
    sess_so_far = [s for w in weeks[:idx+1] for s in wd[w]['sessions']]
    streak = calc_streak_at(sess_so_far)
    if streak < 7: return None
    R = min(1.0, (streak - 7) / 14)
    return {'rn': 32, 'name': 'Streak de aderência', 'A': 0.3, 'R': R,
            'detail': f'{streak} dias'}

def rn33(wd, week):
    """Percentil cruzando 50 ou 75 pela primeira vez no mesociclo."""
    weeks = sorted(wd.keys())
    idx = weeks.index(week) if week in weeks else -1
    if idx < 1: return None
    prev, curr = wd[weeks[idx-1]], wd[week]
    crossings = []
    for dim, pc, pp in [('N', curr['pN'], prev['pN']),
                         ('M', curr['pM'], prev['pM']),
                         ('Met', curr['pMet'], prev['pMet'])]:
        if pp < 0.75 <= pc: crossings.append((dim, 75, 1.0))
        elif pp < 0.50 <= pc: crossings.append((dim, 50, 0.7))
    if not crossings: return None
    best = max(crossings, key=lambda x: x[2])
    detail = ' | '.join(f'{c[0]} cruzou {c[1]}' for c in crossings)
    return {'rn': 33, 'name': 'Percentil cruzando threshold', 'A': 1.0, 'R': best[2],
            'detail': detail}

def rn34(wd, week):
    """Resiliência à carga: alta intensidade com PSE ≤ média anterior."""
    curr = wd[week]
    hi = curr['forca_sess']
    if not hi: return None
    pse_now = sum(s['pse'] for s in hi) / len(hi)
    weeks = sorted(wd.keys())
    idx = weeks.index(week)
    prior_hi = [s for w in weeks[:idx] for s in wd[w]['forca_sess']]
    if len(prior_hi) < 4: return None
    pse_prev = sum(s['pse'] for s in prior_hi[-4:]) / 4
    if pse_now > pse_prev: return None
    R = min(1.0, (pse_prev - pse_now) / 2)
    return {'rn': 34, 'name': 'Resiliência à carga', 'A': 1.0, 'R': R,
            'detail': f'PSE atual={pse_now:.1f} vs prev4={pse_prev:.1f}'}

def rn35(wd, week):
    """Equilíbrio dimensional: var(pN,pM,pMet) ≤ 0.15 por ≥ 2 semanas."""
    weeks = sorted(wd.keys())
    idx = weeks.index(week) if week in weeks else -1
    if idx < 1: return None
    last2 = weeks[max(0, idx-1): idx+1]
    for w in last2:
        d = wd[w]
        vals = [d['pN'], d['pM'], d['pMet']]
        mu = sum(vals) / 3
        if sum((x-mu)**2 for x in vals)/3 > 0.15: return None
    d = wd[week]
    vals = [d['pN'], d['pM'], d['pMet']]
    mu = sum(vals)/3; var = sum((x-mu)**2 for x in vals)/3
    R = min(1.0, (0.15 - var) / 0.15)
    return {'rn': 35, 'name': 'Equilíbrio dimensional', 'A': 0.6, 'R': R,
            'detail': f'var={var:.3f} (N={d["pN"]:.2f} M={d["pM"]:.2f} Met={d["pMet"]:.2f})'}

def rn36(wd, week):
    """Retorno de fadiga: ritmo anterior ∈ {baixo,sobrecarga} → atual ∈ {estavel,alta}."""
    weeks = sorted(wd.keys())
    idx = weeks.index(week) if week in weeks else -1
    if idx < 1: return None
    pr = wd[weeks[idx-1]]['ritmo']
    cr = wd[week]['ritmo']
    if pr not in ('baixo', 'sobrecarga'): return None
    if cr not in ('estavel', 'alta'): return None
    return {'rn': 36, 'name': 'Retorno de fadiga', 'A': 1.0, 'R': 1.0,
            'detail': f'{pr} → {cr}'}

def fallback_signals(wd, week):
    """RN 37: sinais de atenção quando nenhum fato positivo dispara."""
    curr = wd[week]; signals = []
    weeks = sorted(wd.keys()); idx = weeks.index(week)
    if curr['ritmo'] in ('baixo', 'sobrecarga'):
        signals.append(f"ritmo={curr['ritmo']}")
    if idx >= 1:
        prev = wd[weeks[idx-1]]
        if curr['n_sess'] <= 1 and prev['n_sess'] <= 1:
            signals.append(f"baixa aderência ({curr['n_sess']}+{prev['n_sess']} sess/2sem)")
    low_ratio = [s for s in curr['sessions'] if s['ratio_adaptacao'] < 0.80]
    if len(low_ratio) >= 2:
        ar = sum(s['ratio_adaptacao'] for s in low_ratio)/len(low_ratio)
        signals.append(f"divergência PSE/IC (ratio={ar:.2f})")
    return signals

def score(R, A, E): return R*0.45 + A*0.35 + E*0.20

# ── SIMULATE ─────────────────────────────────────────────────────────────────

def simulate(student_id, student):
    sessions = sessions_by_student.get(student_id, [])
    if not sessions: return None
    wd = build_weekly(sessions)
    if not wd: return None

    modelo = student['modelo']
    weeks = sorted(wd.keys())
    recent_rns = []   # últimas 2 headlines (rn ids)
    results = []

    for week in weeks:
        candidates = []
        for fn in [
            lambda: rn27(wd, week),
            lambda: rn28(wd, week, modelo),
            lambda: rn29(wd, week),
            lambda: rn32(wd, week, sessions),
            lambda: rn33(wd, week),
            lambda: rn34(wd, week),
            lambda: rn35(wd, week),
            lambda: rn36(wd, week),
        ]:
            f = fn()
            if f: candidates.append(f)

        # Anti-repetição
        last2_rns = set(recent_rns[-2:])
        scored = []
        for f in candidates:
            A_val = f['A']
            E = 1.0 if A_val == 1.0 else (0.0 if f['rn'] in last2_rns else 1.0)
            scored.append({**f, 'E': E, 'score': score(f['R'], A_val, E)})

        winner = max(scored, key=lambda x: x['score']) if scored else None

        if winner:
            recent_rns.append(winner['rn'])
            tipo = 'fato'
        else:
            fb = fallback_signals(wd, week)
            winner = None
            tipo = 'alerta' if fb else 'neutro'

        curr = wd[week]
        dim_lead = max(('N','M','Met'), key=lambda d: {'N':curr['pN'],'M':curr['pM'],'Met':curr['pMet']}[d])

        results.append({
            'semana':   week,
            'n_sess':   curr['n_sess'],
            'ritmo':    curr['ritmo'],
            'pN':curr['pN'], 'pM':curr['pM'], 'pMet':curr['pMet'],
            'avg_pse':  curr['avg_pse'],
            'vol_load': curr['vol_load'],
            'candidates': scored,
            'winner':   winner,
            'fallback': fallback_signals(wd, week) if tipo == 'alerta' else [],
            'tipo':     tipo,
            'dim_lead': dim_lead,
        })
    return results

# ── REPORT ───────────────────────────────────────────────────────────────────
RN_NAMES = {
    27: 'Acúmulo neural sustentado',
    28: 'Aderência ondulatória [PROXY]',
    29: 'Crescimento mecânico',
    32: 'Streak de aderência',
    33: 'Percentil cruzando threshold',
    34: 'Resiliência à carga',
    35: 'Equilíbrio dimensional',
    36: 'Retorno de fadiga',
}

L = []  # linhas do relatório
all_results = {}
all_fired = Counter(); all_won = Counter()
n_pos = n_alerta = n_neutro = 0
scores_all = []
by_modelo = {'linear': Counter(), 'block': Counter(), 'dup': Counter()}

L += [
    "# Insight Engine — Simulação com Dados Reais",
    "",
    f"**Execução:** 2026-05-28  |  **Alunos:** {len(students)}  |  **Sessões:** {total_sessions}",
    "",
    "## Premissas e proxies desta simulação",
    "",
    "| # | Decisão | Justificativa |",
    "|---|---|---|",
    "| 1 | `semana_deload = false` em todos os alunos | `fase_mesociclo` ausente no Firestore (0/389) |",
    "| 2 | `ritmo_estado` histórico recalculado via `dimEstado(p,t)` + mapeamento dimensional | `ritmo_estado` nunca salvo em sessions (0/389) |",
    "| 3 | RN 30 e RN 31 **DISABLED** | `fc_pos_sessao`, `rir`, `cadencia` ausentes |",
    "| 4 | RN 28 usa **PROXY**: variação de `sessions.tipo` como indicador de aderência DUP | Sem prescrição-calendário no Firestore |",
    "| 5 | Percentil = rolante por semana (histórico acumulado do próprio aluno) | Replica `dimPercentile` de `buildHeroCard` |",
    "| 6 | Streak calculado sobre todas as sessões até a semana corrente | Replica lógica de `buildHeroCard` |",
    "",
    "---",
    "",
    "## Parte 1 — Resultados por aluno, semana a semana",
    "",
]

for sid in sorted(students):
    s = students[sid]
    res = simulate(sid, s)
    if not res:
        L += [f"### {s['name']} — sem sessões", ""]
        continue
    all_results[sid] = res
    modelo = s['modelo']

    L += [
        f"### {s['name']} ({sid})",
        f"modelo: **{modelo}** · semanas analisadas: **{len(res)}** · ritmo atual no Firestore: `{s['ritmo_estado_atual']}`",
        "",
        "| Sem | n | Ritmo calc. | pN | pM | pMet | PSE | Fatos disparados | Headline | Score | Tipo |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]

    for r in res:
        cands = ' / '.join(f"RN{f['rn']}(R={f['R']:.2f},s={f['score']:.2f})" for f in r['candidates']) or '—'

        if r['winner']:
            w = r['winner']
            hl = f"**RN{w['rn']}** {w['name']} — {w['detail']}"
            sc = f"{w['score']:.3f}"
            tp = "✅"
            all_won[w['rn']] += 1; all_fired[w['rn']] += 1
            scores_all.append(w['score']); n_pos += 1
            by_modelo[modelo][w['rn']] += 1
            for f in r['candidates']:
                if f['rn'] != w['rn']: all_fired[f['rn']] += 1
        elif r['fallback']:
            hl = f"⚠ {' · '.join(r['fallback'])}"
            sc = "—"; tp = "⚠"; n_alerta += 1
            for f in r['candidates']: all_fired[f['rn']] += 1
        else:
            hl = f"○ neutro · {r['dim_lead']} lidera"
            sc = "—"; tp = "○"; n_neutro += 1
            for f in r['candidates']: all_fired[f['rn']] += 1

        L.append(
            f"| S{r['semana']} | {r['n_sess']} | {r['ritmo']} |"
            f" {r['pN']:.2f} | {r['pM']:.2f} | {r['pMet']:.2f} |"
            f" {r['avg_pse']:.1f} | {cands} | {hl} | {sc} | {tp} |"
        )
    L.append("")

# ── PARTE 2: NARRATIVA ───────────────────────────────────────────────────────
L += ["---", "", "## Parte 2 — Leitura narrativa (como o aluno leria)", ""]

def hl_text(r):
    if r['winner']:
        w = r['winner']
        rn = w['rn']
        d = w['detail']
        if rn == 27: return f"\"Neural consistente há {d.split('·')[1].strip()}\""
        if rn == 28: return f"\"Você está seguindo o plano DUP — {d}\""
        if rn == 29: return f"\"Volume crescendo há 3 semanas — {d}\""
        if rn == 32: return f"\"Sequência de {d} de treino\""
        if rn == 33: return f"\"Marco atingido: {d}\""
        if rn == 34: return f"\"Mais resistente à carga — {d}\""
        if rn == 35: return f"\"Dimensões equilibradas — {d}\""
        if rn == 36: return f"\"Virada: {d}\""
        return f"\"{w['name']}\""
    elif r['fallback']:
        return f"[ALERTA] {' · '.join(r['fallback'])}"
    else:
        return f"[neutro] {r['dim_lead']} lidera o percentil"

for sid in sorted(students):
    s = students[sid]
    res = all_results.get(sid)
    if not res: continue
    L.append(f"**{s['name']}** (modelo: {s['modelo']}):")
    L.append("")
    for r in res:
        icon = "✅" if r['tipo']=='fato' else ("⚠" if r['tipo']=='alerta' else "○")
        L.append(f"  S{r['semana']:>2} {icon}  {hl_text(r)}")
    L.append("")

# ── PARTE 3: AGREGADO ────────────────────────────────────────────────────────
total_weeks = n_pos + n_alerta + n_neutro
L += [
    "---", "",
    "## Parte 3 — Agregado",
    "",
    f"**Total semanas-aluno:** {total_weeks}",
    "",
    f"| Resultado | Contagem | % |",
    f"|---|---|---|",
    f"| ✅ Fato positivo | {n_pos} | {n_pos/total_weeks*100:.0f}% |",
    f"| ⚠ Alerta | {n_alerta} | {n_alerta/total_weeks*100:.0f}% |",
    f"| ○ Neutro | {n_neutro} | {n_neutro/total_weeks*100:.0f}% |",
    "",
    "### Frequência de fatos",
    "",
    "| RN | Nome | Disparou | Foi headline | Taxa win |",
    "|---|---|---|---|---|",
]

orphans = []
for rn in sorted(RN_NAMES):
    fired = all_fired[rn]; won = all_won[rn]
    if fired == 0: orphans.append(rn)
    rate = f"{won/fired*100:.0f}%" if fired > 0 else "—"
    L.append(f"| {rn} | {RN_NAMES[rn]} | {fired} | {won} | {rate} |")

L.append("")
if orphans:
    L.append(f"**Fatos ÓRFÃOS (nunca dispararam em nenhum aluno):** {', '.join(f'RN {r}' for r in orphans)}")
else:
    L.append("**Fatos ÓRFÃOS:** nenhum — todos dispararam em pelo menos 1 semana-aluno")
L.append("")

if scores_all:
    L += [
        "### Distribuição de scores das headlines vencedoras",
        "",
        f"| Stat | Valor |",
        f"|---|---|",
        f"| Mínimo | {min(scores_all):.3f} |",
        f"| Média  | {sum(scores_all)/len(scores_all):.3f} |",
        f"| Máximo | {max(scores_all):.3f} |",
        f"| Mediana | {sorted(scores_all)[len(scores_all)//2]:.3f} |",
        "",
    ]

L += [
    "### Headlines por modelo de periodização",
    "",
    "| RN | Nome | linear | block | dup |",
    "|---|---|---|---|---|",
]
for rn in sorted(RN_NAMES):
    L.append(f"| {rn} | {RN_NAMES[rn]} | {by_modelo['linear'][rn]} | {by_modelo['block'][rn]} | {by_modelo['dup'][rn]} |")
L.append("")

# ── PARTE 4: DIAGNÓSTICO ─────────────────────────────────────────────────────
L += ["---", "", "## Parte 4 — Diagnóstico e calibração", ""]

# Dominância
if all_won:
    top_rn = max(all_won, key=all_won.get)
    top_pct = all_won[top_rn]/n_pos*100 if n_pos > 0 else 0
    if top_pct > 40:
        L += [
            f"### ⚠ Dominância excessiva detectada",
            "",
            f"**RN {top_rn} ({RN_NAMES[top_rn]})** foi headline em **{all_won[top_rn]} semanas ({top_pct:.0f}%** dos fatos positivos).",
            "Possíveis causas: critério fácil de satisfazer + A baixo compensado por R alto, ou fatos concorrentes com A baixo sendo suprimidos pela anti-repetição.",
            "Recomendação: aumentar exigência de semanas consecutivas **ou** elevar A de fatos com dado igualmente rico (RN 35, RN 28).",
            "",
        ]

# Alunos presos em neutro/alerta
L.append("### Alunos com predominância de neutro/alerta")
L.append("")
L.append("| Aluno | Semanas | ✅ Fato | ⚠ Alerta | ○ Neutro | % sem fato |")
L.append("|---|---|---|---|---|---|")
for sid in sorted(students):
    res = all_results.get(sid)
    if not res: continue
    nf = sum(1 for r in res if r['tipo']=='fato')
    na = sum(1 for r in res if r['tipo']=='alerta')
    nn = sum(1 for r in res if r['tipo']=='neutro')
    pct_sem = (na+nn)/len(res)*100
    flag = " ⚠" if pct_sem > 60 else ""
    L.append(f"| {students[sid]['name']} | {len(res)} | {nf} | {na} | {nn} | {pct_sem:.0f}%{flag} |")
L.append("")

# Órfãos
if orphans:
    L += ["### Análise de fatos órfãos", ""]
    analyses = {
        34: "RN 34 exige ≥4 sessões anteriores do mesmo tipo de alta intensidade. Se poucos alunos têm periodização com 'Força' explícito no tipo, o critério nunca é satisfeito.",
        33: "RN 33 dispara apenas no cruzamento de fronteira — aluno que já estava acima de 50/75 desde o início do mesociclo nunca cruza.",
        36: "RN 36 exige queda prévia de ritmo. Em alunos com ritmo estável recalculado como 'estavel'/'alta' em todas as semanas, nunca dispara.",
        32: "RN 32 exige ≥7 dias consecutivos. Em alunos com menos de 7 sessões no histórico ou gaps frequentes, nunca dispara.",
    }
    for rn in orphans:
        if rn in analyses:
            L.append(f"- **RN {rn}**: {analyses[rn]}")
        else:
            L.append(f"- **RN {rn}**: causa não mapeada — verificar manualmente.")
    L.append("")

# Calibração
L += [
    "### Recomendações de calibração (sugestões — não implementar)",
    "",
]
if scores_all:
    avg_sc = sum(scores_all)/len(scores_all)
    if avg_sc < 0.35:
        L.append(f"- **Scores médios baixos ({avg_sc:.2f})**: fatos comuns (A=0.3) com R moderado geram scores < 0.30. "
                 "Considerar elevar A de RN 29 para 0.5 — crescimento de volume é dados concretos, não merece peso de 'comum'.")
    if avg_sc > 0.55:
        L.append(f"- **Scores médios altos ({avg_sc:.2f})**: fatos raros (A=1.0) dominam. "
                 "Verificar se RN 33/34/36 estão calibrados corretamente ou se disparando com facilidade excessiva.")

eq_won = all_won.get(35, 0); eq_fired = all_fired.get(35, 0)
if eq_fired > 0 and eq_won == 0:
    L.append("- **RN 35 (Equilíbrio)**: disparou mas nunca venceu. A=0.6 não compete com raros (A=1.0). "
             "Se equilíbrio dimensional é evento valioso, elevar A para 0.8 ou 1.0.")

rn28_won = all_won.get(28, 0)
if rn28_won > 0:
    L.append("- **RN 28 [PROXY]**: venceu com dado de proxy (variação de tipo, não conformidade real). "
             "Implementar prescrição-calendário para elevar confiabilidade antes de usar em produção.")

L += [
    "- **ritmo_estado recalculado** é uma aproximação heurística. Comparar com `students.ritmo_estado` atual "
    "dos 10 alunos como sanity check antes de usar RN 36 em produção.",
    "- **Semana 1–3**: percentis sempre 0.50 (dados históricos insuficientes para `dim_percentile`). "
    "Considerar suprimir fatos que dependem de percentil nas 3 primeiras semanas do mesociclo.",
    "",
    "---",
    "",
    "*Script de leitura apenas. Nenhum dado foi escrito no Firestore ou em arquivos de produção.*",
]

report = '\n'.join(L)
out_path = '/Users/ernanda/Downloads/files/insight_engine_report.md'
with open(out_path, 'w') as f:
    f.write(report)

print(f"\n✅ Relatório salvo: {out_path}")
print(f"   {total_weeks} semanas-aluno | {n_pos} fatos | {n_alerta} alertas | {n_neutro} neutros")
print(f"   Scores: min={min(scores_all):.3f} média={sum(scores_all)/len(scores_all):.3f} max={max(scores_all):.3f}" if scores_all else "   Sem scores")
print(f"   Órfãos: {orphans or 'nenhum'}")
if all_won:
    top_rn = max(all_won, key=all_won.get)
    print(f"   Dominante: RN {top_rn} ({all_won[top_rn]} headlines)")
