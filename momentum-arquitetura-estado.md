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
| **`exercise_id` como campo autoritativo** (D3.2, set/2026) | `nome` é gravado na sessão como snapshot de exibição, nunca como chave. `EX_NAME_MAP` e lookup por nome estão descontinuados no caminho de escrita. |
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

### Decisões pré-lançamento Jacqueline (jun/2026)

Decisões tomadas para viabilizar o lançamento do app para a primeira aluna real (Jacqueline), enquanto a calibração do modelo segue em desenvolvimento. **Não são decisões definitivas do produto — são decisões da v1 da home.**

**1. Barras dimensionais (N/M/Met) ocultadas da home v1.**
Razão: os scores atuais da Jacqueline retornam valores uniformes (8.67 em todas as dimensões), o que é artefato dos dados sintéticos atuais, não reflexo do modelo. Exibir três barras idênticas comunicaria "o sistema não diferencia" — o oposto do diferencial Momentum.
Reativação: após re-simulação com scores derivados sessão a sessão do modelo matemático (`momentum-modelo-matematico.md`), com dispersão real entre dimensões.

**2. Score Técnica removido da home v1.**
Razão: discrepância evidente (Técnica=3.07 vs N=M=Met=8.67) sem explicação fisiológica consistente. A questão de fundo — se Técnica deveria ser score derivado, flag binária do PT, ou exclusivo da fase estúdio com supervisão — não está resolvida. Lançar com o score atual seria comunicar uma medição que não está validada.
Resolução pendente: ver Pendências Críticas.

**3. Layer A determinística é mandatória na home v1.**
Razão: checkins da Jacqueline retornam `prontidao`, `cansaco` e `motivacao` null em todos os 11 registros — Layer B/IA não tem como funcionar sem esses dados. Layer A construída a partir de variáveis observáveis no banco (ritmo_estado, PSE médio recente, semana do meso, aderência) é a única narrativa confiável agora.
Conteúdo da Layer A v1: hardcoded para o estado atual da Jacqueline; motor de regras Layer A genérico fica para v1.1.

**4. Re-simulação dos dados da Jacqueline antes do lançamento.**
Razão: os scores uniformes e o Técnica discrepante indicam que a simulação atual foi feita sem derivar os scores do modelo matemático. Re-simular significa: gerar/importar sessões coerentes e calcular N/M/Met/Ritmo sessão a sessão usando as fórmulas documentadas, não atribuir valores agregados sintéticos.
Inclui: popular checkins esparsos (1–2 por semana) com valores coerentes para que a tela de check-in tenha histórico de exemplo quando ela explorar, mesmo que a home v1 não dependa desses dados.

---

### Decisões v1 client-side (set/2026)

Reconstruída a partir dos handoffs originais da revisão, versionados como registro histórico
em `docs/decisoes/momentum-decisoes-v1-bloco1.md`, `-bloco2.md` e `-bloco3.md`. Aqueles
arquivos guardam o *porquê*; **este é o documento vivo** — status, supersessões e decisões
novas entram aqui. **As 17 decisões são fechadas**; reproposta exige justificativa fisiológica
ou de produto explícita.

Coluna **Status**: `implementada` cita o commit; `pendente` não tem código. Onde a
implementação divergiu do handoff, a divergência está registrada logo abaixo da tabela —
o handoff é a fonte da razão, não do estado atual.

#### Bloco 1 · Entrada no app, identidade, âncora temporal

| # | Decisão | Razão | Status |
|---|---|---|---|
| **D1.1** | Sem autenticação na v1 — `STUDENT_ID` vem de query param. Comportamento declarado, não acidental. | A v1 roda com uma aluna, em fase de teste. Consequências aceitas: quem tiver a URL e um `id` válido lê o dashboard de qualquer aluno; se as Security Rules estiverem abertas, o banco é legível por quem tiver a config do Firebase — que está no cliente por definição. | decidida — nenhuma ação (decisão de não fazer) |
| **D1.2** | **`date` é o campo canônico da data da sessão, formato ISO `YYYY-MM-DD`.** Formatação pt-BR é responsabilidade exclusiva da camada de exibição. | Comparação de data é lexicográfica em todo o app. Misturar pt-BR com ISO faz `"01/09/2026" >= "2026-09-01"` retornar `false`, filtrando a sessão para fora da aderência. Ver correção de escopo abaixo. | **implementada** (`f8d4de7`) |
| **D1.3** | `S.sessions` passa a ser ordenado **crescente** (mais antigo primeiro), para que `slice(-n)` signifique literalmente "últimas n". | O hero usava `slice(-4)` sobre array decrescente: o percentil "recente" lia as 4 **mais antigas** e o sinal da tendência vinha **invertido** — aluna progredindo aparecia como queda. Três convenções coexistiam no mesmo arquivo. | **implementada** (`f8d4de7`) |
| **D1.4** | Cálculo dimensional (`ic_neural`/`ic_mecanica`/`ic_metabolica`) em Cloud Function disparada por escrita em `sessions`. | Mantém os coeficientes CT/IM/DN/SV/FC — propriedade do Momentum — fora do cliente, e a home atualiza sozinha via o `onSnapshot` já existente. Sem ela, a sessão recém-executada é invisível para percentis e tendências: a aluna treina e a home não muda. | **Fase 1 implementada** — ver correção de premissa abaixo. Fase 2 desligada deliberadamente |
| **D1.5** | Zero-state dedicado: a camada de intenção do hero renderiza normal; a camada de sinal é **substituída**, não atenuada. Hero didático sobre a periodização prescrita. | Com <4 sessões, `dimEstado(0.5, 0)` devolve `'estavel'` nas três dimensões e o hero exibe um número no meio da escala **sem dado de origem** — violação direta do pilar de auditabilidade. O zero-state antecipa o desenho do ciclo em vez de relatar passado inexistente. Threshold: a camada de sinal não aparece até **4 sessões com dado dimensional válido**. | pendente |
| **D1.6** | Fim de mesociclo: estado mínimo na home (*"mesociclo encerrado — aguardando novo ciclo"*). RN18 (tela de transição com resumo) vai para v1.1. | Hoje `semanaAtual` é clampado e a home congela em "semana N de N" indefinidamente. A aluna continua podendo treinar; as sessões param de contar para a aderência do ciclo encerrado. RN18 depende de evolução de CargaObjetiva, que depende de D1.4 rodando e estabilizado. | pendente |
| **D1.7** | Campo `frequencia_semanal` (número) em `prescricoes`, escrito pelo PT. Aderência vira `sessões da semana ÷ frequencia_semanal`, independente de qual dia. | Desacopla do calendário — a aluna não é penalizada por treinar terça em vez de segunda. Elimina o parse frágil de texto livre de `anamnese.disponibilidade` e seu default silencioso `[1,3,5]`. Move o denominador de um campo de **preferência declarada pela aluna** para um de **prescrição do PT** — auditável, com autor. | pendente |

**D1.7 — fora de escopo decidido.** `dias_treino[]` (array explícito de dias) **não** entra
agora. É pré-requisito de **RN14 (lembrete de treino)**, que depende de o sistema saber que
hoje é dia dela. Se RN14 entrar no lançamento, esta decisão reabre e `frequencia_semanal`
vira derivado (`dias_treino.length`).

**Princípio derivado (aplica-se além de D1.2).**
> Toda duplicidade de campo legado/atual descoberta é **migrada no momento da descoberta**,
> não acumulada. Vale para os pares já documentados: `indice_carga`/`ic_executado`,
> `updated_at`/`atualizado_em`, `date`/`data`.

**Nota de método (D1.3).** Este erro não seria detectado por simulação de cenário — projetar
o hero "com a lógica real" reproduz a inversão junto. Auditoria de código e simulação macro
são complementares, não substitutas.

##### Correção de escopo em D1.2 — a premissa do handoff foi desmentida pelo banco

O handoff descrevia D1.2 como *"`data` é o campo canônico, migrar sessões legadas de pt-BR
para ISO"*. O diagnóstico de banco (set/2026) mostrou o contrário:

- As **355 sessões usam o campo `date`, todas já em ISO**.
- O campo **`data` não existe em nenhum documento** de `sessions` — foi introduzido pelo C1.
- A migração de sessões legadas converteria **zero documentos** e foi **cancelada por
  desnecessária**.

A decisão de formato permanece válida: era um bug **prospectivo**, que quebraria na primeira
sessão gravada pelo app, não nas existentes. O canônico é **`date`**, não `data`.

Dois efeitos colaterais achados na implementação, não previstos no handoff:

- `buildICChart()` rotulava as barras com `.slice(0,5)` da data — formato pt-BR. Com ISO
  viraria `"2026-"`. Passou a usar formatador pt-BR explícito.
- `toISOString()` converte para UTC: em UTC-3, treino após as 21h ia para o dia seguinte no
  campo `date`, divergindo do doc id (que usa componentes locais). Padronizado em
  `toISODate()` com componentes locais.

##### D1.4 — a premissa estava errada: a função já existia

**A decisão foi tomada, priorizada e registrada assumindo que a função não existia. Ela
existia — implantada e ACTIVE.** `onSessionWrite`, gcfv1, trigger `document.write` em
`sessions/{sessionId}`, nodejs22, us-central1, já fazendo as cinco responsabilidades que o
handoff atribuía a uma função a ser escrita.

**Causa do erro:** `functions/` estava **fora do controle de versão** — o repositório é
`files/`, e `functions/` era irmão dele na raiz do projeto. Não aparecia em nenhum `git log`,
`git ls-files` ou diff; qualquer inspeção via git concluía que o backend não existia.

Vale registrar o que **não** foi a causa: o `CLAUDE.md` documentava a pasta corretamente, na
árvore de estrutura e na seção Stack (`firebase-functions ^4.9, Node 22`). A informação estava
escrita e disponível — a revisão simplesmente não a consultou, e a afirmação do handoff de que
esta seria a *"primeira dependência de backend do projeto"* já era contraditada pelo próprio
`CLAUDE.md` no momento em que foi escrita. Não é caso de documentação faltante, é caso de
decisão tomada sem verificar o estado do sistema — a regra de ouro nº 1 do projeto.

Corrigido: `functions/` e `firebase.json` foram movidos para dentro de `files/` e versionados
(`0dffc95`), e a árvore do `CLAUDE.md` foi atualizada para a nova localização. Consequência
operacional: `firebase deploy --only functions` passa a ser rodado de `files/`.

**O que a Fase 1 corrigiu (set/2026).** A função lia `ex.s`, `ex.r`, `ex.kg` e `ex.descanso_s`
do topo do exercício — campos que o payload aninhado do C1 não tem. `kg` caía no default `0`,
zerando `CargaNorm`, que multiplica as três dimensões: **todo IC ia a zero**, gravado por cima
do documento correto, por trigger automático, sem erro para a aluna nem aviso para o PT. A
correção lê `series[]`, resolve por `exercise_id` (D3.2), implementa a Metabólica de §2c
completa (com SV, que estava fora sem menção no código), elimina o fallback de coeficientes
genéricos e corrige o guard de loop, que fazia o corpo da função rodar duas vezes por sessão.

**A Fase 2 continua desligada — agora por decisão, não por acidente.** `recalcStudentScores`
lançava `FAILED_PRECONDITION` por índice composto ausente, fora de try/catch, matando a função
antes da escrita no doc do aluno. Era isso, e só isso, que impedia quatro sessões zeradas de
gravarem `scores: 10/10/10` no perfil. Dois defeitos se cancelando não é salvaguarda: a
chamada passou a ser guardada por `FASE_2_ATIVA = false`.

1. **A infraestrutura de backend já existe — e a função também.** `firebase.json` com runtime nodejs22,
   `functions/functions_index.js`, `firebase-functions ^4.9`, `DEPLOY-TUTORIAL.md`. **O
   handoff afirma que esta seria a "primeira dependência de backend do projeto" — está
   incorreto.** É uma função nova num projeto que já deploya.
2. **A resolução de exercício é por `exercise_id`, não por `nome`.** O handoff do Bloco 1
   manda resolver via `nome` normalizado porque "`exercise_id` legado é não-confiável" —
   **regra superseded por D3.2**, decidida depois. A função resolve por `exercise_id`.
3. **Partida em duas fases.**
   - *Fase 1 (pré-lançamento):* resolve `exercise_id` contra `exercises`, aplica o modelo e
     grava `ic_neural`/`ic_mecanica`/`ic_metabolica` na sessão. Autocontida, não precisa de
     histórico.
   - *Fase 2 (posterior):* recalcula `scores.*` e `ritmo_estado` no doc do aluno (RN20/RN21b,
     adapter por `modelo_periodizacao`). Só passa a importar na **4ª sessão**, quando a
     camada de sinal do hero destrava (D1.5).
4. **Não gravar intermediários** (`CargaNorm`, amplificador, FD, FTT) nem os coeficientes do
   exercício. As sessões guardam os inputs de execução e `exercise_id`, então recalibração é
   reprocessamento via script (padrão de `fix_ic.js`), não releitura de campo.
   **Condição declarada:** `exercises` só muda por correção, **nunca por substituição de
   slug** — se slugs forem reorganizados no futuro, o recálculo perde a âncora.
5. **Riscos a tratar na implementação** (do handoff, ainda válidos): janela de inconsistência
   entre a escrita da sessão e a da função — a home deve tolerar sessão sem `ic_*` por alguns
   segundos sem renderizar estado falso; exercício que não resolve precisa de comportamento
   explícito (log + sessão marcada, **nunca IC parcial silencioso**).

**Ordem declarada:** D1.2 antes de D1.4 — a função precisa nascer lendo e escrevendo ISO, ou
cria uma terceira geração de dado. Leitura de `prescricoes` antes de D1.5 e D1.7.

#### Bloco 2 · Check-in e prontidão

A modulação de prontidão **já estava implementada e rodando**. A decisão central do bloco é
**desligá-la**, mantendo toda a captura. Adiar sem desligar não seria adiamento — seria
lançar o comportamento atual.

| # | Decisão | Razão | Status |
|---|---|---|---|
| **D2.1** | Modulação de prontidão **desligada** na v1. Captura mantida integralmente. | **Calibração, não UX.** Os multiplicadores (0.90/0.75/0.60) são defaults não calibrados, mesma classe dos `wN/wM/wMet`. Aplicar um modulador não calibrado durante a calibração do modelo torna impossível separar variação vinda do **estado real da aluna** de variação **injetada pelo sistema** ao encolher a prescrição. Desligada, o primeiro mesociclo produz o corpus limpo — prontidão declarada × execução real, sem intervenção — e o `fatorProntidao` da v2 nasce de dado. | **implementada** (`b1eb8fd` + `a366840`) |
| **D2.2** | Pular o check-in grava `estado_prontidao: null`, não `5`. | Prontidão 5 acionava a faixa "Sessão adaptada" (volume 0.75): **"não quero responder" era lido como "dia moderado"** e ela recebia um treino 25% menor sem ter declarado nada. Com D2.1 isso não altera mais o treino, mas altera o corpus — um `5` que ninguém declarou polui exatamente o dataset que vai calibrar a modulação da v2. `null` é honesto e filtrável. | **implementada** (`a366840`) |
| **D2.3** | Listener `onSnapshot` em `checkins` + **ID determinístico** `checkins/{student_id}_{data_iso}` com `.set()`, nunca `.add()`. | Não existia query nem listener em `checkins`: `S.checkinHoje` só vivia na sessão de navegador. Recarregar a página zerava o estado, o atalho `jaFez` voltava a `false` e um **segundo documento** era criado para o mesmo dia. ID determinístico torna a duplicata impossível **por construção, não por checagem**. | **implementada** (`a366840`) — migração dos docs antigos pendente |

**O que SAIU da v1 com D2.1:** aplicação de `f.volume` sobre as reps; bloco *"Treino
ajustado: X% do volume · Y% da carga"* da tela de resultado; a parte do banner de execução que
afirmava ajuste; **qualquer copy que afirme ajuste** — não haverá ajuste, o texto não pode
dizer que há; `ex.s_original` / `ex.r_original` / `ex.ajustado`, que perdem função.

**O que PERMANECE:** captura dos quatro campos (disposição, cansaço, sono, alimentação);
`calcEstadoProntidao()` e a exibição do número para a aluna — ela vê seu próprio estado;
gravação em `checkins`; `estado_prontidao_entrada` e `checkin_id` na sessão;
`buildCheckinCorrelacao()` na Evolução, que passa a ter dado não-contaminado.

**Precondição para D2.1 voltar (v2) — as três, não duas:**
1. Corpus de **≥1 mesociclo completo** com prontidão declarada e execução não-modulada.
2. Multiplicadores **derivados desse corpus**, não default.
3. **V2-C resolvida** — o fator aplicado precisa ser gravado na sessão.

**Correção acoplada (D2.2) — dois caminhos de entrada.** `startTreino()` e
`iniciarTreinoComCheckin()` eram ambos alcançáveis e produziam sessões diferentes a partir do
mesmo estado. Dois entry points divergentes são a origem de sessões inexplicáveis no
histórico. **Consolidados em um único caminho no C1** (`5a31bc9`).

##### Movido para v2 — contexto preservado

Levantadas, discutidas e **deliberadamente adiadas**. Registradas para não serem
redescobertas do zero.

**V2-A · O que a prontidão modula: reps, séries ou carga?**
Volume estava sendo cortado em **reps**, não em séries — escolha implícita, nunca decidida.
Reduzir reps mantendo carga preserva intensidade e corta volume; cortar séries corta volume
preservando a qualidade das primeiras execuções. Efeitos distintos sobre densidade e sobre o
componente Metabólico (`FD = 90/descanso`; número de séries entra em `CargaNorm` direto).
Alternativas registradas:
- Só volume, e volume = séries — preserva a zona de estímulo prescrita: *4 reps a 85% ainda é
  força; 4 reps a 76% não é nada*.
- Volume em reps + carga como sugestão visível e editável no widget.
- **Modulação dependente de `tipo_serie`** — em `forca_pura`/`forca_max` a carga é intocável e
  o corte é em séries; em `hipertrofia`/`volume`, corte em reps; em `tecnica`, nenhum ajuste
  (o objetivo já é qualidade sobre carga).

A terceira é a **fisiologicamente correta** e depende de `tipo_serie` estar disponível no
cliente — ou seja, de `prescricoes` ser lido (Bloco 3, já feito).

**V2-B · Estado de "repouso recomendado"**
Prontidão <2 retornava `volume: 0.00`, que passava por `Math.max(1, Math.round(ex.r * 0))` e
virava **1 repetição por série** — um treino completo de singles. O texto dizia "considere
descansar", o botão dizia "Iniciar treino →" e a tela de execução abria normalmente. Com D2.1
a faixa deixa de ter efeito mecânico. Fica em aberto: se o Momentum quer ter uma opinião sobre
**não treinar**, o estado precisa ser terminal (recomendação + saída explícita "treinar mesmo
assim", registrada) ou virar sessão de recuperação real. E, se existir, **um dia de descanso
recomendado pelo sistema não pode contar como falta na aderência** — conecta com D1.7 e RN02.

**V2-C · O ajuste precisa ser gravado (pré-requisito da reativação)**
`finishTreino()` grava `estado_prontidao_entrada` e `checkin_id`, mas **não o fator aplicado**
nem os valores originais. Enquanto nada compara executado contra prescrito, isso não dói.
Assim que `prescricoes` for lido, tudo que depende da comparação lê errado: aderência, RN26
`colapso_de_reps` (`r < r_alvo × 0.75`), RN26 `progressão_ok` (`r ≥ r_alvo`), RN13. Um
mesociclo de dias de prontidão média produziria uma aluna que *"nunca bate o alvo"*.
Estrutura registrada como preferida: `prescricoes` mantém o alvo prescrito intocado; a sessão
grava `alvo_dia` (ajustado) por série **e** `ajuste_prontidao: {volume, carga, aplicado_em}`.
Assim a cadeia fica auditável ponta a ponta — **prescrição → modulação → execução** — e a
pergunta *"por que ela fez 9 e não 10?"* é lida do banco, não reconstruída. É a mesma
estrutura que habilita a leitura mais interessante do check-in: correlação entre prontidão
declarada e desvio de execução. Se ela declara prontidão baixa e entrega volume cheio, o mal
calibrado é o `fatorProntidao`, não ela.

#### Bloco 3 · Origem do treino e identidade de exercício

Antes desta revisão, `momentum-aluno.html` tinha **zero** ocorrências de `prescricoes`,
`collection('exercises')`, `EX_NAME_MAP` e `tipo_serie`. Este bloco não melhorou a origem do
treino — **construiu o caminho de leitura que nunca existiu**. Consequência de prazo: a
leitura de `prescricoes` deixou de ser evolução e virou **pré-requisito de lançamento**.

| # | Decisão | Razão | Status |
|---|---|---|---|
| **D3.1** | `prescricoes` é a **origem única** do treino. `buildTreinoFromProfile()` e os cinco templates são removidos; `s.profile` perde o consumidor e é descontinuado. | Os templates eram **resíduo de mock** — treino de amostra criado de um PDF para testar a tela de execução, nunca decisão de produto. Mas escreviam no Firestore: *andaime que escreve no banco não é andaime*. A intenção de treino vive em `prescricoes`, `dim_dominante` e `modelo_periodizacao`. | **implementada** (`5a31bc9`) |
| **D3.2** | **`exercise_id` é o campo autoritativo** — supersede a regra de ouro anterior. `nome` continua gravado na sessão como **snapshot de exibição**, nunca como chave. | Validação por nome exige normalização e ainda é aproximada: `'Rosca Direta'` e `'Rosca direta '` colidem, mas `'Supino Reto'` e `'Supino reto c/ barra'` não — é comparação difusa fazendo papel de chave estrangeira. ID é binário: existe ou não. `nome` permanece para que a sessão antiga diga o que foi feito sem depender do join — auditabilidade não deve exigir que a coleção de referência esteja intacta. | **implementada** (`5a31bc9` + `2603d0b`) |
| **D3.3** | Granularidade de `exercises` = granularidade do modelo. **Um doc por variação.** Agrupamento vem do campo `pattern`, nunca do slug. | Supino com barra, halteres e máquina têm **CT, IM, DN, SV e FC diferentes**: máquina tem CT baixo (trajetória guiada) e estabilização quase nula; halteres têm CT e DN mais altos pela demanda de controle unilateral; barra fica no meio, com maior carga absoluta. Compartilhar um doc faz o modelo perder exatamente a distinção que existe para medir. **Slug identifica; `pattern` agrupa.** | **implementada** — `desenv_halt` cadastrado no backfill |
| **D3.4** | **A aluna escolhe a sessão do dia**, numa lista das chaves de `prescricoes.sessoes`. | Nada no sistema dizia qual era a sessão de hoje — `students.divisao` é string solta de label, desconectada da estrutura. Zero campo novo, zero inferência, zero risco de servir a sessão errada. | **implementada** (`5a31bc9`) |
| **D3.5** | O **`alvo` completo** viaja da prescrição para `sessions.exercicios[].alvo`, **mesmo o que a tela não exibe** — incluindo `tipo_serie` e `progressao`. | Os campos sem consumidor eram exatamente os que definem as dimensões que o Momentum mede: `tut_s`/`tempo_s` alimentam FTT na Metabólica; `descanso_s` alimenta FD (`90/descanso`); `pse` é o alvo contra o qual RN26 avalia `progressão_ok`; `tipo_serie` é o enum de intenção que a modulação da v2 vai precisar (V2-A). Custo quase zero — o dado já existe do outro lado. Não gravar é jogar fora informação já escrita. | **implementada** (`5a31bc9`) |
| **D3.6** | Chaves de `sessoes` separam **slug de label**: chave `"lower-a"`, campo `"label": "Lower A · PR Agachamento"`. `sessions.tipo` grava o **slug**. | Identidade estável não deve ser texto de exibição — mesma razão de D3.2. Antes, renomear quebrava a referência e casar `sessions.tipo` com a chave virava matching de string com sufixo. Feito junto com o backfill porque o documento já seria reescrito: **custo quase zero agora, alto depois**, quando houver sessões referenciando as chaves antigas. | **implementada** — backfill da prescrição da Jacqueline |
| **D3.7** | ID determinístico em `sessions`: `.set()` com `{student_id}_{data_iso}_{n}`, onde `n` desambigua duas sessões legítimas no mesmo dia. | `.add()` cria sessão duplicada silenciosamente em toque duplo ou reload no meio da escrita. **Duplicata em sessão é pior que em check-in** — polui aderência e o corpus dimensional. Impossibilidade por construção, não por checagem. | **implementada** (`5a31bc9`) |

**D3.5 — `pse_alvo` NÃO é exibido para a aluna na v1.** Efeito de **ancoragem**: se ela vê
"alvo PSE 8" antes de reportar, o PSE relatado deixa de ser independente — e `PSE_relatada` é
metade do blend de `PSE_ritmo`. Contaminaria o corpus na semana em que ele mais importa.
Reavaliar quando a calibração estiver estável.

**D3.1 — nota sobre o dano dos templates.** Três dos cinco nomes não eram exercícios, eram
categorias: `'Agachamento / Leg Press'` (dois movimentos com IM e DN distintos),
`'Puxada / Remada'`, `'Isolamento · Bíceps'` (não nomeia movimento). Nenhum resolve contra
`exercises`. Sessão gravada com esses nomes perdeu a informação de qual movimento foi feito —
**irrecuperável por reprocessamento**, diferente das lacunas dos Blocos 1 e 2.

**D3.2 — risco verificado e descartado.** Doc ids auto-gerados não sobreviveriam a re-seed com
`.add()`. **Não se aplica:** `import.js` usa `.doc(ex.id).set(ex)` com slug semântica. IDs já
determinísticos, sem migração necessária.

**D3.4 — alternativas descartadas para a v1:**
- *Rotação por histórico* — frágil (chaves com sufixo `· Deload` quebram o casamento) e sem
  âncora no estado zero.
- *`ordem` explícita com regra de avanço* — determinístico, mas exige regra que não lida bem
  com dia pulado. **Nota de set/2026:** o campo `ordem` existe em `prescricoes` e é usado
  **apenas para ordenar a lista de exibição**. Não há sugestão de próxima sessão, marcação de
  sessão sugerida nem avanço automático — isso é v1.1.

**Direção v2 (D3.4):** o app propõe segundo a periodização e ela pode divergir; a divergência
fica registrada como sinal. **Sessão livre** (montar treino escolhendo de `exercises`, RN06)
fica para v1.1.

##### Varredura · padrão de ID determinístico no sistema

| Coleção | Padrão | Status |
|---|---|---|
| `exercises` | `.doc(slug).set()` — slug semântica | ✅ já correto |
| `students` | `enrique`, `jacqueline` | ✅ já correto |
| `checkins` | `{student_id}_{data_iso}` | ✅ implementado (D2.3, `a366840`) |
| `sessions` | `{student_id}_{data_iso}_{n}` | ✅ implementado (D3.7, `5a31bc9`) |
| `prescricoes.sessoes{}` | slug como chave + campo `label` | ✅ implementado (D3.6, backfill) |
| `prescricoes` (doc) | `{student_id}` ou `{student_id}_{mesociclo}` | ⚠ **não verificado** |

---

## Pendências Críticas (bloqueadoras)

### ⚠ Score Técnica — validade do proxy
Sem observação direta (vídeo, presença, supervisão), Técnica só pode ser inferida por proxies frágeis (PSE vs carga vs reps prescritas vs executadas). Decisão pendente: Técnica deveria ser (a) score derivado com proxy melhor calibrado, (b) flag binária preenchida pelo PT, (c) exclusiva da fase estúdio com supervisão presencial, ou (d) removida do conjunto dimensional?
Bloqueia: reativação do score na home, comunicação do diferencial técnico em material de marketing, futuro PT-facing dashboard.

### ⚠ IM — recalibração nos exercícios isolados
Com FC fora de CargaNorm, exercícios isolados (Extensora, Flexora, Rosca, Adutora, Abdutora, etc.) terão Mecânica maior do que o calibrado originalmente. IM foi definido assumindo que FC já comprimia a CargaNorm. Revisão exercício a exercício necessária — **julgamento fisiológico do PT.**

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

### `sessions` esvaziada — escala única de Metabólica (set/2026)

As 355 sessões legadas foram **apagadas**. Decisão do PT: não manter duas escalas de
Metabólica convivendo. A função calculava `cn × FD`; §2c define `CargaNorm × FTT × SV × FD`,
e SV varia de 0,2 a 9 entre exercícios — a diferença é de escala, não de arredondamento.

**Por que apagar em vez de reprocessar.** `descanso_s` estava ausente em **100%** dos 1.594
exercícios legados, então reprocessar aplicaria `FD = 1` a todos: escala única, porém com a
Metabólica cega para densidade — metade do que o componente existe para medir. Somado a isso,
116 medições vinham do fallback de coeficientes genéricos e 176 exercícios tinham `series[]`
truncado. O corpus não servia para calibração.

**Backup:** `backups/sessions-2026-09-19.json` (355 docs, 1.594 exercícios, 1,5MB,
sha256 `3666a6c6af34f05227c0d13abf2c503f`), fora do repositório, com cópia redundante `.bak`.
A exclusão foi feita em lotes, após verificar que todo doc do banco constava do backup.

**Consequência:** a primeira sessão da Jacqueline passa a ser a primeira do corpus, na escala
§2c desde o início — que era o objetivo. Os scores de seed em `students` **não** foram
apagados e agora não têm sessões por trás: `scores.*` e `ritmo_estado` dos nove alunos são
valores sem origem até a Fase 2 de D1.4 entrar. Pendência aberta.

**Ressalva registrada:** as 21 sessões de `julia_duzzi` foram apagadas junto, apesar de
indícios de que ela é atleta real — ver abaixo. Estão no backup.

### `julia_duzzi` — sintética ou real? (contradição não resolvida)

Este documento afirma as duas coisas: *"Simulação Julia Duzzi (página de demo de atleta)"*
em Estado Atual do Projeto, e *"Atletas atuais no sistema: Julia Duzzi, Enrique"* em Contexto
do PT. O `CLAUDE.md` repete a segunda.

Indícios levantados em set/2026 de que o dado é **real**:

- É a **única** dos dez alunos **sem `email`** — os outros nove têm o padrão de seed
  `nome@email.com`.
- `anamnese.observacoes` traz observação de quem acompanhou a execução: *"Treino elaborado
  por PT externo. Protocolo baseado em máquinas com foco em isolamento de inferiores. PSE
  naturalmente alto (8.6–9.7) — padrão da aluna."*
- **A faixa de PSE da nota bate com o dado gravado** (9.1, 9.4, 9.6, 9.5, 8.6, 9.8).
- É citada como **evidência em duas decisões arquiteturais fechadas** — a remoção do Score
  Momentum único e o Momentum Dimensional usam o A/B/C/D/E assimétrico dela como caso.
- `scores` dispersos (6.19 / 6.67 / 6.67 / 3.84 / 7.14), sem o artefato de valores uniformes
  que marca os dados sintéticos.
- Nenhum script do projeto cria alunos; os dois que a mencionam são de correção retroativa.

**Não resolvido.** O PT optou por apagar mesmo assim. As 21 sessões estão no backup e podem
ser restauradas. Se ela for atleta real, este documento precisa parar de chamá-la de
simulação — foi essa contradição que quase levou à exclusão silenciosa de dado real.

### Mapa nome-legado → exercise_id

21 das 355 sessões têm ao menos um exercício resolvido pelo fallback genérico
`{CT:4, IM:5, DN:5, SV:3, FC:0.6}` — 116 medições. Nomes não resolvidos, por ocorrência:
Cadeira Abdutora em Pé (14), Coice Perna Flexionada (14), Agachamento Sumo Máquina (11),
Cadeira Abdutora (11), Cadeira Extensora (10), Cadeira Adutora (7), Remada Máquina Pronada (7),
Remada Baixa Triângulo (7), Elevação Lateral Halteres (7), Abdominal Máquina (7),
Búlgaro no Smith (7), Elevação Pélvica Máquina (7), Elevação Lateral Polia Média (4),
Hack Linear (3).
Ao menos um (`Cadeira Extensora`) existe no catálogo sob outro nome. Vários são isolados —
justamente os marcados como pendentes de recalibração de IM.

**Auditado em set/2026:** `exercise_id` está presente em **100%** dos 1.594 exercícios
legados, mas só **39,7% resolvem** contra `exercises` — os demais são slugs de nome geradas
por script (`leg_press_45`, `supino_reto`, `remada_máquina`). Onde `exercise_id` e nome
resolvem, **concordam em 633 de 633 casos, sem nenhuma discordância** — por isso a função
corrigida pode cair para o nome como caminho de compatibilidade sem introduzir ambiguidade.
A pendência é o mapa `exercise_id-legado → slug do catálogo`.

### `series[]` truncado no corpus legado

Dos 1.556 exercícios legados com `series[]`, **176 (11,3%) têm menos entradas que o campo
`s`** — `s=4` com uma única série gravada, por exemplo. Nesses casos os campos achatados
(`s`/`r`/`kg`) são o registro mais completo, e somar as séries parciais subcontaria o volume
em até 75%. A função corrigida ramifica explicitamente: usa `series[]` quando é o registro
completo (sem `s`, ou `series.length === s`), e cai para o achatado quando `series[]` é
demonstravelmente parcial. Globalmente a diferença entre as duas formas no corpus é de
−2,49%. Pendência: decidir se os 176 devem ser corrigidos na origem ou permanecem assim.

### Captura do descanso real (antes do lançamento)

`FD = 90/descanso_s` usa hoje `alvo.descanso_s` (prescrito). O cronômetro de descanso já roda
em `momentum-aluno.html` e o valor é descartado. Descanso é o que separa um protocolo de força
de um metabólico com a mesma carga e reps. A função já lê o campo real quando existe (T2b);
falta a captura no cliente. **`descanso_s` está ausente em 100% dos 1.594 exercícios
legados** — reprocessá-los aplicaria `FD = 1` a todos, ou seja, Metabólica sem informação
alguma de densidade.

### `series_prescritas` não é gravado pelo cliente

`finishTreino()` grava `exercicios[].series[]` com o executado, mas não o número de séries
prescritas — o dado existe em `prescricoes` e não viaja para a sessão. A função grava
`series_executadas` sempre e `series_prescritas` apenas quando derivável do campo achatado
`s` (legado); para sessões novas fica `null`. Sem isso, uma sessão abandonada na metade é
indistinguível de uma sessão curta por prescrição.

### Três fórmulas divergentes para `ic_metabolica`

Função (pré-correção): `cn × FD`. `fix_ic.js`: `s × r × kg × SV` (sem FD). Modelo §2c:
`CargaNorm × FTT × SV × FD`. T2 alinhou a função ao modelo. Escrevem em `sessions`:
`fix_ic.js`, `fix_all.js`, `fix_remaining.js`, `fill_missing_sessions.js`,
`seed_ic_planejado.js` — e `fill_missing_sessions.js` também grava `_recalculated`, então o
flag não identifica quem calculou o quê. Definir a fonte canônica antes de qualquer
reprocessamento futuro.

### `chips` nunca é gravado

O bloco longitudinal de `calcChips` roda em try/catch e a query falha por índice ausente; o
catch engole. 0 de 355 sessões têm o campo. `colapso_de_reps` nunca dispararia: das 5.029
séries, 102 têm `r_alvo` e nenhuma satisfaz `r < r_alvo × 0.75`.

### Pesos `wN/wM/wMet` — chaves que caem no default

O mapa explícito de `getWeights` (T8) reproduz exatamente o comportamento anterior, mas torna
visível que `"Legs"` (20 sessões), `"Volume"`, `"Treino A"`–`"Treino E"` sempre caíram no
default `[0.30, 0.40, 0.30]` — `"Legs"` é sessão de perna e não recebe os pesos de `lower`.
Não alterado nesta correção: os pesos seguem pendentes de revisão fisiológica.

### `firebase-admin`: ^12 em `functions/`, ^13.8 na raiz

Divergência de versão não tocada na correção de leitura — mudar dependência de função é risco
de deploy. Quebra em deploy futuro sem relação aparente com a mudança.

### `firestore.indexes.json` ausente

Índices compostos exigidos por `recalcStudentScores` (`student_id` + `date`) e por
`calcChips` (`student_id` + `tipo` + `date`) não estão declarados. Criar junto com a Fase 2 de
D1.4, não antes — criar o índice sem corrigir a leitura destravaria o segundo defeito.

### Órfãos na raiz do projeto

`public/index.html` e `src/index.ts` não se relacionam a nada do projeto ativo. Possível
resíduo de `firebase init`. Não tocados.

### Migração de `checkins` (pendente, não bloqueante)

Levantado no diagnóstico de banco de set/2026 (50 documentos na coleção):

- **42 documentos com data sem ano** (formato `"10/03"`). O ano precisa ser recuperado do
  `timestamp`. **Não é mecânico:** em pelo menos um caso `data` e `timestamp` divergem
  (`"24/03/2026"` com timestamp em 25/03), então a recuperação exige decisão sobre qual campo
  vence. Quantificar os casos de divergência antes de migrar.
- **1 duplicata real:** `jacqueline` em 2026-03-25, com prontidão 3 e 8 em documentos
  separados. As outras 8 "duplicatas" detectadas eram artefato do agrupamento dos docs sem
  ano, não duplicatas de verdade.
- **Não bloqueia o lançamento.** Check-ins novos já nascem em ISO com id determinístico
  (D2.3), e o listener só precisa funcionar dos novos em diante. Migração ambígua feita às
  pressas cria dado errado com aparência de dado correto.

### Doc id de `prescricoes` — não verificado

A varredura de IDs determinísticos (Bloco 3) deixou o doc de `prescricoes` como único item
não verificado. Os demais já são determinísticos.

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
- Campo autoritativo para exercícios: `exercise_id` (D3.2, set/2026) — `EX_NAME_MAP` e lookup por nome descontinuados

---

## Nota sobre Check-in Pré-treino (implementado e em uso)

A coleção `checkins` existe no Firestore e está em uso real — 50 documentos, todos os alunos
ativos com pelo menos 1. Captura contexto *prospectivo* antes do treino, complementando o
ΔPSE e os chips automáticos, que são *retrospectivos*.

**Correção (set/2026):** este documento afirmava que a Jacqueline estava *"em estado zero,
sem checkins, por reset recente"*. **Ela tem 12 check-ins**, confirmados no banco — dado de
teste, anterior ao lançamento. O estado zero dela vale para `sessions` (0 documentos), não
para `checkins`. Ver *Migração de `checkins`* nas Pendências Não-Críticas.

**Campos confirmados:**
- `estado_prontidao` — resposta da pergunta obrigatória de prontidão (🔥 Pronto / 😐 Ok / 🥱 Cansado / 🤕 Pesado)
- `sono` — qualidade de sono
- `alimentacao` — alimentação adequada
- `disposicao` / `cansaco_nivel` — campos extras além da proposta original, função exata não documentada — confirmar com João Pedro se quiser formalizar

**Decisão original ainda válida:** não fazer ajuste automático de volume baseado em
disponibilidade na v1 (requereria schema de prescrição com faixas min/max — decisão
arquitetural separada).

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

