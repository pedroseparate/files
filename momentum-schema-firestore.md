# Momentum · Schema Firestore (momentum-br)

**Fonte:** inventário de campos extraído via Claude Code direto do banco (não de snapshot),
cruzado com leitura de código (`momentum-aluno.html`, `momentum-dashboard-v3.html`,
`momentum-dashboard-v5.html`, `momentum-pt-dashboard.html`) e com diagnóstico de uso real.
**Escopo:** estrutura de campos — sem valores específicos de aluno.
**Regra:** qualquer valor concreto de um aluno (scores atuais, sessões, estado do mesociclo)
precisa ser pedido ao Claude Code no momento — este doc é referência estrutural, não estado.

---

## `students`

| Campo | Nota |
|---|---|
| `name` | Nome de exibição |
| `email` | Contato/auth |
| `id` | Duplicata do doc id como campo |
| `pt_id` | PT responsável |
| `since` | Data de início com o PT |
| `nivel` | Iniciante/Intermediário/Avançado — atribuído manualmente pelo PT, sem promoção automática |
| `profile` | Lente do aluno: `hiper` / `recomp` / `forca` — usado por `buildTreinoFromProfile()` pra escolher template genérico quando não há prescrição real |
| `risk` | Não documentado, não referenciado em nenhum arquivo verificado |
| `status` | Não documentado, não referenciado em nenhum arquivo verificado |
| `goal` | Label curto de objetivo — usado como label primário (ex: no prompt de narrativa da IA: `Objetivo: ${s.goal}`) |
| `objetivo` | **Descontinuar candidato** — campo top-level lido em nenhum arquivo do repositório. Só escrito por `reset_jacqueline.js`. Distinto de `anamnese.objetivo` (esse sim é lido em `momentum-aluno.html`, `momentum-dashboard-v5.html`, `momentum-pt-dashboard.html`) |
| `observacoes_clinicas` | **Descontinuar candidato** — zero leitura confirmada em qualquer arquivo. Só escrito por `reset_jacqueline.js` |
| `notas` | Notas livres do PT sobre o aluno |
| `mesociclo` | Nome/label do mesociclo atual (ex: "Full Body · Linear II") |
| `mesociclo_inicio` | Data explícita de início — nunca inferir de sessões (decisão fechada) |
| `semanas_total` | Duração do mesociclo em semanas |
| `divisao` | Label descritivo da divisão (ex: "Full Body 3x") — string solta, separada da estrutura real de prescrição que vive em `prescricoes` |
| `modelo_periodizacao` | `linear / dup / block / conjugado / assimetrico` — fallback: infere do nome do mesociclo; default `linear` |
| `dim_dominante` | Dimensão declarada como foco do mesociclo — alimenta a lógica editorial do hero card |
| `ritmo_estado` | `alta/estável/baixo/sobrecarga` — ausente em estado zero (campo removido, não nulo) |
| `recuperacao_estimada_h` | Janela de recuperação estimada — uso exato não confirmado no código, provavelmente informativo pro PT |
| `progressao_mae.modelo` | Aparece também em `prescricoes` — **possível duplicidade entre coleções**, não resolvido |
| `progressao_mae.logica_volume` | Idem |
| `scores.neural` / `.mecanica` / `.metabolica` / `.tecnica` / `.ritmo` / `.momentum` | Os 6 scores 0–10 — ausentes em estado zero |
| `momentum_snapshot.valor` / `.data` / `.sessao_id` | Cache do último score Momentum + sessão que gerou — ausente em estado zero |
| `records.*` | PRs — chaves dinâmicas por exercício, não é schema fixo |
| `anamnese.idade` / `.sexo` / `.peso_kg` / `.altura_cm` | Dados biométricos |
| `anamnese.objetivo` | Lido em todas as telas — campo real de objetivo, junto com `goal` |
| `anamnese.preferencias` | Preferências declaradas |
| `anamnese.restricoes` | Restrições físicas — lido em `momentum-dashboard-v3.html` |
| `anamnese.historico` | Histórico de treino em texto livre |
| `anamnese.disponibilidade` | Parseada por `DIAS_MAP` pra inferir frequência |
| `anamnese.observacoes` | **Órfão** — sem script de escrita ativo, sem leitura confirmada. Dado antigo, deixar como está |
| `perfil_recuperacao.*` | Sono/variabilidade/correlação — já populado em parte dos alunos |
| `semanas[]...` | **Legado morto** — só 1 de 10 documentos tem o campo (`iarima_nunes`). Nenhum script escreve nele hoje. `momentum-dashboard-v5.html` reconstrói essa mesma estrutura em memória a partir de `sessions`, não lê o campo do documento. Sem risco, sem urgência de limpar |

---

## `sessions`

| Campo | Nota |
|---|---|
| `id` | Duplicata do doc id |
| `student_id` | FK pra `students` |
| `date` | Formato historicamente inconsistente entre documentos (`"2026-01-08"` vs `"22/03/2026"`) |
| `mesociclo` | Label denormalizado |
| `semana` | Número da semana no mesociclo |
| `tipo` | Label da divisão **executada** (retrospectivo — ex: "Full A") |
| `dim_dominante` | Dimensão dominante da sessão específica |
| `pse` | PSE geral da sessão |
| `duracao_min` | **Confirmado em uso ativo** (`momentum-aluno.html`, `momentum-dashboard-v5.html`, `momentum-cliente-enrique.html`, com fallback `carga_interna \|\| pse×duracao_min`). A pendência em `arquitetura-estado.md` está desatualizada |
| `carga_interna` | CargaInterna = PSE × duração (Foster) |
| `ic_neural` / `ic_mecanica` / `ic_metabolica` | Totais dimensionais da sessão |
| `ic_executado` / `ic_planejado` | Par executado/planejado — RN 19 |
| `indice_carga` | **Resolvido** — é nome legado de `ic_executado`. `normalizeSession()` em `momentum-dashboard-v5.html`: `raw.ic_executado \|\| raw.indice_carga \|\| 0`. Migração em andamento, não duplicidade real |
| `ratio_adaptacao` | Sempre tendência relativa, nunca valor absoluto |
| `ritmo_delta` | Hipótese não confirmada — pendência documentada como "confirmar com João Pedro" |
| `n` / `m` / `met` | Prováveis proporções realizadas por dimensão na sessão — não confirmado, distinto de `pesos.wN/wM/wMet` |
| `pesos.wN` / `.wM` / `.wMet` | Pesos por tipo de sessão — defaults não calibrados |
| `_recalculated` | Flag de reprocessamento pelo PT Dashboard |
| `exercicios[].nome` / `.exercise_id` | `nome` autoritativo; `exercise_id` legado |
| `exercicios[].kg` / `.r` / `.s` / `.pse` | Valores executados |
| `exercicios[].ic` / `.ic_neural` / `.ic_mecanica` / `.ic_metabolica` | IC por exercício |
| `exercicios[].tipo_serie` | Enum de intenção — só texto exibido em v1 |
| `exercicios[].alvo.*` | **Resolvido** — snapshot congelado de um backfill pontual (`add_tipo_serie_prescricoes.js`), não é campo vivo. `finishTreino()` não escreve nele no fluxo normal. O alvo ativo de verdade está em `prescricoes`, não aqui |
| `exercicios[].series[].kg` / `.r` / `.pse` / `.n` / `.tipo` | Valores executados por série |
| `exercicios[].series[].kg_alvo` / `.r_alvo` / `.pse_alvo` | Valores alvo por série |
| `exercicios[].series[].legacy` | Flag de formato antigo |

---

## `prescricoes` (descoberta durante esta revisão — não fazia parte do inventário original)

10 documentos — todos os alunos têm um. `sessoes` é **objeto-mapa**, não array: cada chave é
o nome livre da sessão/divisão, definido pelo PT (`"Lower A"`, `"Full B"`, `"Treino C"`,
`"Lower A · Deload"`, `"Lower A · PR Agachamento"` — sem enum fixo, varia por aluno).

| Campo | Nota |
|---|---|
| `student_id` | FK |
| `mesociclo` | Label do mesociclo coberto por esta prescrição |
| `atualizado_em` | Timestamp — campo atual |
| `updated_at` | Legado — alguns docs antigos usam este em vez de `atualizado_em`. Mesmo padrão de migração que `indice_carga`/`ic_executado` |
| `progressao_mae.modelo` / `.logica_volume` | Também aparece em `students` — duplicidade entre coleções não resolvida |
| `sessoes.<NomeSessao>.ic_planejado` | IC planejado pra aquela sessão específica |
| `sessoes.<NomeSessao>.dim_dominante` | Dimensão dominante daquela sessão |
| `sessoes.<NomeSessao>.notas_pt` | Nota do PT específica daquela sessão prescrita |
| `sessoes.<NomeSessao>.exercicios[].nome` | Nome do exercício |
| `sessoes.<NomeSessao>.exercicios[].exercise_id` | Ausente em documentos mais novos (ex: Lower C e Upper C da Jacqueline) — consistente com a direção de `nome` como único campo autoritativo |
| `sessoes.<NomeSessao>.exercicios[].tipo_serie` | Enum de intenção |
| `sessoes.<NomeSessao>.exercicios[].series` | Número de séries prescritas |
| `sessoes.<NomeSessao>.exercicios[].progressao` | Modelo de progressão daquele exercício |
| `sessoes.<NomeSessao>.exercicios[].alvo.carga_kg` / `.reps` / `.pse` / `.descanso_s` / `.tut_s` / `.tempo_s` / `.pausa_s` / `.intervalo_s` | Alvo completo por exercício — **esta é a estrutura real de "Treino A/B/C"** que eu não tinha encontrado antes |

**Nuance importante:** pra 9 dos 10 alunos, este documento foi gerado retroativamente por
`add_tipo_serie_prescricoes.js`, inferindo a prescrição a partir do histórico de sessões já
executadas — é documentação do que aconteceu, não plano prospectivo. Só o doc da
**Jacqueline** (`reset_jacqueline.js`, hoje) é prescrição genuína, escrita antes de qualquer
execução. `fix_prescricoes.js` aplica patches pontuais (capitalização, capping de PSE) — não
cria documentos.

**Nenhuma tela lê `prescricoes` hoje.** A estrutura existe, o caminho de leitura não.

---

## `exercises`

| Campo | Nota |
|---|---|
| `id` | Doc id |
| `name` | Nome do exercício — em inglês como chave de campo, enquanto `sessions`/`students`/`prescricoes` usam `nome` (português). Nomenclatura inconsistente entre coleções, não é bug |
| `icon` | Emoji/ícone de exibição |
| `note` | Nota descritiva do movimento |
| `group` | Não confirmado |
| `pattern` | Padrão de movimento (squat, hinge, push_h, push_v, pull_h, pull_v...) |
| `muscles` | Grupos musculares |
| `valences` | Não confirmado |
| `CT` | Complexidade Técnica (0–10) — amplificador do custo neural. Ex: Hack Machine CT=2.0, Snatch CT=9.5 |
| `IM` | Impacto Mecânico (0–10) — base do componente Mecânica |
| `DN` | Demanda Neural (0–10) — **base do componente Neural**, amplificado por CT e SV. (As instruções do projeto citam DN também na Mecânica — divergência; `modelo-matematico.md` e a fórmula consolidada confirmam Neural como correto) |
| `SV` | Sensibilidade à Velocidade (0–10) — amplifica custo neural e metabólico quando intenção explosiva é prescrita |
| `FC` | Fator de Carga Neural (0.3–1.5) — só entra no componente Neural, não em CargaNorm. FC e DN são distintos mas relacionados (r=0.88) |
| `explos` | Boolean — exercício explosivo; quando `true`, não recebe multiplicador extra |

---

## `checkins`

**Confirmado: feature em uso real**, não é dado de seed. 8 de 9 alunos ativos (excluindo
Jacqueline, em estado zero) têm pelo menos 1 checkin. `arquitetura-estado.md` descreve essa
feature como "proposta, não implementada" — **isso está desatualizado, precisa correção**.

| Campo | Nota |
|---|---|
| `student_id` | FK |
| `session_id` | FK — vincula o check-in a uma sessão específica |
| `data` / `timestamp` | Data/hora |
| `estado_prontidao` | Resposta da pergunta obrigatória de prontidão — usado extensivamente em `momentum-aluno.html` |
| `sono` | Qualidade de sono |
| `alimentacao` | Alimentação adequada |
| `disposicao` / `cansaco_nivel` | Campos extras além do descrito na nota original de "check-in pré-treino" |

---

## Itens ainda abertos (poucos, e de baixa urgência)

1. **`progressao_mae.{modelo,logica_volume}`** existe em `students` e em `prescricoes` — checar se é duplicidade real ou papel distinto em cada coleção.
2. **`n`/`m`/`met`** em `sessions` — provável proporção realizada por dimensão, não confirmado com certeza.
3. **`group`** e **`valences`** em `exercises` — função não confirmada em nenhum doc ou código verificado.
4. **`risk`** e **`status`** em `students` — mesma situação.

Nenhum desses bloqueia uso do schema — são lacunas de documentação, não inconsistência de dado.
