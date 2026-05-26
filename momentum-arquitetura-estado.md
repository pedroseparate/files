# Momentum · Decisões Arquiteturais e Estado do Projeto
**v0.1 · Mar 2026**

Documento de referência para contexto de desenvolvimento. Registra o que já foi decidido (não reproponha), o que está pendente, e o estado atual de implementação.

---

## Decisões Arquiteturais Fechadas

Estas decisões foram tomadas após análise e **não devem ser revertidas sem justificativa fisiológica explícita.**


### Decisão — Fórmula da Metabólica (Mar 2026)

**Fechado:** SV removido do componente Metabólica.

**Antes:** `Metabólica = CargaNorm × SV × FD`
**Depois:** `Metabólica = CargaNorm × FTT × FD` (FTT=1 quando cadência não prescrita)

**Razão fisiológica:** SV captura recrutamento de unidades motoras rápidas e coordenação intermuscular — custo neural, não metabólico. Exercícios explosivos têm via anaeróbia alática predominante, cujo custo metabólico total não é maior que séries longas e densas. FTT (tempo sob tensão) e FD (densidade de descanso) capturam o custo oxidativo e acúmulo de metabólitos de forma mais precisa e independente do caráter neural do exercício.

### Modelo Matemático

| Decisão | O que é | Por quê está fechado |
|---------|---------|---------------------|
| **FC fora de CargaNorm** | FC (Fator de Carga Neural) entra apenas no componente Neural, não multiplica kg×reps×séries | FC captura estabilização/coordenação — não afeta tensão mecânica nem custo metabólico. Fisiologicamente desonesto em CargaNorm. |
| **CargaInterna separada de CargaObjetiva** | CargaInterna = PSE_relatada × duração_min (modelo Foster). CargaObjetiva é o índice objetivo. | PSE como multiplicador da carga objetiva distorceria o histórico — uma sessão fácil pareceria objetivamente menos intensa. Os dois índices contam histórias complementares. |
| **RatioAdaptação sempre como tendência** | CargaObjetiva ÷ CargaInterna é estruturalmente alto por diferença de escala. | Nunca exibir como valor absoluto. Sempre relativo ao histórico do próprio aluno. |
| **CT e SV somam (não multiplicam) no amplificador** | `(1 + CT×0.05 + SV×explos×0.05)` | Adição mantém amplificadores independentes e calibráveis. Multiplicação geraria efeitos compostos difíceis de corrigir em exercícios com ambos os coeficientes altos. |
| **FTT=1 quando cadência não prescrita** | Comportamento padrão para metabólica | Confirmar antes de implementar em produção. |
| **Coeficientes fixos no banco** | CT, IM, DN, SV, FC são propriedades do movimento — não do aluno | Alterações exclusivas do time Momentum. PT e aluno não modificam. |
| **Nível não tem promoção automática** | Iniciante/Intermediário/Avançado atribuído manualmente pelo PT | PT tem a palavra final sobre o nível — não existe threshold automático de promoção. |
| **Confirmação dupla de PR** | Record só confirmado após 2 sessões superando o anterior | Exceção: conquistas de iniciante e records de performance (tempo, reps, rounds) — confirmados imediatamente. |

### Arquitetura de Dados

| Decisão | O que é |
|---------|---------|
| **Firebase Firestore** como única fonte de dados | Coleções: `exercises`, `students`, `sessions` |
| **`nome` como campo autoritativo** | `exercise_id` nos registros legados é não-confiável. Usar `EX_NAME_MAP` com lookup normalizado por nome para resolver exercícios. |
| **Single-file HTML** | Toda a UI do dashboard em um único arquivo ~380KB. Mantido assim até refatoração planejada. |
| **Mobile-first** | Viewport alvo: 375–430px. Bottom-nav pattern. |
| **`onSnapshot()` listeners** | Real-time updates via Firestore. |
| **PSE por série** | Granularidade de coleta padrão. Campo `pse_mode` no perfil do aluno pode alterar para exercício ou sessão — **decisão pendente, afeta todo o fluxo de PSE_calc.** |

### Regras de Negócio

| Decisão | O que é |
|---------|---------|
| **Série encerrada = imutável pelo aluno** | PT pode editar via RN 11 com log. Aluno nunca. |
| **Exercício extra não entra na aderência** | Entra no volume total, componentes calculados, mas `extra=true` exclui da aderência. |
| **Timeout de sessão: 10 minutos** | Sem interação por 10min → `abandonada`. Tudo calculado com o executado. |
| **Modo progressão: manual vs automático** | PT configura por microciclo. Manual = PT aprova. Automático = aplica direto. |

---

## Pendências Críticas (bloqueadoras)

### ⚠ IM — recalibração nos exercícios isolados
Com FC fora de CargaNorm, exercícios isolados (Extensora, Flexora, Rosca, Adutora, Abdutora, etc.) terão Mecânica maior do que o calibrado originalmente. IM foi definido assumindo que FC já comprimia a CargaNorm. Revisão exercício a exercício necessária — **julgamento fisiológico do PT.**

### ⚠ `duração_min` no schema de sessions
Campo necessário para cálculo da CargaInterna (modelo Foster). Não existe atualmente em momentum-sessions. Precisa ser adicionado antes de ativar CargaInterna.

### ⚠ Tela de Prescrição do PT
**Bottleneck identificado para o ciclo completo PT → Atleta → Banco.** Sem essa tela, o fluxo de criação de sessões planejadas pelo PT não fecha. É a próxima tela crítica a construir.

---

## Pendências Não-Críticas

| Item | Descrição |
|------|-----------|
| FC — recalibração de escala (0.3–1.5) | Escala definida. Valores do banco precisam de conversão antes do uso em produção. |
| `ritmo_delta` | Campo presente nas sessões (ex: 4.46) sem definição formal. Hipótese: variação longitudinal do Ritmo na janela de 4 semanas. **Confirmar com João Pedro.** |
| fatorAmplificação (0.05) | Valor conservador inicial. Calibrar com dados reais das primeiras sessões. |
| TUT base (3s/rep) | Configurável futuramente por tipo de exercício ou valência. |
| descanso_referencia (90s) | Configurável futuramente por valência ou PT. |
| `pse_mode` por aluno | Granularidade de coleta PSE. Debate pendente — afeta fluxo inteiro. |
| Dumbbell bilateral — kg-doubling | Lógica de duplicar kg para cálculo de IC em exercícios bilaterais com halteres (ex: Supino c/ Halteres = 2×carga). |
| Exercícios faltantes no banco | Ex: Supino Inclinado c/ Halteres. Adicionar variantes de halteres. |
| 1RM — normalização | Preparar no banco desde o início para comparabilidade inter-alunos. |
| Wearables (FC cardíaca) | Reservado para versão premium. Estrutura do modelo já comporta. |
| Instagram session card | Card de resumo de sessão estilo Strava, glassmorphism, "hemômetro", frase gerada por IA. Feature planejada. |

---

## Estado Atual do Projeto

**Estimativa de conclusão (uso pessoal):** ~40% · ~8–10 sessões de desenvolvimento

### Telas e Features Implementadas
- PT Dashboard v5 com schema correto e layout responsivo
- Simulação Julia Duzzi (página de demo de atleta)
- Dashboard do atleta (cliente Enrique)
- Landing page (`index-mobile.html`) com comparativo Terra vs Extensora e bloco de vetores exclusivos
- Cálculo de IC, Neural, Mecânica, Metabólica funcionando
- Chips automáticos de sessão (fadiga precoce, colapso de reps, etc.)
- Firestore como fonte única de dados

### Telas Pendentes
- **Tela de Prescrição do PT** ← crítica / próxima
- Fluxo de execução do treino pelo atleta
- Onboarding de novo aluno
- Tela de progressão e aprovação

---

## Design System (imutável)

| Elemento | Valor |
|---------|-------|
| Fonte display | Cormorant Garamond (serif, itálico) |
| Fonte mono | IBM Plex Mono |
| Cor primária | `--gold: #c8a060` |
| Cor secundária | `--copper: #8a6030` |
| Background | `#0e0b08` (dark) · `#f5f0e6` (light/page) |
| Paleta completa | night/gold/copper/moss/slate — ver CSS vars no dashboard |

---

## Contexto do PT (João Pedro)

- Personal Trainer — domínio fisiológico fluente, usa como PT e dev
- Atletas atuais no sistema: Julia Duzzi, Enrique
- Firestore project: `momentum-br`
- Coleções: `exercises`, `students`, `sessions`
- Campo autoritativo para exercícios: `nome` (não `exercise_id`)
- Normalização de nome: Unicode + trim + lowercase para lookup via `EX_NAME_MAP`

---

## Nota sobre Check-in Pré-treino (feature proposta, não implementada)

O sistema atual captura contexto *retrospectivamente* via ΔPSE e chips automáticos. Uma feature de check-in pré-treino adicionaria uma camada *prospectiva*:

**Proposta:**
- 1 pergunta obrigatória antes do treino: "Como você está hoje?" (🔥 Pronto / 😐 Ok / 🥱 Cansado / 🤕 Pesado)
- 2 perguntas opcionais: qualidade de sono + alimentação adequada
- Dado de disponibilidade enriquece interpretação do ΔPSE e cria histórico longitudinal de "quando este aluno chega fadigado"
- **Não** altera a prescrição do PT na v1 — apenas alimenta o dashboard analítico

**O que NÃO fazer na v1:** ajuste automático de volume baseado em disponibilidade (requereria schema de prescrição com faixas min/max — decisão arquitetural separada).

**Chips da RN 26 já são a narrativa** — a diferença é que hoje são PT-facing only. Versão aluno dos chips é uma evolução natural, não uma reescrita.

---

## Ideias Futuras — Mídia e Marketing

### Conteúdo: Momentum e a Física do Treino

**Origem:** conversa de produto em Mar 2026, surgiu da distinção entre Ritmo e Momentum no modelo matemático.

**Conceito central:**

A analogia com física é quase direta:

- `p = m × v` — momentum = massa × velocidade
- No treino: **consistência** é a massa, **progressão de carga** é a velocidade
- Um aluno que treina muito sem progredir tem "massa" sem "velocidade"
- Um aluno que progride rápido mas falta tem "velocidade" sem "massa"
- **Ritmo** é a derivada: `dp/dt` — taxa de mudança do momentum. Alta num ponto não garante trajetória positiva.

**Formato sugerido: vídeo curto (60–90s)**

- Ato 1 — A fórmula no quadro. `p = m × v`. Simples, clássica.
- Ato 2 — "E se massa fosse consistência? E velocidade fosse progressão de carga?" Mesma fórmula, novo significado.
- Ato 3 — Ritmo como derivada. Um sprint de uma semana não cria momentum. Uma boa semana dentro de uma trajetória positiva, sim.
- Fechamento — "É por isso que o app se chama Momentum. Não mede o quanto você treinou hoje. Mede a direção que você está tomando."

**Por que funciona:**
- Conecta física de ensino médio com algo que todo praticante sente mas não consegue articular
- Conteúdo de posicionamento — não vende, educa
- Posiciona o PT como profissional que pensa diferente
- Alto potencial de engajamento — quem já usou o termo "momentum" sem saber a física vai compartilhar

---

## Decisões de Escala — Scores

### Score Momentum — escala 0–10 [DECISÃO FECHADA · Mar 2026]

**Escala oficial: 0–10.** Alinhada com todos os outros scores (Neural, Mecânica, Metabólica, Técnica, Ritmo).

**Histórico:** Os valores originais no banco (1.8, 2.1, 2.9, 3.2, 3.8, 3.9, 4.6…) foram estimativas qualitativas geradas na criação do banco, escala implícita 0–5. A partir desta decisão, os valores no Firestore precisam ser multiplicados por 2.

**Ação necessária no banco:** atualizar `scores.momentum` de todos os alunos (×2):
- fernanda_lima: 1.8 → 3.6
- roberto_silva: 2.1 → 4.2
- jacqueline: 2.9 → 5.8
- lara_soares: 3.2 → 6.4
- ana_beatriz: 3.8 → 7.6
- paula_freitas: 3.0 → 6.0
- carlos_mendes: 3.9 → 7.8
- mariana_costa: 4.6 → 9.2

**Impacto no código:** toda referência a `momentum / 5` deve ser `momentum / 10`. Já corrigido em `momentum-aluno.html`. Verificar também `momentum-pt-dashboard.html` e qualquer outra página que use o arco SVG.

**Fórmula futura (pendente implementação):**
```
ScoreMomentum = RatioAdaptação_norm×0.40 + Consistência_norm×0.35 + ProgressãoCarga_norm×0.25
```
Normalizado pelo histórico do próprio aluno. Nunca valor absoluto — sempre tendência relativa.

**Frases contextuais (Opção A — textos fixos por combinação de variáveis):**
O sistema cruza `ritmo_estado` + `dim_dominante` + tendência do score (subindo/estável/caindo) para escolher frases de um banco de textos predefinido. Banco de frases construído em parceria com Claude — localizado no código do app como constante `SCORE_CTX_MAP`. Opção B (IA gera frase longa no modal) coexiste com a Opção A.

---

## Pendências v2 — Revisões Necessárias

### Pesos wN/wM/wMet por tipo de sessão [PENDENTE REVISÃO FISIOLÓGICA]

Valores atuais são defaults conservadores, não calibrados com dados reais.
Precisam de revisão antes de usar em produção com alunos reais.

| Tipo de sessão | wN | wM | wMet |
|----------------|----|----|------|
| Força / Neural | 0.50 | 0.35 | 0.15 |
| Hipertrofia / Upper-Lower | 0.30 | 0.45 | 0.25 |
| Full Body / Funcional | 0.25 | 0.40 | 0.35 |
| Metabólico / Condicionamento | 0.20 | 0.25 | 0.55 |

**Ação v2:** João Pedro revisa com base nos primeiros ciclos de dados reais.

---


---

## Pendência v2 — Metabólica com FTT e FD no engine de recálculo

**Arquivo:** `momentum-pt-dashboard.html` · função `calcExIC()`

**Implementação atual (incorreta):**
```js
ic_metabolica: round2(cn * c.SV)
```

**Implementação correta (documentação §2c):**
```js
// FTT = 1 quando cadência não prescrita (padrão fechado)
// FD = 90 / descanso_s (fator de densidade; referência 90s)
const FD = descanso_s > 0 ? 90 / descanso_s : 1;
ic_metabolica: round2(cn * 1 * c.SV * FD)
```

**Impacto atual:** baixo — maioria das sessões tem descanso=90s → FD=1, resultado idêntico.
Impacto real quando o PT passar a prescrever descansos diferentes de 90s.

**Nota arquitetural:** o cálculo de IC acontece no PT Dashboard (engine de recálculo),
não no app do aluno. O aluno salva o executado bruto; o PT Dashboard recalcula via
`recalcStudentAfterSession()` ao detectar `_recalculated: false`.

## Roadmap v2 — Features para Usuário Avançado

*Contexto: análise feita pensando como um usuário avançado de musculação com interesse específico em força e hipertrofia, familiarizado com periodização, MEV/MAV/MRV, RPE/RIR. Registrado em 26/Mar/2026.*

---

### 1. Volume por grupo muscular por semana [PRIORITÁRIO]

O dado mais acionável para o usuário avançado de hipertrofia. Ele gerencia volume semanal por grupo muscular conscientemente e nenhum app entrega isso bem.

**O que entregar:**
- Séries efetivas por grupo muscular por semana (ex: quadríceps: 14 séries)
- Comparação com MEV/MAV estimado (configurável pelo PT no mesociclo)
- Ponderado pelo IC mecânico de cada exercício — não só contagem bruta de séries
- Gráfico de tendência semana a semana

**Dado necessário:** mapeamento exercício → grupos musculares (já existe no campo `muscles` de exercises.json)

---

### 2. 1RM estimado e progressão de força relativa

**O que entregar:**
- Fórmula de Epley nos exercícios principais: `1RM = kg × (1 + reps/30)`
- Gráfico longitudinal de 1RM estimado por exercício principal
- Frase de impacto: "Seu 1RM estimado no agachamento subiu de 118kg → 124kg nas últimas 4 semanas"
- Confirmação dupla já implementada (RN 12) — integrar aqui

---

### 3. Deload detector + curva de fadiga visível

Atualmente o `ritmo_estado` já captura isso, mas não está exposto de forma granular o suficiente para o usuário avançado.

**O que entregar:**
- Curva de fadiga acumulada visível na tela de evolução: PSE subindo + IC caindo = zona de atenção
- Sinalização antecipada — antes do deload virar obrigatório
- Diferenciação entre fadiga aguda (uma sessão ruim) e fadiga acumulada (tendência de 2+ semanas)

---

### 4. Frequência por padrão de movimento

**O que entregar:**
- Contagem semanal: push, pull, squat, hinge, carry, core
- Alerta de desequilíbrio: "você treinou push 4× e pull 2× esta semana"
- Dado disponível: campo `pattern` em exercises.json (squat, hinge, push_h, push_v, pull_h, pull_v...)

---

### 5. RPE/RIR por série na tela de treino [MENOR DO QUE PARECE]

O schema já salva PSE em 3 níveis: por série, por exercício e por sessão. O banco está correto.

**O que falta:** a tela de execução captura um PSE por exercício e replica o mesmo valor em todas as séries — todas ficam . O widget já existe, basta não propagar o mesmo valor para todas as séries e sim pedir confirmação a cada série individualmente.

**O que entregar:**
- No widget de série: PSE pedido a cada série, não uma vez por exercício
- Diferenciação visual intra-exercício: série 1 PSE 6 → série 4 PSE 9 (fadiga visível)
- PSE_calc mais preciso automaticamente — o modelo matemático já está preparado

---

### 6. Comparação inter-mesociclo

**O que entregar:**
- "Mesociclo atual vs anterior: volume mecânico +18%, progressão nos compostos +12%"
- Radar comparativo: este ciclo vs ciclo anterior
- Requer armazenamento de `momentum_snapshot` por mesociclo (estrutura pendente)

---

### 7. Projeção de carga

**O que entregar:**
- Com base na progressão atual (slope de IC): "Se mantiver o ritmo, em 3 semanas você chega a ~110kg no agachamento"
- Condicional: "Se mantiver PSE abaixo de 8"
- Visual simples — linha de projeção pontilhada no gráfico de progressão

---

### Nota sobre perfil do usuário avançado

O usuário avançado de força/hipertrofia:
- **Valoriza:** dados granulares reais, 1RM, volume por grupo muscular, deload antecipado, comparação inter-mesociclo
- **Não precisa de:** mensagens motivacionais da IA, análise de recuperação/sono (já gerencia empiricamente), visual elaborado se os dados forem corretos
- **Diferencial do Momentum para esse perfil:** dimensionalização Neural/Mecânica/Metabólica e Momentum como tendência relativa ao próprio histórico — conceitos que ele entende e que outros apps não entregam


---

## Decisão Arquitetural — Remoção do Score Momentum Único

**Data:** Mar 2026 · **Status:** FECHADO

### O que foi decidido

O score `Momentum` como número único (0–10) foi **removido** da interface do aluno.

**Razão fisiológica:** Um número único não consegue representar com integridade periodizações diferentes. Para alunos em progressão linear, o número sobe suavemente. Para alunos em DUP, ondulatória ou especialização (como a Julia Duzzi com A/B/C/D/E assimétrico), o ratio IC÷PSE oscila por design — não por regressão real. Qualquer normalização que funcione para um caso distorce o outro.

O que faz sentido fisiológico é apresentar os **componentes individualmente** — cada um com seu próprio histórico e direção.

### O que substitui

**No hero card — lógica editorial:**

O sistema escolhe qual dimensão exibir com base em relevância situacional:

```
1. Se alguma dimensão em queda/sobrecarga → mostra essa (sinal de atenção)
2. Senão, se dimensão dominante do ciclo em alta → mostra essa (confirmação)
3. Senão → mostra a dimensão com maior percentil recente (positivo)
```

O número exibido não é um score 0–10 arbitrário — é o **percentil interno** da dimensão, expresso em linguagem humana:

> *Mecânica · top 80% do seu histórico*  
> *Neural ↑ +18% nas últimas 4 sessões*

**No gráfico de trajetória:**

Três linhas finas sobrepostas — Neural, Mecânica, Metabólica — cada uma como percentil rolante do próprio histórico do aluno. O aluno lê visualmente qual curva está subindo e qual não.

Isso é comparável entre qualquer periodização porque cada dimensão é normalizada pelo histórico interno daquela dimensão — não pelo IC total absoluto.

**No modal (ao clicar no hero):**

Mantém as bolinhas do mesociclo. Remove número de Momentum. Adiciona tendência dimensional com linguagem direta.

### O que NÃO muda

- Os scores individuais Neural, Mecânica, Metabólica, Técnica e Ritmo permanecem
- O campo `momentum` permanece no banco por compatibilidade — apenas não é mais exibido com destaque
- O cálculo de `ritmo_estado` permanece (alta/estavel/baixo/sobrecarga)
- O PSE como moderador do sinal dimensional está documentado para v2

### Pendência registrada — IC Semanal Agregado

Para o gráfico de trajetória fazer sentido como linha única suave, o ideal é plotar **IC semanal acumulado** (soma das sessões da semana) em vez de IC por sessão. Isso elimina a oscilação estrutural de protocolos assimétricos sem precisar de normalização dimensional.

- Soma semanal é mais intuitiva para o aluno ("sua semana gerou 42.000 de IC")
- Comparável entre semanas com frequências diferentes via média diária
- **Pendente para v2** — requer agregação temporal que hoje não existe no schema de sessions

---

## Decisão Arquitetural — Insight Engine (Slot do Hero)

**Data:** Mai 2026 · **Status:** FECHADO

### O que foi decidido

O destaque visual do hero card no app do aluno é um **slot elástico** alimentado por um motor de seleção chamado **Insight Engine**. Em vez de exibir uma métrica fixa (percentil, IC, score), o engine mantém uma biblioteca de **fatos celebráveis** — cada um com critérios fisiológicos próprios — e seleciona semanalmente o fato mais relevante para o momento do aluno.

### Princípio fundamental

Progressões reais não são lineares. O mesmo número significa coisas diferentes em fases diferentes do mesociclo:

- Volume Load caindo em deload é **resultado planejado**, não regressão
- PSE alto em intensificação é **esperado**, não fadiga descontrolada
- Percentil mecânico baixo em semana técnica é **correto por design**

Portanto, o destaque do hero também precisa mudar conforme o contexto. Uma métrica fixa universal sempre vai mentir para alguma fase ou perfil de aluno.

### O que o Insight Engine resolve

1. **Tradução técnica → linguagem natural sem perder auditabilidade**
   Cada fato tem critérios numéricos fisiologicamente fundamentados (inputs auditáveis pelo PT) e uma headline em linguagem direta (consumível pelo aluno). O PT pode questionar "por que destacou isso essa semana?" e ver exatamente quais inputs ativaram aquele fato.

2. **Padronização da expectativa por periodização**
   Aluno em DUP, ondulatória, linear ou bloco vê fatos diferentes destacados porque o engine entende o que é esperado de cada periodização. O aluno linear celebra progressão de carga; o aluno em DUP celebra aderência ao plano ondulatório; o aluno em deload celebra recuperação ativa.

3. **Eliminação do "número fora de contexto"**
   Antes: "24" sem âncora semântica era lido como nota baixa. Agora: cada número exibido tem um fato declarado que o sustenta ("Acúmulo neural sustentado · percentil 65 há 3 semanas").

### Classificação dos fatos (uso interno)

| Categoria | Definição | Esperado |
|-----------|-----------|----------|
| **Comum** | Aplicável em qualquer fase, qualquer perfil | Garante presença mínima do slot |
| **Contextual** | Depende da fase do mesociclo ou tipo de sessão | Aparece quando a fase permite |
| **Raro** | Critério fisiológico estrito; quando aparece, é marco | Aceitar raridade — não calibrar para frequência |
| **Perfil** | Só faz sentido para certos perfis/periodizações | Pode nunca disparar para alguns alunos |

A raridade entra no **score composto de seleção** — fatos raros têm bônus de prioridade quando disparam, justamente porque carregam mais sinal.

### Fallback e ausência de positivo

Se nenhum fato celebrável dispara na semana:

Há sinal de atenção ativo (ritmo_estado em baixo/sobrecarga)?
→ SIM: hero entra em estado de alerta (frase + cor de atenção)
→ NÃO: hero exibe estado neutro contextualizado pela fase
(ex: "Semana de consolidação técnica — execução em foco")


A ausência de positivo nunca vira vazio. Ou é alerta acionável, ou é narrativa neutra de fase.

### Anti-repetição contextual

Um fato que foi headline nas últimas 2 semanas perde prioridade na seleção da semana atual — mesmo que ainda esteja ativo. Isso evita banalização: ver "streak de 7 dias" três semanas seguidas vira ruído. O fato continua visível em chips secundários, mas a headline rotaciona para outro fato disponível.

Fatos raros são exceção: se um fato raro dispara, ele ganha headline mesmo em janela de anti-repetição (raridade vence recency).

### Auditabilidade — o diferencial

O Insight Engine é a tradução prática do princípio estratégico do Momentum: "tecnicidade real, mastigada". A camada exibida ao aluno é narrativa; a camada subjacente — critérios numéricos, inputs, janelas temporais — é totalmente auditável pelo PT na Tela de Prescrição.

### O que NÃO muda

- Gráfico de trajetória dimensional (três linhas) permanece
- Chips automáticos de sessão (RN 26) permanecem
- ritmo_estado permanece como sinal independente
- Modal do hero continua exibindo as bolinhas do mesociclo

### Onde está especificado

- **Regras de Negócio §6** — definição dos 10 fatos + sinais de atenção + score
- **Modelo Matemático §6** — fórmulas de score composto e critérios numéricos

---

## Decisão Arquitetural — Momentum Dimensional (v2)

**Data:** Mar 2026 · **Status:** DOCUMENTADO PARA V2

### Proposta

Substituir `ratio_adaptacao` (IC÷PSE por sessão) por **percentil dimensional rolante**:

Para cada aluno, a cada nova sessão, calcula-se a janela de tendência de cada dimensão (últimas 4 vs 4 anteriores) e posiciona esse trend no percentil histórico daquela dimensão do próprio aluno.

```
trend_N   = (avg_N_recente - avg_N_anterior) / avg_N_anterior
percentil_N = posição desse trend no histórico de trends_N do aluno

Momentum_dim = percentil_N × wN + percentil_M × wM + percentil_Met × wMet
               × PSE_moderador
```

O PSE entra como **moderador multiplicativo** (0.75–1.15):
- PSE piorando com carga subindo → sinal amortecido
- PSE caindo com carga subindo → sinal amplificado

### Por que isso funciona para periodizações diferentes

Para progressão linear: as três dimensões sobem juntas de forma suave → percentis estáveis acima de 0.5 → Momentum consistente.

Para DUP/ondulatória: cada dimensão é comparada com ela mesma, não com IC total. O Treino A da Julia (IC 15.000) não contamina a leitura do Treino B (IC 4.000) porque Neural do Treino A é comparado com Neural de todos os Treinos A anteriores.

### Pesos sugeridos (a calibrar com mais dados)

| Dimensão | Peso sugerido | Razão |
|----------|--------------|-------|
| Neural   | 0.30 | Alta variância, dependente do exercício |
| Mecânica | 0.45 | Mais estável, diretamente ligada a hipertrofia/força |
| Metabólica | 0.15 | Menor relevância para protocolos de força/hipertrofia |
| PSE (moderador) | × 0.75–1.15 | Não é dimensão — é qualidade do sinal |

### Validação nos dados atuais

| Aluno | Atual | v3 | Ritmo atual | Ritmo v3 | Observação |
|-------|-------|----|-------------|----------|------------|
| julia_duzzi | 7.08 | 6.37 | alta | alta | Sem oscilação — correto |
| lara_soares | 7.81 | 6.20 | alta | alta | Progressão real confirmada |
| iarima_nunes | 7.11 | 0.75 | alta | baixo | Fadiga real detectada corretamente |
| mariana_costa | 7.21 | 2.57 | estavel | baixo | Overreaching confirmado |
| roberto_silva | 6.88 | 3.02 | baixo | estavel | Reab conservadora — correto |


---

## Prescrição — Estrutura e Progressão (Abr 2026)

### tipo_serie — Campo novo em `sessions.exercicios[]` e `prescricoes`

**Status:** implementado como campo de linguagem (v1). Diferenciação de IC por tipo_serie documentada para v2.

**Valores válidos para v1:**

| tipo_serie | Frase exibida ao aluno | Contexto fisiológico |
|---|---|---|
| `forca_pura` | "Foco na carga — execute com máxima intenção" | Força máxima, 1–5 reps, PSE alvo como critério principal |
| `forca_explosiva` | "Intenção máxima na fase concêntrica — velocidade é a carga" | Potência, pliométrico, olímpicos |
| `hipertrofia` | "Complete todas as reps com controle" | 6–15 reps, carga + reps alvo |
| `volume` | "A fadiga no final é o objetivo" | Muitas reps, descanso curto, acúmulo metabólico |
| `tecnica` | "Carga leve — qualidade acima de tudo" | Aprendizado motor, amplitude, reabilitação |
| `amrap` | "Máximo de reps com boa técnica" | Reps abertas, carga fixa |
| `emom` | "Respeite o intervalo — ritmo constante" | Intervalo fixo define FD diretamente |
| `densidade` | "Descanso curto intencional" | Mesma carga/reps, descanso reduzido |
| `isometrico` | "Sustente a posição pelo tempo prescrito" | TUT = tempo_s, reps = 1 |
| `excentrico` | "Controle total na descida — a fase negativa é o trabalho" | Excêntrico acentuado, nórdico, tempo na descida |
| `pausa` | "Pause na posição de maior tensão — sem usar o elástico" | Supino com pausa, agachamento com pausa |

**Para v2 (não implementar agora):**
- `rest_pause` — mini-séries com pausa curta intra-série
- `drop_set` — redução de carga sem pausa
- `oclusão` — requer equipamento específico
- `supersérie` / `bi-set` / `tri-set` — estrutura de múltiplos exercícios, não de série única

**Como o sistema lê em v1:** puramente como texto de intenção exibido ao aluno na tela de execução. Não altera cálculo de IC.

**Como o sistema lerá em v2:** cada tipo_serie define qual coeficiente domina o cálculo:
- `forca_pura` / `forca_explosiva` → Neural domina; chip `colapso_de_reps` desativado
- `volume` → Metabólica domina; chip `colapso_de_reps` altamente relevante
- `tecnica` → IC intencionalmente baixo, não sinalizar como problema; PSE baixo esperado
- `amrap` → ic_planejado estimado com média histórica de reps; comparação planejado vs executado especialmente valiosa

---

### Prescrição — Combinações de alvo por tipo_serie

Nem todo exercício terá carga + reps alvo simultaneamente. A estrutura `alvo` é flexível por tipo_serie:

| Contexto | O que é prescrito | O que fica livre |
|---|---|---|
| `forca_pura` | carga_kg + pse_alvo | reps (aluno executa até não conseguir com boa técnica) |
| `hipertrofia` | carga_kg + reps_alvo + pse_alvo | — |
| `volume` | reps_alvo + pse_alvo | carga (aluno escolhe o que permite completar) |
| `tecnica` | carga_kg fixa baixa + reps_alvo | pse (irrelevante) |
| `amrap` | carga_kg + tempo_s | reps (máximo possível) |
| `emom` | carga_kg + reps_alvo + intervalo_s | — |
| `densidade` | carga_kg + reps_alvo + descanso_s | — |
| `isometrico` | carga_kg + tempo_s | — |
| `excentrico` | carga_kg + reps_alvo + tut_descida_s | — |
| `pausa` | carga_kg + reps_alvo + pausa_s | — |

**Estrutura do objeto `alvo` no banco:**
```json
{
  "nome": "Agachamento Livre",
  "tipo_serie": "forca_pura",
  "series": 5,
  "progressao": "carga",
  "alvo": {
    "carga_kg": 100,
    "reps": null,
    "pse": 8.5,
    "descanso_s": 180,
    "tut_s": null,
    "tempo_s": null,
    "pausa_s": null,
    "intervalo_s": null
  }
}
```

---

### Prescrição — Tipos de progressão (v1)

| Tipo | O que é | V1 |
|---|---|---|
| `carga` | Aumenta kg mantendo reps | ✅ |
| `volume` | Aumenta reps mantendo kg | ✅ |
| `densidade` | Reduz descanso_s mantendo carga+reps | ✅ |
| `pse` | Mantém carga+reps, alvo é PSE ≤ threshold | ✅ |
| `tecnica` | Carga estável, foco em amplitude e controle | ✅ |
| `dupla` | Sobe reps até teto, depois sobe carga e reseta reps | ✅ requer `reps_teto` por exercício |
| `ondulante` | Alterna carga alta/baixa entre sessões | ✅ lógica no engine |
| `tut` | Aumenta tempo sob tensão via cadência | ⚠️ depende campo cadência (FTT) — v2 |
| `cluster` | Pausa intra-série para mais volume | ⚠️ requer schema de série mais rico — v2 |
| `1rm_percentual` | Prescreve % do 1RM estimado | ⚠️ requer 1RM no banco — v2 |

---

### Prescrição — Estrutura da coleção `prescricoes` no Firestore

```
prescricoes/{student_id}
  ├── student_id: string
  ├── mesociclo: string
  ├── atualizado_em: timestamp
  ├── progressao_mae: {
  │     modelo: 'linear' | 'bloco' | 'dup'
  │     logica_volume: 'carga_primeiro' | 'reps_primeiro'
  │   }
  └── sessoes: {
        "[tipo]": {
          ic_planejado: number,
          dim_dominante: string,
          notas_pt: string,
          exercicios: [{
            nome: string,
            tipo_serie: string,
            series: number,
            progressao: 'herda_mae' | 'carga' | 'volume' | 'densidade' | 'pse' | 'tecnica' | 'dupla' | 'ondulante' | 'estavel',
            alvo: {
              carga_kg: number | null,
              reps: number | null,
              pse: number | null,
              descanso_s: number,
              tut_s: number | null,
              tempo_s: number | null,
              pausa_s: number | null,
              intervalo_s: number | null
            }
          }]
        }
      }
```

**Nota:** `incremento_kg` por exercício foi removido da estrutura. A progressão de carga é calculada pelo engine com base no histórico real — não é um campo fixo. O PT define o *tipo* de progressão, não o delta específico.

**Regras especiais por perfil** (hoje hardcoded no prompt do Claude Code — migrar para campos configuráveis na Tela de Prescrição do PT na v2):
- `iarima_nunes`: exercícios com CT ≥ 7 → `progressao: 'estavel'`
- `roberto_silva`: todos os exercícios → `progressao: 'volume'` (reps antes de carga)
- `mariana_costa`: progressão calculada separadamente por tipo de sessão (Força vs Volume vs Hipertrofia)

