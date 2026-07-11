# Insight Engine — Simulação com Dados Reais

**Execução:** 2026-05-28  |  **Alunos:** 10  |  **Sessões:** 389

## Premissas e proxies desta simulação

| # | Decisão | Justificativa |
|---|---|---|
| 1 | `semana_deload = false` em todos os alunos | `fase_mesociclo` ausente no Firestore (0/389) |
| 2 | `ritmo_estado` histórico recalculado via `dimEstado(p,t)` + mapeamento dimensional | `ritmo_estado` nunca salvo em sessions (0/389) |
| 3 | RN 30 e RN 31 **DISABLED** | `fc_pos_sessao`, `rir`, `cadencia` ausentes |
| 4 | RN 28 usa **PROXY**: variação de `sessions.tipo` como indicador de aderência DUP | Sem prescrição-calendário no Firestore |
| 5 | Percentil = rolante por semana (histórico acumulado do próprio aluno) | Replica `dimPercentile` de `buildHeroCard` |
| 6 | Streak calculado sobre todas as sessões até a semana corrente | Replica lógica de `buildHeroCard` |

---

## Parte 1 — Resultados por aluno, semana a semana

### Ana Beatriz (ana_beatriz)
modelo: **linear** · semanas analisadas: **13** · ritmo atual no Firestore: `estavel`

| Sem | n | Ritmo calc. | pN | pM | pMet | PSE | Fatos disparados | Headline | Score | Tipo |
|---|---|---|---|---|---|---|---|---|---|---|
| S1 | 1 | estavel | 0.50 | 0.50 | 0.50 | 6.4 | — | ○ neutro · N lidera | — | ○ |
| S2 | 4 | estavel | 0.50 | 0.50 | 0.50 | 6.5 | RN35(R=1.00,s=0.86) | **RN35** Equilíbrio dimensional — var=0.000 (N=0.50 M=0.50 Met=0.50) | 0.860 | ✅ |
| S3 | 4 | estavel | 0.50 | 0.50 | 0.50 | 6.7 | RN32(R=0.14,s=0.37) / RN35(R=1.00,s=0.66) | **RN35** Equilíbrio dimensional — var=0.000 (N=0.50 M=0.50 Met=0.50) | 0.660 | ✅ |
| S4 | 4 | estavel | 0.50 | 0.50 | 0.50 | 6.2 | RN32(R=0.43,s=0.50) / RN35(R=1.00,s=0.66) | **RN35** Equilíbrio dimensional — var=0.000 (N=0.50 M=0.50 Met=0.50) | 0.660 | ✅ |
| S5 | 4 | baixo | 0.25 | 0.25 | 0.25 | 6.1 | RN32(R=0.71,s=0.63) / RN35(R=1.00,s=0.66) | **RN35** Equilíbrio dimensional — var=0.000 (N=0.25 M=0.25 Met=0.25) | 0.660 | ✅ |
| S6 | 4 | estavel | 1.00 | 1.00 | 1.00 | 7.0 | RN32(R=1.00,s=0.76) / RN33(R=1.00,s=1.00) / RN35(R=1.00,s=0.66) / RN36(R=1.00,s=1.00) | **RN33** Percentil cruzando threshold — N cruzou 75 | M cruzou 75 | Met cruzou 75 | 1.000 | ✅ |
| S7 | 4 | estavel | 1.00 | 1.00 | 1.00 | 7.2 | RN29(R=1.00,s=0.76) / RN32(R=1.00,s=0.76) / RN35(R=1.00,s=0.66) | **RN29** Crescimento mecânico — 29466→44418→47094 (+59.8%) | 0.755 | ✅ |
| S8 | 4 | alta | 1.00 | 1.00 | 1.00 | 7.3 | RN27(R=0.60,s=0.57) / RN29(R=0.77,s=0.45) / RN32(R=1.00,s=0.76) / RN35(R=1.00,s=0.86) | **RN35** Equilíbrio dimensional — var=0.000 (N=1.00 M=1.00 Met=1.00) | 0.860 | ✅ |
| S9 | 3 | alta | 1.00 | 1.00 | 1.00 | 7.7 | RN27(R=0.68,s=0.61) / RN32(R=1.00,s=0.76) / RN35(R=1.00,s=0.66) | **RN32** Streak de aderência — 32 dias | 0.755 | ✅ |
| S10 | 1 | baixo | 0.22 | 0.11 | 0.00 | 7.0 | RN35(R=0.95,s=0.64) | **RN35** Equilíbrio dimensional — var=0.008 (N=0.22 M=0.11 Met=0.00) | 0.635 | ✅ |
| S12 | 4 | alta | 0.60 | 0.60 | 0.70 | 7.8 | RN33(R=0.70,s=0.86) / RN35(R=0.99,s=0.65) / RN36(R=1.00,s=1.00) | **RN36** Retorno de fadiga — baixo → alta | 1.000 | ✅ |
| S13 | 4 | estavel | 0.64 | 0.64 | 0.82 | 7.6 | RN29(R=1.00,s=0.76) / RN32(R=0.07,s=0.34) / RN33(R=1.00,s=1.00) / RN35(R=0.95,s=0.64) | **RN33** Percentil cruzando threshold — Met cruzou 75 | 1.000 | ✅ |
| S14 | 4 | sobrecarga | 0.75 | 0.75 | 0.92 | 7.7 | RN29(R=0.79,s=0.66) / RN32(R=0.36,s=0.47) / RN33(R=1.00,s=1.00) / RN35(R=0.96,s=0.84) | **RN33** Percentil cruzando threshold — N cruzou 75 | M cruzou 75 | 1.000 | ✅ |

### Carlos Mendes (carlos_mendes)
modelo: **linear** · semanas analisadas: **12** · ritmo atual no Firestore: `alta`

| Sem | n | Ritmo calc. | pN | pM | pMet | PSE | Fatos disparados | Headline | Score | Tipo |
|---|---|---|---|---|---|---|---|---|---|---|
| S1 | 1 | estavel | 0.50 | 0.50 | 0.50 | 7.1 | — | ○ neutro · N lidera | — | ○ |
| S2 | 4 | estavel | 0.50 | 0.50 | 0.50 | 7.0 | RN35(R=1.00,s=0.86) | **RN35** Equilíbrio dimensional — var=0.000 (N=0.50 M=0.50 Met=0.50) | 0.860 | ✅ |
| S3 | 4 | estavel | 0.50 | 0.50 | 0.50 | 7.3 | RN32(R=0.14,s=0.37) / RN35(R=1.00,s=0.66) | **RN35** Equilíbrio dimensional — var=0.000 (N=0.50 M=0.50 Met=0.50) | 0.660 | ✅ |
| S4 | 3 | estavel | 0.50 | 0.50 | 0.50 | 7.2 | RN32(R=0.36,s=0.47) / RN35(R=1.00,s=0.66) | **RN35** Equilíbrio dimensional — var=0.000 (N=0.50 M=0.50 Met=0.50) | 0.660 | ✅ |
| S5 | 4 | estavel | 1.00 | 1.00 | 1.00 | 7.1 | RN32(R=0.64,s=0.59) / RN33(R=1.00,s=1.00) / RN35(R=1.00,s=0.66) | **RN33** Percentil cruzando threshold — N cruzou 75 | M cruzou 75 | Met cruzou 75 | 1.000 | ✅ |
| S6 | 4 | estavel | 1.00 | 1.00 | 1.00 | 7.0 | RN32(R=0.93,s=0.72) / RN35(R=1.00,s=0.66) | **RN32** Streak de aderência — 20 dias | 0.723 | ✅ |
| S7 | 4 | estavel | 1.00 | 1.00 | 1.00 | 7.2 | RN27(R=0.60,s=0.57) / RN32(R=1.00,s=0.56) / RN35(R=1.00,s=0.86) | **RN35** Equilíbrio dimensional — var=0.000 (N=1.00 M=1.00 Met=1.00) | 0.860 | ✅ |
| S8 | 3 | estavel | 0.29 | 0.29 | 0.29 | 7.4 | RN32(R=1.00,s=0.56) / RN35(R=1.00,s=0.66) | **RN35** Equilíbrio dimensional — var=0.000 (N=0.29 M=0.29 Met=0.29) | 0.660 | ✅ |
| S9 | 3 | alta | 1.00 | 1.00 | 1.00 | 7.1 | RN32(R=1.00,s=0.76) / RN33(R=1.00,s=1.00) / RN35(R=1.00,s=0.66) | **RN33** Percentil cruzando threshold — N cruzou 75 | M cruzou 75 | Met cruzou 75 | 1.000 | ✅ |
| S12 | 4 | alta | 1.00 | 1.00 | 1.00 | 7.8 | RN29(R=1.00,s=0.76) / RN35(R=1.00,s=0.66) | **RN29** Crescimento mecânico — 15719→23128→46582 (+196.3%) | 0.755 | ✅ |
| S13 | 4 | alta | 0.90 | 0.90 | 0.90 | 7.5 | RN27(R=0.43,s=0.50) / RN32(R=0.07,s=0.34) / RN35(R=1.00,s=0.86) | **RN35** Equilíbrio dimensional — var=0.000 (N=0.90 M=0.90 Met=0.90) | 0.860 | ✅ |
| S14 | 4 | alta | 0.82 | 0.82 | 0.91 | 7.6 | RN27(R=0.37,s=0.47) / RN32(R=0.36,s=0.47) / RN35(R=0.99,s=0.65) | **RN35** Equilíbrio dimensional — var=0.002 (N=0.82 M=0.82 Met=0.91) | 0.654 | ✅ |

### Fernanda Lima (fernanda_lima)
modelo: **linear** · semanas analisadas: **11** · ritmo atual no Firestore: `sobrecarga`

| Sem | n | Ritmo calc. | pN | pM | pMet | PSE | Fatos disparados | Headline | Score | Tipo |
|---|---|---|---|---|---|---|---|---|---|---|
| S1 | 1 | estavel | 0.50 | 0.50 | 0.50 | 8.3 | — | ○ neutro · N lidera | — | ○ |
| S2 | 3 | estavel | 0.50 | 0.50 | 0.50 | 8.5 | RN35(R=1.00,s=0.86) | **RN35** Equilíbrio dimensional — var=0.000 (N=0.50 M=0.50 Met=0.50) | 0.860 | ✅ |
| S3 | 3 | estavel | 0.50 | 0.50 | 0.50 | 7.6 | RN29(R=1.00,s=0.76) / RN32(R=0.00,s=0.30) / RN35(R=1.00,s=0.66) | **RN29** Crescimento mecânico — 2449→8186→8967 (+266.2%) | 0.755 | ✅ |
| S4 | 3 | estavel | 0.50 | 0.50 | 0.50 | 6.9 | RN29(R=1.00,s=0.56) / RN32(R=0.21,s=0.40) / RN35(R=1.00,s=0.66) | **RN35** Equilíbrio dimensional — var=0.000 (N=0.50 M=0.50 Met=0.50) | 0.660 | ✅ |
| S5 | 3 | estavel | 1.00 | 1.00 | 1.00 | 6.8 | RN32(R=0.43,s=0.50) / RN33(R=1.00,s=1.00) / RN35(R=1.00,s=0.66) | **RN33** Percentil cruzando threshold — N cruzou 75 | M cruzou 75 | Met cruzou 75 | 1.000 | ✅ |
| S6 | 3 | baixo | 0.20 | 0.40 | 0.40 | 7.3 | RN32(R=0.64,s=0.59) / RN35(R=0.94,s=0.63) | **RN35** Equilíbrio dimensional — var=0.009 (N=0.20 M=0.40 Met=0.40) | 0.633 | ✅ |
| S7 | 2 | sobrecarga | 0.17 | 0.67 | 0.67 | 7.7 | RN32(R=0.79,s=0.66) / RN33(R=0.70,s=0.86) / RN35(R=0.63,s=0.49) | **RN33** Percentil cruzando threshold — M cruzou 50 | Met cruzou 50 | 0.865 | ✅ |
| S10 | 1 | alta | 1.00 | 1.00 | 1.00 | 7.6 | RN33(R=1.00,s=1.00) / RN35(R=1.00,s=0.66) / RN36(R=1.00,s=1.00) | **RN33** Percentil cruzando threshold — N cruzou 75 | M cruzou 75 | Met cruzou 75 | 1.000 | ✅ |
| S12 | 3 | alta | 0.88 | 1.00 | 1.00 | 7.8 | RN35(R=0.98,s=0.85) | **RN35** Equilíbrio dimensional — var=0.003 (N=0.88 M=1.00 Met=1.00) | 0.850 | ✅ |
| S13 | 3 | alta | 0.78 | 0.78 | 0.78 | 7.4 | RN27(R=0.22,s=0.40) / RN35(R=1.00,s=0.66) | **RN35** Equilíbrio dimensional — var=0.000 (N=0.78 M=0.78 Met=0.78) | 0.660 | ✅ |
| S14 | 3 | estavel | 0.50 | 0.50 | 0.50 | 7.2 | RN32(R=0.14,s=0.37) / RN35(R=1.00,s=0.66) | **RN35** Equilíbrio dimensional — var=0.000 (N=0.50 M=0.50 Met=0.50) | 0.660 | ✅ |

### Iarima Nunes (iarima_nunes)
modelo: **block** · semanas analisadas: **14** · ritmo atual no Firestore: `baixo`

| Sem | n | Ritmo calc. | pN | pM | pMet | PSE | Fatos disparados | Headline | Score | Tipo |
|---|---|---|---|---|---|---|---|---|---|---|
| S1 | 1 | estavel | 0.50 | 0.50 | 0.50 | 7.0 | — | ○ neutro · N lidera | — | ○ |
| S2 | 3 | estavel | 0.50 | 0.50 | 0.50 | 6.9 | RN35(R=1.00,s=0.86) | **RN35** Equilíbrio dimensional — var=0.000 (N=0.50 M=0.50 Met=0.50) | 0.860 | ✅ |
| S3 | 3 | estavel | 0.50 | 0.50 | 0.50 | 7.0 | RN29(R=1.00,s=0.76) / RN32(R=0.00,s=0.30) / RN35(R=1.00,s=0.66) | **RN29** Crescimento mecânico — 4255→13155→14273 (+235.5%) | 0.755 | ✅ |
| S4 | 5 | estavel | 0.50 | 0.50 | 0.50 | 7.3 | RN29(R=1.00,s=0.56) / RN32(R=0.36,s=0.47) / RN35(R=1.00,s=0.66) | **RN35** Equilíbrio dimensional — var=0.000 (N=0.50 M=0.50 Met=0.50) | 0.660 | ✅ |
| S5 | 6 | estavel | 0.75 | 0.75 | 0.75 | 6.7 | RN32(R=0.79,s=0.66) / RN33(R=1.00,s=1.00) / RN35(R=1.00,s=0.66) | **RN33** Percentil cruzando threshold — N cruzou 75 | M cruzou 75 | Met cruzou 75 | 1.000 | ✅ |
| S6 | 4 | estavel | 1.00 | 0.80 | 0.80 | 7.3 | RN32(R=1.00,s=0.76) / RN35(R=0.94,s=0.63) | **RN32** Streak de aderência — 22 dias | 0.755 | ✅ |
| S7 | 1 | estavel | 0.50 | 0.83 | 1.00 | 7.9 | RN35(R=0.71,s=0.73) | **RN35** Equilíbrio dimensional — var=0.043 (N=0.50 M=0.83 Met=1.00) | 0.730 | ✅ |
| S8 | 5 | alta | 0.71 | 1.00 | 1.00 | 7.7 | RN35(R=0.88,s=0.61) | **RN35** Equilíbrio dimensional — var=0.018 (N=0.71 M=1.00 Met=1.00) | 0.606 | ✅ |
| S9 | 4 | alta | 1.00 | 1.00 | 1.00 | 7.8 | RN32(R=0.21,s=0.40) / RN33(R=1.00,s=1.00) / RN35(R=1.00,s=0.66) | **RN33** Percentil cruzando threshold — N cruzou 75 | 1.000 | ✅ |
| S10 | 2 | estavel | 0.44 | 0.44 | 0.56 | 7.8 | RN32(R=0.36,s=0.47) / RN35(R=0.98,s=0.65) | **RN35** Equilíbrio dimensional — var=0.003 (N=0.44 M=0.44 Met=0.56) | 0.652 | ✅ |
| S11 | 5 | estavel | 0.40 | 0.30 | 0.60 | 7.6 | RN35(R=0.90,s=0.61) | **RN35** Equilíbrio dimensional — var=0.016 (N=0.40 M=0.30 Met=0.60) | 0.613 | ✅ |
| S12 | 4 | estavel | 0.45 | 0.27 | 0.36 | 7.3 | RN32(R=0.14,s=0.37) / RN35(R=0.96,s=0.64) | **RN35** Equilíbrio dimensional — var=0.006 (N=0.45 M=0.27 Met=0.36) | 0.643 | ✅ |
| S13 | 4 | baixo | 0.25 | 0.42 | 0.67 | 7.4 | RN32(R=0.43,s=0.50) / RN33(R=0.70,s=0.86) / RN35(R=0.80,s=0.57) | **RN33** Percentil cruzando threshold — Met cruzou 50 | 0.865 | ✅ |
| S14 | 3 | baixo | 0.31 | 0.69 | 0.85 | 7.2 | RN32(R=0.64,s=0.59) / RN33(R=1.00,s=1.00) / RN35(R=0.66,s=0.51) | **RN33** Percentil cruzando threshold — M cruzou 50 | Met cruzou 75 | 1.000 | ✅ |

### Jacqueline (jacqueline)
modelo: **linear** · semanas analisadas: **13** · ritmo atual no Firestore: `estavel`

| Sem | n | Ritmo calc. | pN | pM | pMet | PSE | Fatos disparados | Headline | Score | Tipo |
|---|---|---|---|---|---|---|---|---|---|---|
| S1 | 1 | estavel | 0.50 | 0.50 | 0.50 | 7.9 | — | ○ neutro · N lidera | — | ○ |
| S2 | 3 | estavel | 0.50 | 0.50 | 0.50 | 7.7 | RN35(R=1.00,s=0.86) | **RN35** Equilíbrio dimensional — var=0.000 (N=0.50 M=0.50 Met=0.50) | 0.860 | ✅ |
| S3 | 3 | estavel | 0.50 | 0.50 | 0.50 | 7.3 | RN29(R=1.00,s=0.76) / RN32(R=0.00,s=0.30) / RN35(R=1.00,s=0.66) | **RN29** Crescimento mecânico — 4244→11479→12571 (+196.2%) | 0.755 | ✅ |
| S4 | 3 | estavel | 0.50 | 0.50 | 0.50 | 7.0 | RN29(R=1.00,s=0.56) / RN32(R=0.21,s=0.40) / RN35(R=1.00,s=0.66) | **RN35** Equilíbrio dimensional — var=0.000 (N=0.50 M=0.50 Met=0.50) | 0.660 | ✅ |
| S5 | 3 | estavel | 0.75 | 0.75 | 0.75 | 6.9 | RN32(R=0.43,s=0.50) / RN33(R=1.00,s=1.00) / RN35(R=1.00,s=0.66) | **RN33** Percentil cruzando threshold — N cruzou 75 | M cruzou 75 | Met cruzou 75 | 1.000 | ✅ |
| S6 | 3 | baixo | 0.20 | 0.20 | 0.20 | 7.0 | RN32(R=0.64,s=0.59) / RN35(R=1.00,s=0.66) | **RN35** Equilíbrio dimensional — var=0.000 (N=0.20 M=0.20 Met=0.20) | 0.660 | ✅ |
| S7 | 3 | estavel | 0.67 | 0.67 | 0.67 | 6.9 | RN32(R=0.86,s=0.69) / RN33(R=0.70,s=0.86) / RN35(R=1.00,s=0.66) / RN36(R=1.00,s=1.00) | **RN36** Retorno de fadiga — baixo → estavel | 1.000 | ✅ |
| S8 | 3 | alta | 1.00 | 1.00 | 1.00 | 6.7 | RN29(R=1.00,s=0.76) / RN32(R=1.00,s=0.76) / RN33(R=1.00,s=1.00) / RN35(R=1.00,s=0.66) | **RN33** Percentil cruzando threshold — N cruzou 75 | M cruzou 75 | Met cruzou 75 | 1.000 | ✅ |
| S9 | 2 | alta | 0.88 | 0.75 | 0.75 | 6.6 | RN27(R=0.39,s=0.48) / RN32(R=1.00,s=0.76) / RN35(R=0.98,s=0.85) | **RN35** Equilíbrio dimensional — var=0.003 (N=0.88 M=0.75 Met=0.75) | 0.850 | ✅ |
| S11 | 1 | alta | 1.00 | 1.00 | 1.00 | 7.3 | RN27(R=0.68,s=0.61) / RN35(R=1.00,s=0.66) | **RN35** Equilíbrio dimensional — var=0.000 (N=1.00 M=1.00 Met=1.00) | 0.660 | ✅ |
| S12 | 5 | alta | 1.00 | 0.90 | 0.90 | 7.6 | RN27(R=0.76,s=0.65) / RN35(R=0.99,s=0.65) | **RN35** Equilíbrio dimensional — var=0.002 (N=1.00 M=0.90 Met=0.90) | 0.653 | ✅ |
| S13 | 3 | alta | 0.82 | 0.82 | 0.82 | 6.7 | RN27(R=0.53,s=0.54) / RN32(R=0.14,s=0.37) / RN35(R=1.00,s=0.66) | **RN35** Equilíbrio dimensional — var=0.000 (N=0.82 M=0.82 Met=0.82) | 0.660 | ✅ |
| S14 | 1 | baixo | 0.33 | 0.00 | 0.00 | 7.5 | RN32(R=0.21,s=0.40) / RN35(R=0.84,s=0.59) | **RN35** Equilíbrio dimensional — var=0.025 (N=0.33 M=0.00 Met=0.00) | 0.586 | ✅ |

### Julia Duzzi (julia_duzzi)
modelo: **block** · semanas analisadas: **4** · ritmo atual no Firestore: `baixo`

| Sem | n | Ritmo calc. | pN | pM | pMet | PSE | Fatos disparados | Headline | Score | Tipo |
|---|---|---|---|---|---|---|---|---|---|---|
| S4 | 2 | estavel | 0.50 | 0.50 | 0.50 | 9.2 | — | ○ neutro · N lidera | — | ○ |
| S5 | 7 | estavel | 0.50 | 0.50 | 0.50 | 9.3 | RN35(R=1.00,s=0.86) | **RN35** Equilíbrio dimensional — var=0.000 (N=0.50 M=0.50 Met=0.50) | 0.860 | ✅ |
| S6 | 9 | estavel | 0.50 | 0.50 | 0.50 | 9.2 | RN29(R=1.00,s=0.76) / RN32(R=0.14,s=0.37) / RN35(R=1.00,s=0.66) | **RN29** Crescimento mecânico — 5567→32150→37180 (+567.9%) | 0.755 | ✅ |
| S7 | 3 | estavel | 0.50 | 0.50 | 0.50 | 9.2 | RN32(R=0.86,s=0.69) / RN35(R=1.00,s=0.66) | **RN32** Streak de aderência — 19 dias | 0.691 | ✅ |

### Lara Soares (lara_soares)
modelo: **linear** · semanas analisadas: **12** · ritmo atual no Firestore: `alta`

| Sem | n | Ritmo calc. | pN | pM | pMet | PSE | Fatos disparados | Headline | Score | Tipo |
|---|---|---|---|---|---|---|---|---|---|---|
| S1 | 1 | estavel | 0.50 | 0.50 | 0.50 | 6.9 | — | ○ neutro · N lidera | — | ○ |
| S2 | 3 | estavel | 0.50 | 0.50 | 0.50 | 6.8 | RN35(R=1.00,s=0.86) | **RN35** Equilíbrio dimensional — var=0.000 (N=0.50 M=0.50 Met=0.50) | 0.860 | ✅ |
| S3 | 3 | estavel | 0.50 | 0.50 | 0.50 | 6.9 | RN32(R=0.00,s=0.30) / RN35(R=1.00,s=0.66) | **RN35** Equilíbrio dimensional — var=0.000 (N=0.50 M=0.50 Met=0.50) | 0.660 | ✅ |
| S4 | 3 | estavel | 0.50 | 0.50 | 0.50 | 6.9 | RN32(R=0.21,s=0.40) / RN35(R=1.00,s=0.66) | **RN35** Equilíbrio dimensional — var=0.000 (N=0.50 M=0.50 Met=0.50) | 0.660 | ✅ |
| S5 | 2 | estavel | 1.00 | 1.00 | 1.00 | 6.8 | RN32(R=0.36,s=0.47) / RN33(R=1.00,s=1.00) / RN35(R=1.00,s=0.66) | **RN33** Percentil cruzando threshold — N cruzou 75 | M cruzou 75 | Met cruzou 75 | 1.000 | ✅ |
| S6 | 1 | sobrecarga | 0.20 | 0.20 | 0.20 | 8.2 | RN35(R=1.00,s=0.66) | **RN35** Equilíbrio dimensional — var=0.000 (N=0.20 M=0.20 Met=0.20) | 0.660 | ✅ |
| S7 | 3 | estavel | 0.83 | 0.83 | 0.83 | 7.8 | RN33(R=1.00,s=1.00) / RN35(R=1.00,s=0.66) / RN36(R=1.00,s=1.00) | **RN33** Percentil cruzando threshold — N cruzou 75 | M cruzou 75 | Met cruzou 75 | 1.000 | ✅ |
| S8 | 3 | alta | 1.00 | 0.86 | 0.86 | 7.2 | RN32(R=0.00,s=0.30) / RN35(R=0.97,s=0.65) | **RN35** Equilíbrio dimensional — var=0.005 (N=1.00 M=0.86 Met=0.86) | 0.646 | ✅ |
| S9 | 2 | alta | 1.00 | 1.00 | 1.00 | 7.2 | RN27(R=0.60,s=0.57) / RN32(R=0.14,s=0.37) / RN35(R=1.00,s=0.66) | **RN35** Equilíbrio dimensional — var=0.000 (N=1.00 M=1.00 Met=1.00) | 0.660 | ✅ |
| S12 | 4 | baixo | 0.11 | 0.22 | 0.56 | 5.8 | RN35(R=0.76,s=0.55) | **RN35** Equilíbrio dimensional — var=0.036 (N=0.11 M=0.22 Met=0.56) | 0.553 | ✅ |
| S13 | 4 | alta | 0.60 | 0.60 | 0.80 | 7.6 | RN29(R=1.00,s=0.76) / RN32(R=0.07,s=0.34) / RN33(R=1.00,s=1.00) / RN35(R=0.94,s=0.63) / RN36(R=1.00,s=1.00) | **RN33** Percentil cruzando threshold — N cruzou 50 | M cruzou 50 | Met cruzou 75 | 1.000 | ✅ |
| S14 | 2 | alta | 0.55 | 0.91 | 0.91 | 7.1 | RN32(R=0.21,s=0.40) / RN33(R=1.00,s=1.00) / RN35(R=0.80,s=0.57) | **RN33** Percentil cruzando threshold — M cruzou 75 | 1.000 | ✅ |

### Mariana Costa (mariana_costa)
modelo: **dup** · semanas analisadas: **17** · ritmo atual no Firestore: `estavel`

| Sem | n | Ritmo calc. | pN | pM | pMet | PSE | Fatos disparados | Headline | Score | Tipo |
|---|---|---|---|---|---|---|---|---|---|---|
| S1 | 1 | estavel | 0.50 | 0.50 | 0.50 | 6.9 | — | ○ neutro · N lidera | — | ○ |
| S2 | 4 | estavel | 0.50 | 0.50 | 0.50 | 6.7 | RN28(R=1.00,s=0.86) / RN35(R=1.00,s=0.86) | **RN28** Aderência ondulatória [PROXY] — 4 tipos distintos: Lower · Força, Lower · Volume, Upper · Força, Upper · Hipertrofia | 0.860 | ✅ |
| S3 | 4 | estavel | 0.50 | 0.50 | 0.50 | 6.8 | RN28(R=1.00,s=0.66) / RN29(R=1.00,s=0.76) / RN32(R=0.14,s=0.37) / RN35(R=1.00,s=0.86) | **RN35** Equilíbrio dimensional — var=0.000 (N=0.50 M=0.50 Met=0.50) | 0.860 | ✅ |
| S4 | 4 | estavel | 0.50 | 0.50 | 0.50 | 7.0 | RN28(R=1.00,s=0.66) / RN29(R=0.73,s=0.63) / RN32(R=0.43,s=0.50) / RN34(R=0.04,s=0.57) / RN35(R=1.00,s=0.66) | **RN28** Aderência ondulatória [PROXY] — 4 tipos distintos: Lower · Força, Lower · Volume, Upper · Força, Upper · Hipertrofia | 0.660 | ✅ |
| S5 | 4 | estavel | 1.00 | 1.00 | 1.00 | 6.8 | RN28(R=1.00,s=0.66) / RN32(R=0.71,s=0.63) / RN33(R=1.00,s=1.00) / RN35(R=1.00,s=0.66) | **RN33** Percentil cruzando threshold — N cruzou 75 | M cruzou 75 | Met cruzou 75 | 1.000 | ✅ |
| S6 | 4 | estavel | 1.00 | 1.00 | 1.00 | 6.9 | RN28(R=1.00,s=0.66) / RN32(R=1.00,s=0.76) / RN34(R=0.05,s=0.57) / RN35(R=1.00,s=0.86) | **RN35** Equilíbrio dimensional — var=0.000 (N=1.00 M=1.00 Met=1.00) | 0.860 | ✅ |
| S7 | 4 | estavel | 1.00 | 1.00 | 1.00 | 7.2 | RN27(R=0.60,s=0.57) / RN28(R=1.00,s=0.86) / RN32(R=1.00,s=0.76) / RN35(R=1.00,s=0.66) | **RN28** Aderência ondulatória [PROXY] — 4 tipos distintos: Lower · Força, Lower · Volume, Upper · Força, Upper · Hipertrofia | 0.860 | ✅ |
| S8 | 4 | alta | 1.00 | 1.00 | 1.00 | 7.3 | RN27(R=0.68,s=0.61) / RN28(R=1.00,s=0.66) / RN32(R=1.00,s=0.76) / RN35(R=1.00,s=0.66) | **RN32** Streak de aderência — 29 dias | 0.755 | ✅ |
| S9 | 4 | alta | 1.00 | 1.00 | 1.00 | 7.6 | RN27(R=0.76,s=0.65) / RN28(R=1.00,s=0.66) / RN32(R=1.00,s=0.56) / RN35(R=1.00,s=0.86) | **RN35** Equilíbrio dimensional — var=0.000 (N=1.00 M=1.00 Met=1.00) | 0.860 | ✅ |
| S10 | 4 | alta | 1.00 | 1.00 | 1.00 | 8.5 | RN27(R=0.84,s=0.68) / RN28(R=1.00,s=0.86) / RN32(R=1.00,s=0.56) / RN35(R=1.00,s=0.66) | **RN28** Aderência ondulatória [PROXY] — 4 tipos distintos: Lower · Força, Lower · Volume, Upper · Força, Upper · Hipertrofia | 0.860 | ✅ |
| S11 | 4 | alta | 0.80 | 0.90 | 0.90 | 9.0 | RN27(R=0.58,s=0.56) / RN28(R=1.00,s=0.66) / RN32(R=1.00,s=0.76) / RN35(R=0.99,s=0.65) | **RN32** Streak de aderência — 41 dias | 0.755 | ✅ |
| S12 | 4 | estavel | 0.45 | 0.55 | 0.55 | 8.9 | RN28(R=1.00,s=0.66) / RN32(R=1.00,s=0.56) / RN35(R=0.99,s=0.85) | **RN35** Equilíbrio dimensional — var=0.002 (N=0.45 M=0.55 Met=0.55) | 0.854 | ✅ |
| S13 | 3 | sobrecarga | 0.25 | 0.58 | 0.58 | 8.8 | RN28(R=1.00,s=0.86) / RN32(R=1.00,s=0.56) / RN34(R=0.04,s=0.57) / RN35(R=0.84,s=0.59) | **RN28** Aderência ondulatória [PROXY] — 4 tipos distintos: Lower · Força, Lower · Volume, Upper · Força, Upper · Hipertrofia | 0.860 | ✅ |
| S15 | 1 | estavel | 0.38 | 0.31 | 0.38 | 0.0 | RN28(R=1.00,s=0.66) / RN35(R=0.99,s=0.66) / RN36(R=1.00,s=1.00) | **RN36** Retorno de fadiga — sobrecarga → estavel | 1.000 | ✅ |
| S17 | 4 | estavel | 1.00 | 1.00 | 1.00 | 7.9 | RN28(R=1.00,s=0.66) / RN33(R=1.00,s=1.00) / RN34(R=0.69,s=0.86) / RN35(R=1.00,s=0.86) | **RN33** Percentil cruzando threshold — N cruzou 75 | M cruzou 75 | Met cruzou 75 | 1.000 | ✅ |
| S18 | 4 | estavel | 0.93 | 0.73 | 0.67 | 7.8 | RN28(R=1.00,s=0.86) / RN32(R=0.07,s=0.34) / RN34(R=0.21,s=0.64) / RN35(R=0.91,s=0.82) | **RN28** Aderência ondulatória [PROXY] — 7 tipos distintos: Força, Lower · Força, Lower · Volume, Metabólico | 0.860 | ✅ |
| S19 | 4 | estavel | 0.31 | 0.31 | 0.31 | 8.0 | RN28(R=1.00,s=0.66) / RN32(R=0.36,s=0.47) / RN35(R=1.00,s=0.86) | **RN35** Equilíbrio dimensional — var=0.000 (N=0.31 M=0.31 Met=0.31) | 0.860 | ✅ |

### Paula Freitas (paula_freitas)
modelo: **linear** · semanas analisadas: **13** · ritmo atual no Firestore: `estavel`

| Sem | n | Ritmo calc. | pN | pM | pMet | PSE | Fatos disparados | Headline | Score | Tipo |
|---|---|---|---|---|---|---|---|---|---|---|
| S1 | 1 | estavel | 0.50 | 0.50 | 0.50 | 6.6 | — | ○ neutro · N lidera | — | ○ |
| S2 | 4 | estavel | 0.50 | 0.50 | 0.50 | 7.1 | RN35(R=1.00,s=0.86) | **RN35** Equilíbrio dimensional — var=0.000 (N=0.50 M=0.50 Met=0.50) | 0.860 | ✅ |
| S3 | 4 | estavel | 0.50 | 0.50 | 0.50 | 7.8 | RN32(R=0.14,s=0.37) / RN35(R=1.00,s=0.66) | **RN35** Equilíbrio dimensional — var=0.000 (N=0.50 M=0.50 Met=0.50) | 0.660 | ✅ |
| S4 | 4 | estavel | 0.50 | 0.50 | 0.50 | 7.2 | RN32(R=0.43,s=0.50) / RN35(R=1.00,s=0.66) | **RN35** Equilíbrio dimensional — var=0.000 (N=0.50 M=0.50 Met=0.50) | 0.660 | ✅ |
| S5 | 4 | estavel | 0.50 | 0.50 | 0.50 | 7.8 | RN32(R=0.71,s=0.63) / RN35(R=1.00,s=0.66) | **RN35** Equilíbrio dimensional — var=0.000 (N=0.50 M=0.50 Met=0.50) | 0.660 | ✅ |
| S6 | 4 | estavel | 1.00 | 1.00 | 1.00 | 7.0 | RN32(R=1.00,s=0.76) / RN33(R=1.00,s=1.00) / RN35(R=1.00,s=0.66) | **RN33** Percentil cruzando threshold — N cruzou 75 | M cruzou 75 | Met cruzou 75 | 1.000 | ✅ |
| S7 | 4 | estavel | 0.50 | 0.50 | 0.50 | 7.8 | RN32(R=1.00,s=0.76) / RN35(R=1.00,s=0.66) | **RN32** Streak de aderência — 25 dias | 0.755 | ✅ |
| S8 | 4 | alta | 1.00 | 1.00 | 1.00 | 7.0 | RN32(R=1.00,s=0.56) / RN33(R=1.00,s=1.00) / RN35(R=1.00,s=0.86) | **RN33** Percentil cruzando threshold — N cruzou 75 | M cruzou 75 | Met cruzou 75 | 1.000 | ✅ |
| S9 | 3 | alta | 0.88 | 0.75 | 0.62 | 8.1 | RN32(R=1.00,s=0.56) / RN35(R=0.93,s=0.83) | **RN35** Equilíbrio dimensional — var=0.010 (N=0.88 M=0.75 Met=0.62) | 0.829 | ✅ |
| S10 | 1 | sobrecarga | 0.00 | 0.00 | 0.00 | 7.5 | RN35(R=1.00,s=0.66) | **RN35** Equilíbrio dimensional — var=0.000 (N=0.00 M=0.00 Met=0.00) | 0.660 | ✅ |
| S12 | 4 | sobrecarga | 0.20 | 0.20 | 0.60 | 7.8 | RN33(R=0.70,s=0.86) / RN35(R=0.76,s=0.55) | **RN33** Percentil cruzando threshold — Met cruzou 50 | 0.865 | ✅ |
| S13 | 3 | sobrecarga | 0.27 | 0.27 | 0.36 | 7.7 | RN32(R=0.00,s=0.30) / RN35(R=0.99,s=0.65) | **RN35** Equilíbrio dimensional — var=0.002 (N=0.27 M=0.27 Met=0.36) | 0.654 | ✅ |
| S14 | 3 | baixo | 0.25 | 0.33 | 0.25 | 7.2 | RN32(R=0.21,s=0.40) / RN35(R=0.99,s=0.66) | **RN35** Equilíbrio dimensional — var=0.002 (N=0.25 M=0.33 Met=0.25) | 0.655 | ✅ |

### Roberto Silva (roberto_silva)
modelo: **linear** · semanas analisadas: **12** · ritmo atual no Firestore: `estavel`

| Sem | n | Ritmo calc. | pN | pM | pMet | PSE | Fatos disparados | Headline | Score | Tipo |
|---|---|---|---|---|---|---|---|---|---|---|
| S1 | 1 | estavel | 0.50 | 0.50 | 0.50 | 5.5 | — | ○ neutro · N lidera | — | ○ |
| S2 | 3 | estavel | 0.50 | 0.50 | 0.50 | 5.7 | RN35(R=1.00,s=0.86) | **RN35** Equilíbrio dimensional — var=0.000 (N=0.50 M=0.50 Met=0.50) | 0.860 | ✅ |
| S3 | 3 | estavel | 0.50 | 0.50 | 0.50 | 5.6 | RN32(R=0.00,s=0.30) / RN35(R=1.00,s=0.66) | **RN35** Equilíbrio dimensional — var=0.000 (N=0.50 M=0.50 Met=0.50) | 0.660 | ✅ |
| S4 | 3 | estavel | 0.50 | 0.50 | 0.50 | 5.7 | RN32(R=0.21,s=0.40) / RN35(R=1.00,s=0.66) | **RN35** Equilíbrio dimensional — var=0.000 (N=0.50 M=0.50 Met=0.50) | 0.660 | ✅ |
| S5 | 3 | estavel | 1.00 | 1.00 | 0.75 | 6.0 | RN32(R=0.43,s=0.50) / RN33(R=1.00,s=1.00) / RN35(R=0.91,s=0.62) | **RN33** Percentil cruzando threshold — N cruzou 75 | M cruzou 75 | Met cruzou 75 | 1.000 | ✅ |
| S6 | 3 | estavel | 1.00 | 1.00 | 1.00 | 5.8 | RN32(R=0.64,s=0.59) / RN35(R=1.00,s=0.66) | **RN35** Equilíbrio dimensional — var=0.000 (N=1.00 M=1.00 Met=1.00) | 0.660 | ✅ |
| S7 | 3 | estavel | 1.00 | 1.00 | 1.00 | 6.1 | RN27(R=0.60,s=0.57) / RN32(R=0.86,s=0.69) / RN35(R=1.00,s=0.66) | **RN32** Streak de aderência — 19 dias | 0.691 | ✅ |
| S8 | 3 | alta | 1.00 | 1.00 | 1.00 | 6.1 | RN27(R=0.68,s=0.61) / RN32(R=1.00,s=0.56) / RN35(R=1.00,s=0.66) | **RN35** Equilíbrio dimensional — var=0.000 (N=1.00 M=1.00 Met=1.00) | 0.660 | ✅ |
| S9 | 2 | alta | 1.00 | 0.88 | 0.75 | 6.3 | RN27(R=0.76,s=0.65) / RN32(R=1.00,s=0.56) / RN35(R=0.93,s=0.63) | **RN27** Acúmulo neural sustentado — pN=1.00 · 5 semanas | 0.647 | ✅ |
| S12 | 4 | alta | 1.00 | 1.00 | 1.00 | 7.8 | RN27(R=0.84,s=0.48) / RN35(R=1.00,s=0.66) | **RN35** Equilíbrio dimensional — var=0.000 (N=1.00 M=1.00 Met=1.00) | 0.660 | ✅ |
| S13 | 4 | alta | 0.90 | 0.90 | 0.90 | 6.6 | RN27(R=0.75,s=0.44) / RN32(R=0.07,s=0.34) / RN35(R=1.00,s=0.66) | **RN35** Equilíbrio dimensional — var=0.000 (N=0.90 M=0.90 Met=0.90) | 0.660 | ✅ |
| S14 | 2 | alta | 0.64 | 0.82 | 0.82 | 6.1 | RN32(R=0.21,s=0.40) / RN35(R=0.95,s=0.64) | **RN35** Equilíbrio dimensional — var=0.007 (N=0.64 M=0.82 Met=0.82) | 0.638 | ✅ |

---

## Parte 2 — Leitura narrativa (como o aluno leria)

**Ana Beatriz** (modelo: linear):

  S 1 ○  [neutro] N lidera o percentil
  S 2 ✅  "Dimensões equilibradas — var=0.000 (N=0.50 M=0.50 Met=0.50)"
  S 3 ✅  "Dimensões equilibradas — var=0.000 (N=0.50 M=0.50 Met=0.50)"
  S 4 ✅  "Dimensões equilibradas — var=0.000 (N=0.50 M=0.50 Met=0.50)"
  S 5 ✅  "Dimensões equilibradas — var=0.000 (N=0.25 M=0.25 Met=0.25)"
  S 6 ✅  "Marco atingido: N cruzou 75 | M cruzou 75 | Met cruzou 75"
  S 7 ✅  "Volume crescendo há 3 semanas — 29466→44418→47094 (+59.8%)"
  S 8 ✅  "Dimensões equilibradas — var=0.000 (N=1.00 M=1.00 Met=1.00)"
  S 9 ✅  "Sequência de 32 dias de treino"
  S10 ✅  "Dimensões equilibradas — var=0.008 (N=0.22 M=0.11 Met=0.00)"
  S12 ✅  "Virada: baixo → alta"
  S13 ✅  "Marco atingido: Met cruzou 75"
  S14 ✅  "Marco atingido: N cruzou 75 | M cruzou 75"

**Carlos Mendes** (modelo: linear):

  S 1 ○  [neutro] N lidera o percentil
  S 2 ✅  "Dimensões equilibradas — var=0.000 (N=0.50 M=0.50 Met=0.50)"
  S 3 ✅  "Dimensões equilibradas — var=0.000 (N=0.50 M=0.50 Met=0.50)"
  S 4 ✅  "Dimensões equilibradas — var=0.000 (N=0.50 M=0.50 Met=0.50)"
  S 5 ✅  "Marco atingido: N cruzou 75 | M cruzou 75 | Met cruzou 75"
  S 6 ✅  "Sequência de 20 dias de treino"
  S 7 ✅  "Dimensões equilibradas — var=0.000 (N=1.00 M=1.00 Met=1.00)"
  S 8 ✅  "Dimensões equilibradas — var=0.000 (N=0.29 M=0.29 Met=0.29)"
  S 9 ✅  "Marco atingido: N cruzou 75 | M cruzou 75 | Met cruzou 75"
  S12 ✅  "Volume crescendo há 3 semanas — 15719→23128→46582 (+196.3%)"
  S13 ✅  "Dimensões equilibradas — var=0.000 (N=0.90 M=0.90 Met=0.90)"
  S14 ✅  "Dimensões equilibradas — var=0.002 (N=0.82 M=0.82 Met=0.91)"

**Fernanda Lima** (modelo: linear):

  S 1 ○  [neutro] N lidera o percentil
  S 2 ✅  "Dimensões equilibradas — var=0.000 (N=0.50 M=0.50 Met=0.50)"
  S 3 ✅  "Volume crescendo há 3 semanas — 2449→8186→8967 (+266.2%)"
  S 4 ✅  "Dimensões equilibradas — var=0.000 (N=0.50 M=0.50 Met=0.50)"
  S 5 ✅  "Marco atingido: N cruzou 75 | M cruzou 75 | Met cruzou 75"
  S 6 ✅  "Dimensões equilibradas — var=0.009 (N=0.20 M=0.40 Met=0.40)"
  S 7 ✅  "Marco atingido: M cruzou 50 | Met cruzou 50"
  S10 ✅  "Marco atingido: N cruzou 75 | M cruzou 75 | Met cruzou 75"
  S12 ✅  "Dimensões equilibradas — var=0.003 (N=0.88 M=1.00 Met=1.00)"
  S13 ✅  "Dimensões equilibradas — var=0.000 (N=0.78 M=0.78 Met=0.78)"
  S14 ✅  "Dimensões equilibradas — var=0.000 (N=0.50 M=0.50 Met=0.50)"

**Iarima Nunes** (modelo: block):

  S 1 ○  [neutro] N lidera o percentil
  S 2 ✅  "Dimensões equilibradas — var=0.000 (N=0.50 M=0.50 Met=0.50)"
  S 3 ✅  "Volume crescendo há 3 semanas — 4255→13155→14273 (+235.5%)"
  S 4 ✅  "Dimensões equilibradas — var=0.000 (N=0.50 M=0.50 Met=0.50)"
  S 5 ✅  "Marco atingido: N cruzou 75 | M cruzou 75 | Met cruzou 75"
  S 6 ✅  "Sequência de 22 dias de treino"
  S 7 ✅  "Dimensões equilibradas — var=0.043 (N=0.50 M=0.83 Met=1.00)"
  S 8 ✅  "Dimensões equilibradas — var=0.018 (N=0.71 M=1.00 Met=1.00)"
  S 9 ✅  "Marco atingido: N cruzou 75"
  S10 ✅  "Dimensões equilibradas — var=0.003 (N=0.44 M=0.44 Met=0.56)"
  S11 ✅  "Dimensões equilibradas — var=0.016 (N=0.40 M=0.30 Met=0.60)"
  S12 ✅  "Dimensões equilibradas — var=0.006 (N=0.45 M=0.27 Met=0.36)"
  S13 ✅  "Marco atingido: Met cruzou 50"
  S14 ✅  "Marco atingido: M cruzou 50 | Met cruzou 75"

**Jacqueline** (modelo: linear):

  S 1 ○  [neutro] N lidera o percentil
  S 2 ✅  "Dimensões equilibradas — var=0.000 (N=0.50 M=0.50 Met=0.50)"
  S 3 ✅  "Volume crescendo há 3 semanas — 4244→11479→12571 (+196.2%)"
  S 4 ✅  "Dimensões equilibradas — var=0.000 (N=0.50 M=0.50 Met=0.50)"
  S 5 ✅  "Marco atingido: N cruzou 75 | M cruzou 75 | Met cruzou 75"
  S 6 ✅  "Dimensões equilibradas — var=0.000 (N=0.20 M=0.20 Met=0.20)"
  S 7 ✅  "Virada: baixo → estavel"
  S 8 ✅  "Marco atingido: N cruzou 75 | M cruzou 75 | Met cruzou 75"
  S 9 ✅  "Dimensões equilibradas — var=0.003 (N=0.88 M=0.75 Met=0.75)"
  S11 ✅  "Dimensões equilibradas — var=0.000 (N=1.00 M=1.00 Met=1.00)"
  S12 ✅  "Dimensões equilibradas — var=0.002 (N=1.00 M=0.90 Met=0.90)"
  S13 ✅  "Dimensões equilibradas — var=0.000 (N=0.82 M=0.82 Met=0.82)"
  S14 ✅  "Dimensões equilibradas — var=0.025 (N=0.33 M=0.00 Met=0.00)"

**Julia Duzzi** (modelo: block):

  S 4 ○  [neutro] N lidera o percentil
  S 5 ✅  "Dimensões equilibradas — var=0.000 (N=0.50 M=0.50 Met=0.50)"
  S 6 ✅  "Volume crescendo há 3 semanas — 5567→32150→37180 (+567.9%)"
  S 7 ✅  "Sequência de 19 dias de treino"

**Lara Soares** (modelo: linear):

  S 1 ○  [neutro] N lidera o percentil
  S 2 ✅  "Dimensões equilibradas — var=0.000 (N=0.50 M=0.50 Met=0.50)"
  S 3 ✅  "Dimensões equilibradas — var=0.000 (N=0.50 M=0.50 Met=0.50)"
  S 4 ✅  "Dimensões equilibradas — var=0.000 (N=0.50 M=0.50 Met=0.50)"
  S 5 ✅  "Marco atingido: N cruzou 75 | M cruzou 75 | Met cruzou 75"
  S 6 ✅  "Dimensões equilibradas — var=0.000 (N=0.20 M=0.20 Met=0.20)"
  S 7 ✅  "Marco atingido: N cruzou 75 | M cruzou 75 | Met cruzou 75"
  S 8 ✅  "Dimensões equilibradas — var=0.005 (N=1.00 M=0.86 Met=0.86)"
  S 9 ✅  "Dimensões equilibradas — var=0.000 (N=1.00 M=1.00 Met=1.00)"
  S12 ✅  "Dimensões equilibradas — var=0.036 (N=0.11 M=0.22 Met=0.56)"
  S13 ✅  "Marco atingido: N cruzou 50 | M cruzou 50 | Met cruzou 75"
  S14 ✅  "Marco atingido: M cruzou 75"

**Mariana Costa** (modelo: dup):

  S 1 ○  [neutro] N lidera o percentil
  S 2 ✅  "Você está seguindo o plano DUP — 4 tipos distintos: Lower · Força, Lower · Volume, Upper · Força, Upper · Hipertrofia"
  S 3 ✅  "Dimensões equilibradas — var=0.000 (N=0.50 M=0.50 Met=0.50)"
  S 4 ✅  "Você está seguindo o plano DUP — 4 tipos distintos: Lower · Força, Lower · Volume, Upper · Força, Upper · Hipertrofia"
  S 5 ✅  "Marco atingido: N cruzou 75 | M cruzou 75 | Met cruzou 75"
  S 6 ✅  "Dimensões equilibradas — var=0.000 (N=1.00 M=1.00 Met=1.00)"
  S 7 ✅  "Você está seguindo o plano DUP — 4 tipos distintos: Lower · Força, Lower · Volume, Upper · Força, Upper · Hipertrofia"
  S 8 ✅  "Sequência de 29 dias de treino"
  S 9 ✅  "Dimensões equilibradas — var=0.000 (N=1.00 M=1.00 Met=1.00)"
  S10 ✅  "Você está seguindo o plano DUP — 4 tipos distintos: Lower · Força, Lower · Volume, Upper · Força, Upper · Hipertrofia"
  S11 ✅  "Sequência de 41 dias de treino"
  S12 ✅  "Dimensões equilibradas — var=0.002 (N=0.45 M=0.55 Met=0.55)"
  S13 ✅  "Você está seguindo o plano DUP — 4 tipos distintos: Lower · Força, Lower · Volume, Upper · Força, Upper · Hipertrofia"
  S15 ✅  "Virada: sobrecarga → estavel"
  S17 ✅  "Marco atingido: N cruzou 75 | M cruzou 75 | Met cruzou 75"
  S18 ✅  "Você está seguindo o plano DUP — 7 tipos distintos: Força, Lower · Força, Lower · Volume, Metabólico"
  S19 ✅  "Dimensões equilibradas — var=0.000 (N=0.31 M=0.31 Met=0.31)"

**Paula Freitas** (modelo: linear):

  S 1 ○  [neutro] N lidera o percentil
  S 2 ✅  "Dimensões equilibradas — var=0.000 (N=0.50 M=0.50 Met=0.50)"
  S 3 ✅  "Dimensões equilibradas — var=0.000 (N=0.50 M=0.50 Met=0.50)"
  S 4 ✅  "Dimensões equilibradas — var=0.000 (N=0.50 M=0.50 Met=0.50)"
  S 5 ✅  "Dimensões equilibradas — var=0.000 (N=0.50 M=0.50 Met=0.50)"
  S 6 ✅  "Marco atingido: N cruzou 75 | M cruzou 75 | Met cruzou 75"
  S 7 ✅  "Sequência de 25 dias de treino"
  S 8 ✅  "Marco atingido: N cruzou 75 | M cruzou 75 | Met cruzou 75"
  S 9 ✅  "Dimensões equilibradas — var=0.010 (N=0.88 M=0.75 Met=0.62)"
  S10 ✅  "Dimensões equilibradas — var=0.000 (N=0.00 M=0.00 Met=0.00)"
  S12 ✅  "Marco atingido: Met cruzou 50"
  S13 ✅  "Dimensões equilibradas — var=0.002 (N=0.27 M=0.27 Met=0.36)"
  S14 ✅  "Dimensões equilibradas — var=0.002 (N=0.25 M=0.33 Met=0.25)"

**Roberto Silva** (modelo: linear):

  S 1 ○  [neutro] N lidera o percentil
  S 2 ✅  "Dimensões equilibradas — var=0.000 (N=0.50 M=0.50 Met=0.50)"
  S 3 ✅  "Dimensões equilibradas — var=0.000 (N=0.50 M=0.50 Met=0.50)"
  S 4 ✅  "Dimensões equilibradas — var=0.000 (N=0.50 M=0.50 Met=0.50)"
  S 5 ✅  "Marco atingido: N cruzou 75 | M cruzou 75 | Met cruzou 75"
  S 6 ✅  "Dimensões equilibradas — var=0.000 (N=1.00 M=1.00 Met=1.00)"
  S 7 ✅  "Sequência de 19 dias de treino"
  S 8 ✅  "Dimensões equilibradas — var=0.000 (N=1.00 M=1.00 Met=1.00)"
  S 9 ✅  "Neural consistente há 5 semanas"
  S12 ✅  "Dimensões equilibradas — var=0.000 (N=1.00 M=1.00 Met=1.00)"
  S13 ✅  "Dimensões equilibradas — var=0.000 (N=0.90 M=0.90 Met=0.90)"
  S14 ✅  "Dimensões equilibradas — var=0.007 (N=0.64 M=0.82 Met=0.82)"

---

## Parte 3 — Agregado

**Total semanas-aluno:** 121

| Resultado | Contagem | % |
|---|---|---|
| ✅ Fato positivo | 111 | 92% |
| ⚠ Alerta | 0 | 0% |
| ○ Neutro | 10 | 8% |

### Frequência de fatos

| RN | Nome | Disparou | Foi headline | Taxa win |
|---|---|---|---|---|
| 27 | Acúmulo neural sustentado | 21 | 1 | 5% |
| 28 | Aderência ondulatória [PROXY] | 16 | 6 | 38% |
| 29 | Crescimento mecânico | 16 | 6 | 38% |
| 32 | Streak de aderência | 82 | 8 | 10% |
| 33 | Percentil cruzando threshold | 26 | 24 | 92% |
| 34 | Resiliência à carga | 5 | 0 | 0% |
| 35 | Equilíbrio dimensional | 111 | 63 | 57% |
| 36 | Retorno de fadiga | 7 | 3 | 43% |

**Fatos ÓRFÃOS:** nenhum — todos dispararam em pelo menos 1 semana-aluno

### Distribuição de scores das headlines vencedoras

| Stat | Valor |
|---|---|
| Mínimo | 0.553 |
| Média  | 0.791 |
| Máximo | 1.000 |
| Mediana | 0.755 |

### Headlines por modelo de periodização

| RN | Nome | linear | block | dup |
|---|---|---|---|---|
| 27 | Acúmulo neural sustentado | 1 | 0 | 0 |
| 28 | Aderência ondulatória [PROXY] | 0 | 0 | 6 |
| 29 | Crescimento mecânico | 4 | 2 | 0 |
| 32 | Streak de aderência | 4 | 2 | 2 |
| 33 | Percentil cruzando threshold | 18 | 4 | 2 |
| 34 | Resiliência à carga | 0 | 0 | 0 |
| 35 | Equilíbrio dimensional | 50 | 8 | 5 |
| 36 | Retorno de fadiga | 2 | 0 | 1 |

---

## Parte 4 — Diagnóstico e calibração

### ⚠ Dominância excessiva detectada

**RN 35 (Equilíbrio dimensional)** foi headline em **63 semanas (57%** dos fatos positivos).
Possíveis causas: critério fácil de satisfazer + A baixo compensado por R alto, ou fatos concorrentes com A baixo sendo suprimidos pela anti-repetição.
Recomendação: aumentar exigência de semanas consecutivas **ou** elevar A de fatos com dado igualmente rico (RN 35, RN 28).

### Alunos com predominância de neutro/alerta

| Aluno | Semanas | ✅ Fato | ⚠ Alerta | ○ Neutro | % sem fato |
|---|---|---|---|---|---|
| Ana Beatriz | 13 | 12 | 0 | 1 | 8% |
| Carlos Mendes | 12 | 11 | 0 | 1 | 8% |
| Fernanda Lima | 11 | 10 | 0 | 1 | 9% |
| Iarima Nunes | 14 | 13 | 0 | 1 | 7% |
| Jacqueline | 13 | 12 | 0 | 1 | 8% |
| Julia Duzzi | 4 | 3 | 0 | 1 | 25% |
| Lara Soares | 12 | 11 | 0 | 1 | 8% |
| Mariana Costa | 17 | 16 | 0 | 1 | 6% |
| Paula Freitas | 13 | 12 | 0 | 1 | 8% |
| Roberto Silva | 12 | 11 | 0 | 1 | 8% |

### Recomendações de calibração (sugestões — não implementar)

- **Scores médios altos (0.79)**: fatos raros (A=1.0) dominam. Verificar se RN 33/34/36 estão calibrados corretamente ou se disparando com facilidade excessiva.
- **RN 28 [PROXY]**: venceu com dado de proxy (variação de tipo, não conformidade real). Implementar prescrição-calendário para elevar confiabilidade antes de usar em produção.
- **ritmo_estado recalculado** é uma aproximação heurística. Comparar com `students.ritmo_estado` atual dos 10 alunos como sanity check antes de usar RN 36 em produção.
- **Semana 1–3**: percentis sempre 0.50 (dados históricos insuficientes para `dim_percentile`). Considerar suprimir fatos que dependem de percentil nas 3 primeiras semanas do mesociclo.

---

*Script de leitura apenas. Nenhum dado foi escrito no Firestore ou em arquivos de produção.*