# Momentum · Modelo Matemático
**v0.1 · Mar 2026**

Sistema de quantificação de carga fisiológica por sessão. Define como o Momentum transforma dados de execução em índices comparáveis, separando carga objetiva de carga interna percebida.

---

## 0 · Os 5 Coeficientes

Fixos no banco de exercícios — propriedades do movimento, não do aluno. **Alterações são exclusivas do time Momentum.**

| Coef. | Escala | Nome | Papel no modelo |
|-------|--------|------|-----------------|
| CT | 0–10 | Complexidade Técnica | Amplificador do custo neural em movimentos complexos. Ex: Hack Machine CT=2.0 · Snatch CT=9.5 |
| IM | 0–10 | Impacto Mecânico | Estresse mecânico direto sobre tecidos. Base do componente Mecânica. Ex: Leg Press IM=6.0 · Agachamento Livre IM=9.0 |
| DN | 0–10 | Demanda Neural | Demanda neural base do exercício. Base do componente Neural, amplificado por CT e SV. |
| SV | 0–10 | Sensibilidade à Velocidade | Amplifica custo neural e metabólico quando intenção explosiva é prescrita pelo PT. |
| FC | 0.3–1.5 | Fator de Carga Neural | Grau de liberdade do movimento — custo de estabilização e coordenação. **Entra apenas no componente Neural, não em CargaNorm.** Ex: Agachamento Livre FC=1.2 · Leg Press FC=0.45 · Extensora FC=0.2 |

**FC e DN: distintos mas relacionados (r=0.88).** FC captura grau de liberdade (livre vs guiado). DN captura complexidade de coordenação (programação motora). Agachamento e Clean têm DN próximos, mas FC do Agachamento é maior porque permite carga absoluta maior sobre o SNC.

---

## 1 · Carga Normalizada (CargaNorm)

Base de todos os componentes. FC **não entra aqui** — fisiologicamente incorreto.

```
CargaNorm_i = kg_i × reps_i × séries_i
```

> **⚠ Consequência da saída de FC do CargaNorm:** IM dos exercícios isolados (Extensora, Flexora, Rosca, etc.) precisa ser recalibrado. Com FC fora de CargaNorm, a Mecânica desses exercícios aumenta — IM deve refletir honestamente a tensão mecânica local.

---

## 2 · Componentes Fisiológicos

### 2a · Componente Neural

```
Neural_i = CargaNorm_i × FC_i × DN_i × (1 + CT_i×0.05 + SV_i×explos_i×0.05)
```

- `explos_i`: intenção explosiva prescrita pelo PT (0=controlado · 1=explosivo)
- `0.05` = fatorAmplificação — conservador, calibrável com dados reais
- CT e SV **somam** (não multiplicam) para manter os amplificadores independentes e calibráveis

### 2b · Componente Mecânica

```
Mecânica_i = CargaNorm_i × IM_i
```

Componente mais direto. FC não entra — tensão muscular não depende de grau de liberdade do movimento.

> **⚠ IM precisa ser recalibrado nos isolados** após a mudança de FC. Ver pendências no §∑.

### 2c · Componente Metabólica

```
TempoRep_i   = exc_i + pausaInf_i + conc_i + pausaSup_i     (cadência prescrita pelo PT)
TUT_i        = TempoRep_i × reps_i × séries_i
TUT_base_i   = 3 × reps_i × séries_i                        (referência: 3s/rep)
FTT_i        = TUT_i / TUT_base_i                           (fator de tempo sob tensão)
FD_i         = 90 / descanso_s_i                            (fator de densidade; referência 90s)

Metabólica_i = CargaNorm_i × FTT_i × SV_i × FD_i
```

- FTT > 1 → execução mais lenta que o padrão (maior custo oxidativo)
- FTT < 1 → execução mais rápida (maior componente de potência — capturado pelo SV no Neural)
- FD > 1 → descanso menor que 90s → maior custo metabólico
- **FTT = 1 quando cadência não prescrita** (comportamento padrão — confirmar antes de implementar)

---

## 3 · Soma da Sessão

```
Neural_sessao     = Σ Neural_i
Mecânica_sessao   = Σ Mecânica_i
Metabólica_sessao = Σ Metabólica_i
```

Expõe o caráter dominante do treino. Base do radar do aluno e alertas de Ritmo.

---

## 4 · Carga Objetiva da Sessão

Pesos definidos pelo PT na criação do mesociclo. **wN + wM + wMet não precisam somar 1 — são amplificadores relativos.**

```
CargaObjetiva = (wN × Neural_sessao) + (wM × Mecânica_sessao) + (wMet × Metabólica_sessao)
```

Dois campos obrigatórios por sessão:
- `ic_planejado` = CargaObjetiva calculada sobre a prescrição
- `ic_executado` = CargaObjetiva calculada sobre o executado

**Pesos por valência (exemplos):**

| Valência | wN | wM | wMet |
|----------|----|----|------|
| Força Máxima | 0.50 | 0.35 | 0.15 |
| Força Hipertrófica | 0.30 | 0.40 | 0.30 |
| Resistência de Força | 0.20 | 0.25 | 0.55 |
| Potência/Pliometria | 0.50 | 0.30 | 0.20 |

---

## 5 · Carga Interna e Índice de Adaptação

### 5a · Carga Interna (modelo Foster)

```
CargaInterna = PSE_relatada × duração_min
```

Separado da CargaObjetiva para preservar a carga real executada no histórico — PSE como multiplicador distorceria o registro objetivo.

> **⚠ `duração_min` não existe no schema atual de momentum-sessions — precisa ser adicionado.**

### 5b · PSE por série, calculada e relatada

```
PSE_exercício = média(PSE das séries do exercício)
PSE_calc      = Σ(CargaNorm_i × PSE_exercício_i) / Σ(CargaNorm_i)   [ponderada por volume]
PSE_relatada  = prompt ao finalizar a sessão ("Como foi a sessão como um todo?")
PSE_ritmo     = (PSE_calc × α) + (PSE_relatada × (1 − α))
```

**α por nível (configurável pelo PT):**
- Iniciante: α=0.85 (confia no calculado — autorrelato não calibrado)
- Intermediário: α=0.65 (equilíbrio)
- Avançado: α=0.40 (confia no relatado — alta interoceptividade)
- Personalizado: α livre

**ΔPSE — série temporal própria:**
```
ΔPSE = PSE_relatada − PSE_calc
```
- Δ+ = fadiga acumulada / estresse externo / sobrecarga não capturada pelo IC
- Δ− = adaptação acima do prescrito / possível subdesafio
- Δ consistentemente zero = aluno bem calibrado

### 5c · Índice de Adaptação (RatioAdaptação)

```
RatioAdaptação = CargaObjetiva / CargaInterna
```

- Ratio crescente → aluno absorvendo o estímulo com facilidade crescente → sinal de progressão
- Ratio decrescente → fadiga ou estresse externo → cautela

> **Nota importante:** RatioAdaptação é estruturalmente alto por diferença de escala entre CargaObjetiva e CargaInterna. Deve ser exibido **sempre como tendência relativa ao histórico do próprio aluno** — nunca como valor absoluto.

---

## 6 · Insight Engine — Fórmulas de Seleção

Especificação matemática do motor que alimenta o slot do hero card. Define o cálculo do score composto, as janelas temporais de cada critério e a função de seleção semanal.

Definição operacional dos fatos: **Regras de Negócio §6 (RN 27–38)**.

### 6a · Score composto

Quando múltiplos fatos disparam, a seleção é por score composto:
Score(fato) = R × wR + A × wA + E × wE

| Componente | Símbolo | Escala | Definição |
|------------|---------|--------|-----------|
| Relevância | R | 0–1 | Força do gatilho (quão acima do critério mínimo está) |
| Raridade | A | 0–1 | 0.3 (comum) · 0.6 (contextual) · 1.0 (raro) |
| Recency | E | 0–1 | 1.0 se não foi headline nas últimas 2 semanas; 0 caso contrário |

**Pesos sugeridos (a calibrar):**

| Peso | Valor inicial | Razão |
|------|--------------|-------|
| wR | 0.45 | Relevância é o componente mais importante — fato muito forte sempre deve vencer |
| wA | 0.35 | Raridade carrega muito sinal narrativo, mas não pode dominar |
| wE | 0.20 | Recency é tiebreaker, não dominante |

**Calibração:** valores iniciais conservadores. Após 4–6 mesociclos de dados reais, revisar a distribuição de fatos selecionados — se um tipo de fato domina excessivamente, ajustar pesos.

### 6b · Cálculo de Relevância (R)

Cada fato define seu critério mínimo (RN 27–36). Relevância mede quão acima do mínimo o aluno está, normalizado em 0–1.

**Exemplo — RN 27 (Acúmulo neural sustentado):**
critério_min = percentil_N ≥ 65 por 3 semanas
percentil_atual = 78, semanas_consecutivas = 5
R_percentil = min(1, (78 - 65) / (100 - 65)) = 0.37
R_persistência = min(1, (5 - 3) / 5) = 0.40
R = 0.6 × R_percentil + 0.4 × R_persistência = 0.38

Cada fato implementa seu próprio cálculo de R com base nos critérios da RN correspondente. Quando o fato apenas atinge o critério mínimo, R ≈ 0.0–0.2. Quando está muito acima, R → 1.0.

### 6c · Raridade (A)

Constante por fato, definida na RN:

| Categoria | A | Fatos |
|-----------|---|-------|
| Comum | 0.30 | RN 27, 29, 31, 32 |
| Contextual | 0.60 | RN 28, 30, 35 |
| Raro | 1.00 | RN 33, 34, 36 |

Fatos contextuais só entram na disputa quando seu contexto se aplica (ex: RN 30 só dispara em fase de deload).

### 6d · Recency (E) — anti-repetição
E = 1.0,  se fato NÃO foi headline na semana_atual - 1 nem na semana_atual - 2
E = 0.0,  caso contrário

**Exceção:** se A(fato) = 1.0 (raro), Recency é sempre 1.0. Fatos raros vencem anti-repetição.

### 6e · Função de seleção
fatos_ativos = [f for f in BIBLIOTECA if dispara(f, dados_aluno)]
se len(fatos_ativos) = 0:
se há_sinal_de_atenção(dados_aluno):
return modo_alerta(RN 37)
senão:
return modo_neutro_contextualizado_por_fase(RN 37)
para cada f em fatos_ativos:
f.score = Score(f)
return argmax(fatos_ativos, key=score)

### 6f · Janelas temporais

Os critérios das RNs operam em janelas temporais específicas. Padronização:

| Janela | Definição |
|--------|-----------|
| `semana_atual` | últimos 7 dias a partir de hoje |
| `semanas_consecutivas` | semanas sem quebra (gap > 5 dias = quebra) |
| `mesociclo_atual` | desde `mesociclo_inicio` até hoje |
| `últimas_N_sessões` | últimas N sessões do mesmo tipo_sessao |

**Importante:** `mesociclo_inicio` é campo explícito no documento do aluno — nunca inferido de datas de sessões (regra fechada na arquitetura).

### 6g · Pendências de calibração

| Item | Status | Descrição |
|------|--------|-----------|
| Pesos wR, wA, wE | A calibrar | Valores iniciais conservadores. Revisar após 4–6 mesociclos. |
| Limiar `≥ 5%` em RN 29 | A calibrar | Pode variar por nível do aluno. Iniciantes têm progressão maior; avançados menor. |
| Variância `≤ 0.15` em RN 35 | A calibrar | Limiar empírico. Validar com perfis reais. |
| Anti-repetição de 2 semanas | A calibrar | Janela pode ser estendida para 3 semanas após uso real. |
| Biblioteca de headlines | A expandir | Headlines atuais são templates; podem evoluir para versões com variantes (anti-fadiga textual). |

---

## ∑ · Fórmula Consolidada

```
CargaObjetiva =
  wN   × Σ [ (kg × reps × séries) × FC × DN × (1 + CT×0.05 + SV×explos×0.05) ]
+ wM   × Σ [ (kg × reps × séries) × IM ]
+ wMet × Σ [ (kg × reps × séries) × FTT × SV × FD ]

CargaInterna  = PSE_relatada × duração_min

RatioAdaptação = CargaObjetiva / CargaInterna
```

### Exemplos numéricos (CargaNorm=1000 para todos)

| Exercício | DN | CT | SV | explos | Amp | Neural |
|-----------|----|----|-----|--------|-----|--------|
| Hack Machine | 4.0 | 2.0 | 3.0 | 0 | 1.10 | 4.400 |
| Agachamento Livre | 8.0 | 6.0 | 5.0 | 0 | 1.30 | 10.400 |
| Snatch (explosivo) | 9.0 | 9.5 | 9.0 | 1 | 1.925 | 17.325 |

---

---

## 6 · Estado de Prontidão e Ajuste de Treino

### 6a · Cálculo do Estado de Prontidão

Calculado a partir do check-in pré-treino do aluno. Escala 1–10.

```
score_disposicao  = disposicao × 3.0
// disposicao: 1=cansado · 2=normal · 3=disposto → mapeia para 3 · 6 · 9

score_cansaco     = cansaco_nivel !== null ? (10 - cansaco_nivel + 1) : 5
// Inverte a escala: cansaco_nivel 10 → score 1 · cansaco_nivel 1 → score 10
// Null → neutro (5)

score_sono        = { ruim: 3, normal: 6, bom: 9 }[sono] ?? 5
score_alimentacao = { ruim: 3, normal: 6, boa: 9 }[alimentacao] ?? 5

estado_prontidao  = round(
  score_disposicao × 0.50 +   // peso maior — resposta principal
  score_cansaco    × 0.20 +   // aprofundamento do cansaço
  score_sono       × 0.20 +   // sono
  score_alimentacao × 0.10    // alimentação — menor peso
)
// Resultado clampado entre 1 e 10
```

**Comportamento quando aluno pula o check-in:**
- `disposicao: null` → `estado_prontidao: 5` (neutro)
- Sem ajuste de treino — prescrição original mantida

### 6b · Fator de Prontidão

Converte `estado_prontidao` em multiplicador de volume e carga.

```
fator_prontidao(p):
  p >= 8  → { volume: 1.00, carga: 1.00 }   // treino completo · pode progredir
  p >= 6  → { volume: 0.90, carga: 1.00 }   // volume −10% · carga mantida
  p >= 4  → { volume: 0.75, carga: 0.90 }   // volume −25% · carga −10%
  p >= 2  → { volume: 0.60, carga: 0.85 }   // sessão leve
  p == 1  → { volume: 0.00, carga: 0.00 }   // repouso recomendado
```

### 6c · IC Ajustado

```
ic_ajustado = ic_planejado × fator_prontidao(estado_prontidao).volume
```

> **Nota:** `ic_planejado` só existe quando a tela de prescrição do PT estiver ativa.
> Enquanto isso, `ic_ajustado` é calculado sobre o IC médio histórico do aluno como referência.

### 6d · Delta IC

```
delta_ic = ic_executado − ic_planejado
```

- `delta_ic > 0` → aluno superou o prescrito
- `delta_ic < 0` → aluno ficou abaixo
- Exibido ao aluno com contexto do check-in: "Você chegou cansado e treinou X% abaixo do planejado — dentro do esperado."

### 6e · Perfil de Recuperação (janela 4 semanas)

```
disponibilidade_media = média(estado_prontidao) das últimas 28 sessões

variabilidade = desvio_padrao(estado_prontidao):
  < 1.5 → "baixa"
  1.5–2.5 → "media"
  > 2.5 → "alta"

padrao_semanal[dia] = média(estado_prontidao | dia_semana == dia)
```

O `padrao_semanal` permite ao sistema e ao PT identificar padrões como:
"Este aluno consistentemente chega melhor às quintas — agendar sessões de alta intensidade nesse dia."

---

## Pendências

| Item | Status | Descrição |
|------|--------|-----------|
| fatorAmplificação (0.05) | Pendente calibração | Valor inicial conservador. Calibrar com dados reais das primeiras sessões. |
| TUT base (3s/rep) | Pendente decisão | Pode se tornar configurável por tipo de exercício ou valência. Definir antes de popular cadência. |
| descanso_referencia (90s) | Pendente decisão | Candidato a configurável por valência ou por PT. |
| FTT quando cadência não prescrita | Pendente confirmação | Comportamento padrão proposto: FTT=1. |
| FC — recalibração de escala (0.3–1.5) | Pendente | Escala definida. Valores do banco precisam de conversão antes do uso em produção. |
| **IM — recalibração nos isolados** | **⚠ Prioritário** | Com FC fora de CargaNorm, isolados (Extensora, Flexora, Rosca, etc.) terão Mecânica maior. Revisão exercício a exercício necessária. |
| `duração_min` no schema | Pendente | Campo não existe em momentum-sessions. Necessário para CargaInterna. |
| `ritmo_delta` | Pendente confirmação | Campo presente nas sessões (ex: 4.46) sem definição formal. Hipótese: variação longitudinal do Ritmo na janela. |
| pse_mode por aluno | Debate pendente | Granularidade de coleta: série / exercício / sessão. Afeta todo o fluxo de PSE_calc. |
| 1RM — normalização | Futuro | Não está no modelo atual. Preparar no banco desde o início para comparabilidade inter-alunos. |
| Wearables (FC cardíaca) | Reservado premium | Estrutura do modelo já comporta essa adição. |

---

## 7 · Progressão Intra-Mesociclo — Variáveis e Hierarquia

### 7a · Regra geral

A progressão de um exercício é determinada por **objetivo + categoria**, não pela categoria isolada.

```
objetivo × categoria → variável-mãe + variável secundária + limites
```

| Objetivo | Variável-mãe | Variável secundária | Observação |
|---|---|---|---|
| Hipertrofia | Volume (séries) | Carga | Carga progride quando PSE ficou dentro do alvo por N sessões |
| Força Máxima | Carga (%1RM) | Volume | Volume tem teto por CT do exercício |
| Potência | Carga (%1RM) | Velocidade/Intenção | SV determina o potencial de transferência |
| Técnica | Carga (leve, controlada) | Volume | CT alto → volume tem teto mais baixo |
| Metabólico | Densidade (descanso↓) | Volume | FD como variável principal |
| Resistência de Força | Volume | Densidade | Descanso é reduzido conforme adaptação |

### 7b · Curvas de progressão disponíveis

O PT seleciona uma curva base para cada exercício (ou herda do mesociclo). Pode personalizar ponto a ponto — inclusive editando graficamente (ver §7c · Pendente).

| Curva | Comportamento | Uso típico |
|---|---|---|
| Linear | +X unidades/semana de forma constante | Iniciantes, curto prazo |
| Step-load | Sobe 2–3 semanas → mantém 1 → sobe | Intermediários |
| Ondulatória | Alternância de semanas pesadas e leves | DUP, avançados |
| Block | Acumulação → Intensificação → Realização | Powerlifting, força-pico |
| Deload programado | Queda intencional em semana definida | Qualquer nível |

### 7c · Gatilho de progressão automática

```
N_sessoes_alvo = base_por_nivel × fator_variabilidade

base_por_nivel:
  Iniciante    → 2 sessões consecutivas dentro do alvo
  Intermediário → 1 sessão dentro do alvo
  Avançado      → 1 sessão dentro do alvo

fator_variabilidade (perfil_recuperacao.variabilidade):
  alta   → ×2 (mais sessões necessárias para confirmar)
  media  → ×1
  baixa  → ×1

fator_delta_pse:
  ΔPSE crescente nas últimas 3 sessões → segura progressão automática independente de N
```

Progressão aplicada automaticamente → PT notificado (RN 13 modo automático).

---

## ∑ Pendências adicionadas em Mar 2026

| Item | Status | Descrição |
|---|---|---|
| **Curvas editáveis graficamente** | **⚠ Pendente implementação** | PT arrasta pontos da curva de volume/carga no gráfico de projeção → sistema recalcula IC planejado, N/M/Met e dispara alertas de overtraining. Afeta: tela de prescrição, modal de edição de mesociclo em andamento. |
| **campo `categoria` no banco** | ✅ Implementado v1.1.0 | 17 categorias, 84 exercícios. Ver momentum-exercises.json. |
| **Progressão por objetivo × categoria** | ✅ Documentado §7 | Variável-mãe e secundária por combinação. Implementar na tela de prescrição. |
