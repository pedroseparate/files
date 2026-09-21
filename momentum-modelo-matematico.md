# Momentum · Modelo Matemático
**v0.3 · Set 2026**

Sistema de quantificação de carga fisiológica por sessão. Define como o Momentum transforma dados de execução em índices comparáveis, separando carga objetiva de carga interna percebida.

---

## 0 · Os 5 Coeficientes

Fixos no banco de exercícios — propriedades do movimento, não do aluno. **Alterações são exclusivas do time Momentum.**

| Coef. | Escala | Nome | Papel no modelo |
|-------|--------|------|-----------------|
| CT | 0–10 | Complexidade Técnica | Amplificador do custo neural em movimentos complexos. Ex: Hack Machine CT=2.0 · Snatch CT=9.5 |
| IM | 0–10 | Impacto Mecânico | Estresse mecânico direto sobre tecidos. Base do componente Mecânica. Ex: Leg Press IM=6.0 · Agachamento Livre IM=9.0 |
| DN | 0–10 | Demanda Neural | Demanda neural base do exercício. Base do componente Neural, amplificado por CT e SV. |
| SV | 0–10 | Sensibilidade à Velocidade | Amplifica custo neural quando intenção explosiva é prescrita pelo PT. |
| FC | 0.3–1.5 | Fator de Carga Neural | Grau de liberdade do movimento — custo de estabilização e coordenação. **Entra apenas no componente Neural, não em CargaNorm.** Ex: Agachamento Livre FC=1.2 · Leg Press FC=0.45 · Extensora FC=0.2 |

**FC e DN: distintos mas relacionados (r=0.88).** FC captura grau de liberdade (livre vs guiado). DN captura complexidade de coordenação (programação motora). Agachamento e Clean têm DN próximos, mas FC do Agachamento é maior porque permite carga absoluta maior sobre o SNC.

---

## 1 · Carga Normalizada (CargaNorm)

Base de todos os componentes. FC **não entra aqui** — fisiologicamente incorreto.

```
CargaNorm_i = Σ_j (kg_j × reps_j)        sobre as séries j do exercício i
```

A forma anterior — `kg_i × reps_i × séries_i` — **assumia implicitamente que todas as séries
do exercício têm a mesma carga e as mesmas repetições**, assunção nunca declarada. `Σ(kg×r)` é
a generalização exata que remove essa assunção: no caso uniforme as duas formas são
identicamente iguais, então nenhum valor histórico muda.

Médias por exercício foram descartadas (set/2026). Dentro de um exercício, kg e reps são
anticorrelacionadas por construção — mais peso, menos repetições — e o produto das médias de
duas variáveis anticorrelacionadas **superestima sistematicamente** o produto real: +0,9% em
top-set com back-off, +2,7% em pirâmide, +27,3% em drop set. O erro não é ruído que se cancela
ao longo de um mesociclo; cresce com a dispersão entre séries, ou seja, justamente nos
protocolos em que a carga foi manipulada de propósito. Viés correlacionado com o sinal medido.

> **⚠ Consequência da saída de FC do CargaNorm:** IM dos exercícios isolados (Extensora, Flexora, Rosca, etc.) precisa ser recalibrado. Com FC fora de CargaNorm, a Mecânica desses exercícios aumenta — IM deve refletir honestamente a tensão mecânica local.

---

## 2 · Componentes Fisiológicos

**Fórmula única para todos os contextos** — IC por exercício, radar do aluno, soma da sessão. Não existem fórmulas "simplificadas" separadas.

### 2a · Componente Neural

```
Neural_i = CargaNorm_i × FC_i × DN_i × (1 + CT_i×0.05 + SV_i×explos_i×0.05)
```

### 2b · Componente Mecânica

```
Mecânica_i = CargaNorm_i × IM_i
```

> **⚠ IM precisa ser recalibrado nos isolados** após a mudança de FC. Ver pendências no §∑.

### 2c · Componente Metabólica

```
FTT_i = TUT_i / TUT_base_i       (1 quando cadência não prescrita — decisão fechada)
FD_i  = 90 / descanso_s_i        (fator de densidade; referência 90s)

Metabólica_i = CargaNorm_i × FTT_i × SV_i × FD_i
```

**Na v1, `descanso_s` é o descanso PRESCRITO** (`alvo.descanso_s`, que viaja da prescrição
para a sessão por D3.5), não o executado. O descanso é tratado como **output para a aluna** —
exibido junto do cronômetro na tela de treino — e não como input do modelo.

Consequência declarada: **FD reflete a intenção de programação e não varia com a execução.**
Duas sessões do mesmo exercício, uma cumprida com 90s de pausa e outra com 180s, produzem a
mesma Metabólica. O que FD mede na v1 é a densidade *prescrita* pelo PT, não a densidade
*realizada* pela aluna.

Isso é decisão de escopo, não limitação técnica: capturar o descanso real é barato — o
cronômetro já roda e o valor é descartado — e está registrado como pendência de v2. A função
`onSessionWrite` já lê o campo executado quando ele existe, caindo para o prescrito quando
não; ligar a captura no cliente basta para FD passar a medir execução, sem tocar no modelo.

### 2d · Radar do aluno (proporção dimensional)

Mesma fórmula, camada de apresentação diferente:

```
soma = Neural_sessao + Mecânica_sessao + Metabólica_sessao
radar_neural     = Neural_sessao / soma        (0–1)
radar_mecanica   = Mecânica_sessao / soma      (0–1)
radar_metabolica = Metabólica_sessao / soma    (0–1)
```

---

## 3 · Soma da Sessão

```
Neural_sessao     = Σ Neural_i
Mecânica_sessao   = Σ Mecânica_i
Metabólica_sessao = Σ Metabólica_i
```

---

## 4 · Carga Objetiva da Sessão

```
CargaObjetiva = (wN × Neural_sessao) + (wM × Mecânica_sessao) + (wMet × Metabólica_sessao)
```

Pesos definidos pelo PT. `wN + wM + wMet` não precisam somar 1.

| Valência | wN | wM | wMet |
|----------|----|----|------|
| Força Máxima | 0.50 | 0.35 | 0.15 |
| Força Hipertrófica | 0.30 | 0.40 | 0.30 |
| Resistência de Força | 0.20 | 0.25 | 0.55 |
| Potência/Pliometria | 0.50 | 0.30 | 0.20 |

---

## 5 · Carga Interna e PSE

### 5a · Carga Interna (modelo Foster)

```
CargaInterna = PSE_relatada × duração_min
```

> **⚠ `duração_min` não existe no schema atual de momentum-sessions — precisa ser adicionado antes de ativar CargaInterna.**

### 5b · PSE — calculada, relatada, e ritmo

```
PSE_exercício = média(PSE das séries do exercício)
PSE_calc      = Σ(CargaNorm_i × PSE_exercício_i) / Σ(CargaNorm_i)
PSE_relatada  = prompt ao finalizar a sessão
PSE_ritmo     = (PSE_calc × α) + (PSE_relatada × (1 − α))
```

**α por nível:**
- Iniciante: α=0.85
- Intermediário: α=0.65
- Avançado: α=0.40
- Personalizado: α livre

**PSE_ritmo é obrigatório no cálculo do Ritmo.** Uso de `pse` cru é incorreto.

**ΔPSE:**
```
ΔPSE = PSE_relatada − PSE_calc
```

---

## 6 · Ritmo de Adaptação

### 6a · Fórmula base

```
Ritmo_sessao = CargaObjetiva / PSE_ritmo
```

Janela rolante de 4 semanas. Compara metade recente vs metade antiga.

### 6b · Estados

| Estado | Delta % | Ação |
|--------|---------|------|
| `alta` | ≥ +10% | Corpo adaptado — candidato a progressão |
| `estavel` | −10% a +10% | Dentro do esperado |
| `baixo` | −20% a −10% | Alerta PT · possível fadiga |
| `sobrecarga` | < −20% | Alerta urgente · sugestão de deload |

> **Nomenclatura unificada:** `alta | estavel | baixo | sobrecarga` em todo o sistema.

### 6c · Adapter de Periodização

A fórmula base é a mesma — o que muda é a **unidade de agrupamento** e a **janela de comparação**.

| Modelo | Agrupamento | Janela | Comportamento especial |
|--------|-------------|--------|----------------------|
| **Linear** | Todas as sessões | Metade recente vs antiga | Nenhum |
| **Block** | Sessões da fase atual | Dentro da mesma fase | Queda de IC na transição Acum→Int é esperada |
| **DUP** | Por tipo_sessao | Por tipo, separadamente | Alerta global só se TODOS os tipos em queda |
| **Conjugado** | Por exercício principal | Mesma sessão semana anterior | Progressão por exercício |
| **Assimétrico** | Por divisão (A/B/C/D/E) | Mesma divisão ciclo anterior | Compara dia consigo mesmo |
| **Autoregulado** | Todas as sessões | Carga vs RPE target | Futuro — não implementado |

**Block — awareness de fase:**

| Fase | IC esperado | PSE esperado |
|------|------------|-------------|
| Acumulação | Subindo | Moderado |
| Intensificação | Caindo | Subindo |
| Realização | Estável (taper) | Baixo |

Na Intensificação, queda de IC < 25% mantém estado `estavel` com flag `fase_alinhado: true`.

**DUP — ritmos paralelos:**

Ritmo independente por tipo_sessao. Estado global: queda só se todos os tipos em queda simultaneamente.

### 6d · Campos no student doc

```json
{
  "modelo_periodizacao": "linear | dup | block | conjugado | assimetrico",
  "fases_periodizacao": [
    { "nome": "acumulacao", "semanas": [1, 2, 3] },
    { "nome": "intensificacao", "semanas": [4, 5] },
    { "nome": "realizacao", "semanas": [6] }
  ]
}
```

Fallback: infere do nome do mesociclo. Default: `linear`.

### 6e · Hierarquia de Progressão por Objetivo

A progressão de um exercício é determinada por **objetivo + categoria** — define qual variável progride primeiro e qual é secundária.

```
objetivo × categoria → variável-mãe + variável secundária
```

| Objetivo | Variável-mãe | Variável secundária | Observação |
|---|---|---|---|
| Hipertrofia | Volume (séries) | Carga | Carga progride quando PSE ficou dentro do alvo por N sessões |
| Força Máxima | Carga (%1RM) | Volume | Volume tem teto por CT do exercício |
| Potência | Carga (%1RM) | Velocidade/Intenção | SV determina o potencial de transferência |
| Técnica | Carga (leve, controlada) | Volume | CT alto → volume tem teto mais baixo |
| Metabólico | Densidade (descanso↓) | Volume | FD como variável principal |
| Resistência de Força | Volume | Densidade | Descanso é reduzido conforme adaptação |

> **⚠ Revisar à luz da decisão RN23 (ago/2026)** — ajuste fino pode ser necessário após consolidação das regras de negócio de agosto.

### 6f · Gatilho de Progressão Automática

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

## 7 · Scores do Aluno (0–10)

### 7a · Cálculo

Scores são **computados dinamicamente** — nunca hardcoded.

```
Score(dimensão) = percentil_rolling(últimas 4 sessões no histórico total) × 10
```

| Score | Fonte | Cálculo |
|-------|-------|---------|
| Neural | ic_neural | Percentil rolling × 10 |
| Mecânica | ic_mecanica | Percentil rolling × 10 |
| Metabólica | ic_metabolica | Percentil rolling × 10 |
| Técnica | CT médio exercícios recentes | CT_avg / 10 × 10 |
| Ritmo | Delta do calcRitmo | delta mapeado para 0–10 |
| Momentum | Média ponderada | 0.25×N + 0.30×M + 0.25×Met + 0.20×Ritmo |

### 7b · Contexto editorial

Cada score recebe texto contextual baseado em `ritmo_estado` × tendência do score (up/ok/dn). Tabela `SCORE_CTX_MAP` no app do aluno.

---

## 8 · RatioAdaptação

```
RatioAdaptação = CargaObjetiva / CargaInterna
```

**Sempre como tendência relativa ao histórico do próprio aluno — nunca como valor absoluto.**

---

## ∑ · Fórmula Consolidada

```
CargaObjetiva =
  wN   × Σ [ (kg × reps × séries) × FC × DN × (1 + CT×0.05 + SV×explos×0.05) ]
+ wM   × Σ [ (kg × reps × séries) × IM ]
+ wMet × Σ [ (kg × reps × séries) × FTT × SV × FD ]

CargaInterna  = PSE_relatada × duração_min
Ritmo         = CargaObjetiva / PSE_ritmo  (com adapter de periodização)
Score(dim)    = percentil_rolling(dim, 4 sessões) × 10
```

---

## Pendências

| Item | Status | Descrição |
|------|--------|-----------|
| fatorAmplificação (0.05) | Pendente calibração | Calibrar com dados reais das primeiras sessões. |
| TUT base (3s/rep) | Pendente decisão | Pode tornar-se configurável por tipo de exercício ou valência. |
| descanso_referencia (90s) | Pendente decisão | Candidato a configurável por valência ou por PT. |
| FC — recalibração escala (0.3–1.5) | Pendente | Valores do banco precisam conversão antes do uso em produção. |
| **IM — recalibração isolados** | **⚠ Prioritário** | Com FC fora de CargaNorm, isolados (Extensora, Flexora, Rosca, etc.) terão Mecânica maior. Revisão exercício a exercício — julgamento fisiológico do PT. |
| `duração_min` no schema | Pendente | Campo não existe em momentum-sessions. Necessário para CargaInterna. |
| `ritmo_delta` | Pendente confirmação | Campo presente nas sessões (ex: 4.46) sem definição formal. Hipótese: variação longitudinal do Ritmo na janela. |
| tipo_sessao para DUP | Pendente | Campo necessário em sessões DUP. Sem ele, usa `tipo` como proxy. |
| fases_periodizacao para Block | Pendente | Array de fases. Sem ele, Block = Linear. |
| modelo_periodizacao nos alunos | Pendente | Campo novo. Inferido do mesociclo como fallback. |
| pse_mode por aluno | Debate pendente | Granularidade de coleta: série / exercício / sessão. Afeta todo o fluxo de PSE_calc. |
| 1RM — normalização | Futuro | Não está no modelo atual. Preparar no banco para comparabilidade inter-alunos. |
| Autoregulado | Futuro | Documentado, não implementado. |
| Wearables | Reservado premium | Estrutura do modelo já comporta. |
