> **Registro histórico — não é documento vivo.**
> Este arquivo registra uma rodada de revisão de decisões (set/2026) e serve como fonte do
> *porquê* de cada decisão: alternativas descartadas, razão fisiológica, pontos de tensão.
> **O documento vivo é `momentum-arquitetura-estado.md`**, subseção "Decisões v1 client-side
> (set/2026)" — é lá que status, supersessões e decisões novas são registrados.
> Não editar este arquivo para atualizar uma decisão. Correções de erro factual na redação
> original são a única edição prevista, e devem vir acompanhadas de nota explicando a causa.

# Momentum · Decisões v1 — Bloco 3: Origem do treino do dia

**Data:** set/2026
**Escopo:** v1 aluno (`momentum-aluno.html`) — lançamento Jacqueline
**Origem:** revisão de decisões macro do client-side, Bloco 3
**Destino:** incorporar em `momentum-arquitetura-estado.md`, subseção "Decisões v1 client-side (set/2026)"
**Depende de:** Blocos 1 e 2 (já registrados)

---

## Por que este bloco é diferente

Contagem de ocorrências em `momentum-aluno.html` antes desta revisão:

| Termo | Ocorrências |
|---|---|
| `prescricoes` | **0** |
| `collection('exercises')` | **0** |
| `EX_NAME_MAP` | **0** |
| `tipo_serie` | **0** |

O app do aluno não lê a prescrição, não carrega a coleção de exercícios e não tem o mapa de
normalização de nomes que as instruções do projeto tratam como padrão — ele existe no
`momentum-dashboard-v3.html`, não aqui. Todo treino vinha de `buildTreinoFromProfile()`:
cinco exercícios genéricos por `s.profile`, com `kg: 0`.

Este bloco não melhora a origem do treino. **Constrói o caminho de leitura que nunca existiu.**

**Consequência de prazo:** a leitura de `prescricoes` deixa de ser evolução e passa a ser
pré-requisito de lançamento. Não existe caminho em que a aluna treina corretamente sem ela.

---

## D3.1 · `prescricoes` é a origem única do treino

**Estado anterior.** `buildTreinoFromProfile()` montava o treino a partir de cinco templates
internos selecionados por `s.profile`. Origem confirmada: **resíduo de mock** — treino de
amostra criado a partir de um PDF para testar a tela de execução. Nunca foi decisão de produto.

**Mas não era mock na prática.** Era chamado por `startTreino()` e por
`iniciarTreinoComCheckin()`, e o que montava ia direto para `finishTreino()` e para o
Firestore. Andaime que escreve no banco não é andaime.

**Decisão.**
- `momentum-aluno.html` lê `prescricoes` e monta o treino a partir do documento real.
- `buildTreinoFromProfile()` e os cinco templates são **removidos**.
- `s.profile` perde o consumidor e é **descontinuado** (a intenção de treino vive em
  `prescricoes`, `dim_dominante` e `modelo_periodizacao`; `profile` era muleta para a
  ausência de prescrição, e o schema documentava 3 valores enquanto o código tinha 5).

**Nota sobre o dano dos templates.** Três dos cinco nomes não eram exercícios, eram
categorias: `'Agachamento / Leg Press'` (dois movimentos com IM e DN distintos),
`'Puxada / Remada'`, `'Isolamento · Bíceps'` (não nomeia movimento). Nenhum resolve contra
`exercises`. Sessão gravada com esses nomes perdeu a informação de qual movimento foi feito —
**irrecuperável por reprocessamento**, diferente das lacunas dos Blocos 1 e 2.

---

## D3.2 · `exercise_id` é o campo autoritativo — supersede a regra de ouro

**Regra anterior** (instruções do projeto, `CLAUDE.md`, `arquitetura-estado.md`):
> `nome` é o campo autoritativo de exercícios. `exercise_id` em sessões legadas é
> não-confiável. Lookup via `EX_NAME_MAP` com normalização Unicode + trim + lowercase.

Essa regra era sobre **leitura de dado que já existe**: os IDs no banco não eram confiáveis,
então não dava para fazer join por eles retroativamente. Não era uma afirmação de que ID é
ruim como mecanismo.

**Decisão.** `exercise_id` passa a ser autoritativo. `nome` continua sendo gravado na sessão
como **snapshot de exibição**, não como chave.

**Sem período de convivência.** As sessões anteriores ao corte deixam de existir (decisão do
PT), então não há dois regimes. `exercise_id` é autoritativo, ponto.

**Por que ID é superior.** Validação por nome exige normalização e ainda é aproximada —
`'Rosca Direta'` e `'Rosca direta '` colidem, mas `'Supino Reto'` e `'Supino reto c/ barra'`
não. É comparação difusa fazendo papel de chave estrangeira. ID é binário: existe ou não.

**Por que `nome` continua sendo gravado.** Se um exercício for renomeado ou removido de
`exercises`, a sessão antiga ainda diz o que foi feito sem depender do join. Auditabilidade
não deve exigir que a coleção de referência esteja intacta.

**Risco verificado e descartado.** Doc ids auto-gerados não sobrevivem a re-seed com `.add()`
— qualquer script que recriasse a coleção quebraria toda referência silenciosamente.
**Verificado: não se aplica.** `import.js` usa `.doc(ex.id).set(ex)` com slug semântica
(`"squat"`, `"terra"`, `"extensora"`). IDs já determinísticos, sem migração necessária.

**Cadeia pretendida:**

```
exercises/{slug}  ←── exercise_id ──  prescricoes.sessoes{}.exercicios[]
                                              │
                                              ▼ (app copia id + nome)
                                      sessions.exercicios[]
                                         { exercise_id, nome, ... }
```

**Validação na escrita (mantida).** `finishTreino()` resolve cada `exercise_id` contra
`exercises` antes de gravar e falha visível se não resolver. Não é rede para o template
(que morreu) — é garantia de que nenhuma origem futura (RN06 exercício extra, sessão livre,
prescrição com id errado) escreva sessão sem identidade resolvível.

### Atualização documental obrigatória

A decisão só vale quando os documentos mudarem. Enquanto disserem `nome`, o Claude Code
continuará implementando por nome — corretamente, seguindo o que está escrito.

| Documento | Mudança |
|---|---|
| Instruções do projeto (claude.ai) | Gotcha `nome` autoritativo → `exercise_id` autoritativo, `nome` como snapshot |
| `CLAUDE.md` (repo) | Mesma nota — é o primeiro documento que o Claude Code lê |
| `momentum-schema-firestore.md` | `sessions.exercicios[].exercise_id`: de "não-confiável" para FK obrigatória; `nome` como denormalização de exibição |
| `momentum-arquitetura-estado.md` | Esta decisão, com o marco de corte declarado |

---

## D3.3 · Granularidade de `exercises` = granularidade do modelo

**Questão.** Supino reto com barra, com halteres e na máquina são o mesmo exercício?

**Decisão.** Não. **Um doc por variação.**

**Razão fisiológica.** As três variações têm CT, IM, DN, SV e FC diferentes. Máquina tem CT
baixo (trajetória guiada) e estabilização quase nula; halteres têm CT e DN mais altos pela
demanda de controle unilateral; barra fica no meio, com maior carga absoluta possível. Se as
três compartilham um doc, o modelo perde exatamente a distinção que existe para medir.

```
supino-reto-barra
supino-reto-halteres
supino-reto-maquina
```

**Agrupamento não vem do slug.** Vem do campo **`pattern`**, que já existe em `exercises`
(`push_h` para as três). É ele que alimenta "volume por padrão de movimento", já no Roadmap v2.
**Slug identifica; `pattern` agrupa.** Não sobrecarregar o slug com hierarquia.

**Pendência registrada, não bloqueante.** Os slugs atuais misturam inglês e português e usam
abreviações inconsistentes (`"squat"`, `"terra"`, `"extensora"`). Vai doer quando a coleção
crescer. Não é problema da v1.

---

## D3.4 · A aluna escolhe a sessão do dia

**Estado anterior.** `prescricoes.sessoes` é objeto-mapa com chaves livres definidas pelo PT
(`"Lower A"`, `"Full B"`, `"Lower A · Deload"`), sem enum fixo. **Nada no sistema diz qual é
a sessão de hoje.** `students.divisao` é string solta de label, desconectada da estrutura.

**Decisão.** A home lista as sessões de `prescricoes.sessoes` e a aluna toca a que vai fazer.
Zero campo novo, zero inferência, zero risco de o app servir a sessão errada.

**Alternativas descartadas para a v1:**
- Rotação por histórico — frágil (chaves com sufixo `· Deload` quebram o casamento) e sem
  âncora no estado zero.
- `ordem: []` explícita em `prescricoes` — determinístico, mas exige campo novo e regra de
  avanço, e não lida bem com dia pulado.

**Escopo de `ordem` (esclarecimento).** O campo `ordem` foi descartado como **mecanismo de
seleção** — o sistema não infere qual sessão é a de hoje nem avança automaticamente. Ele
permanece em uso como **ordenação de exibição**: define a sequência em que as sessões
aparecem na lista da home, e nada mais. Os valores foram redeclarados com intenção de
periodização pelo PT (antes eram derivados de `Object.keys()`), de modo que a v1.1 — em que
o app sugere a próxima sessão e a divergência da aluna fica registrada como sinal — já nasce
com a base correta.

**Direção v2:** o app propõe segundo a periodização e ela pode divergir; a divergência fica
registrada como sinal. Requer a ordem explícita.

**Resolve D3.C por consequência.** Com a aluna escolhendo, "treinar fora do dia previsto"
deixa de ser um estado — ela escolhe qualquer sessão do mapa, sempre. Não há fallback de
"dia sem prescrição" porque não há dia prescrito. Os casos de mesociclo encerrado (D1.6) e
prescrição ausente permanecem como estados de home, não do fluxo de treino.

**Sessão livre** (montar treino escolhendo de `exercises`, cai em RN06) fica para v1.1.

---

## D3.5 · O `alvo` completo viaja para a sessão

**Estado anterior.** O objeto `alvo` carrega oito campos por exercício. O template interno
carregava quatro; a tela de execução consome três (kg, reps, descanso). `tipo_serie` aparecia
zero vezes no arquivo.

Os campos sem consumidor eram exatamente os que definem as dimensões que o Momentum mede:
`tut_s` e `tempo_s` alimentam FTT no componente Metabólico; `descanso_s` alimenta FD
(`90/descanso`); `pse` é o alvo contra o qual RN26 avalia `progressão_ok`; `tipo_serie` é o
enum de intenção que a modulação da v2 vai precisar (V2-A).

**Decisão.** Todo o `alvo` é lido da prescrição e gravado em `sessions.exercicios[].alvo`,
**mesmo o que a tela não exibe** — incluindo `tipo_serie` e `progressao`.

**Razão.** Custo quase zero (o dado já existe do outro lado) e é o que dá à Metabólica o TUT
e o descanso reais em vez de defaults. Habilita RN26 sem trabalho de tela. Não gravar é jogar
fora informação já escrita.

**`pse_alvo` NÃO é exibido para a aluna na v1.** Efeito de ancoragem: se ela vê "alvo PSE 8"
antes de reportar, o PSE relatado deixa de ser independente — e `PSE_relatada` é metade do
blend de `PSE_ritmo`. Contaminaria o corpus na semana em que ele mais importa. Reavaliar
quando a calibração estiver estável.

---

## D3.6 · Chaves de `sessoes` separam slug de label

**Estado anterior.** `"Lower A · PR Agachamento"` é simultaneamente o texto exibido e a
identidade da sessão. Consequências: renomear quebra a referência, e casar `sessions.tipo`
com a chave vira matching de string com sufixo.

**Decisão.** Separar:

```json
"lower-a": {
  "label": "Lower A · PR Agachamento",
  "ic_planejado": ...,
  "exercicios": [...]
}
```

`sessions.tipo` grava o **slug**, não o label.

**Princípio.** Identidade estável não deve ser texto de exibição — mesma razão de D3.2 e do
ID determinístico de `exercises`.

**Por que agora e não depois.** O documento da Jacqueline já será reescrito para o backfill
de `exercise_id` (ver §Bloqueante). Separar slug de label pega carona na mesma edição — custo
quase zero agora, alto depois, quando houver sessões referenciando as chaves antigas.

---

## D3.7 · ID determinístico em `sessions`

**Estado anterior.** `finishTreino()` usa `.add()`. Toque duplo em "finalizar" ou reload no
meio da escrita cria sessão duplicada, silenciosamente. Também: `S.treino.sessaoId` é gerado
como `sim_${Date.now()}` e **nunca usado** — o `.add()` gera o próprio id.

**Decisão.** `.set()` com id determinístico: `{student_id}_{data_iso}_{n}`, onde `n`
desambigua duas sessões legítimas no mesmo dia.

**Razão.** Mesma linha de código que já será tocada. Duplicata em sessão é pior que em
check-in — polui aderência e o corpus dimensional. Impossibilidade por construção, não por
checagem.

**Remover** `S.treino.sessaoId` ou passá-lo a carregar o id real.

---

## BLOQUEANTE · Backfill de `exercise_id` na prescrição da Jacqueline

**`momentum-schema-firestore.md` documenta:**

> `sessoes.<NomeSessao>.exercicios[].exercise_id` — **Ausente em documentos mais novos
> (ex: Lower C e Upper C da Jacqueline)** — consistente com a direção de `nome` como único
> campo autoritativo.

A prescrição genuína da Jacqueline — a única prospectiva do banco, e a que o app vai ler — é
justamente a que não tem os IDs em pelo menos duas sessões.

**Não é decisão, é correção.** Sem isso, D3.2 não tem de onde ler o `exercise_id`.

**Ação:** script que percorre `prescricoes/{jacqueline}`, resolve cada `nome` contra
`exercises` e grava o `exercise_id` correspondente. Falhar alto em qualquer nome que não
resolva — esses são os que precisam de decisão manual sua (variação não cadastrada, nome
divergente).

**Fazer junto com D3.6** (separação slug/label) — mesma edição do mesmo documento.

---

## Varredura · Padrão de ID determinístico no sistema

Extensão do princípio de D3.2 e D3.7 às demais coleções:

| Coleção | Hoje | Determinístico | Ganho | Status |
|---|---|---|---|---|
| `exercises` | ✅ `.doc(id).set()`, slug semântica | — | — | já correto |
| `students` | ✅ `enrique`, `jacqueline` | — | — | já correto |
| `checkins` | `.add()` | `{student_id}_{data_iso}` | Impede duplicata por reload | **D2.3** |
| `sessions` | `.add()` | `{student_id}_{data_iso}_{n}` | Impede duplicata por toque duplo | **D3.7** |
| `prescricoes.sessoes{}` | chave = label | slug + campo `label` | Renomear sem quebrar referência | **D3.6** |
| `prescricoes` (doc) | não verificado | `{student_id}` ou `{student_id}_{mesociclo}` | Leitura direta sem query | pendente |

---

## Ordem de implementação

```
1. BLOQUEANTE  backfill exercise_id + separação slug/label na prescrição da Jacqueline
2. D3.2        atualizar CLAUDE.md, instruções do projeto e schema (exercise_id autoritativo)
3. D3.1        remover buildTreinoFromProfile(), templates e s.profile
4. D3.4/D3.5   leitura de prescricoes: seleção de sessão pela aluna + alvo completo
5. D3.7        ID determinístico em sessions + remover sessaoId morto
6. D3.2        validação de exercise_id na escrita de finishTreino()
```

O passo 2 vem antes do 3 e do 4 deliberadamente: o Claude Code lê os documentos antes de
decidir, e enquanto eles disserem `nome`, ele implementará por nome.

---

## Pendências geradas por este bloco

| Item | Tipo | Bloqueia |
|---|---|---|
| Nomes que não resolvem no backfill — variação não cadastrada ou nome divergente | dado | BLOQUEANTE |
| Slugs de `exercises` misturam idiomas e abreviações | dívida | — |
| Doc id de `prescricoes` — determinístico? | schema | — |
| `progressao_mae` duplicado entre `students` e `prescricoes` | schema | — |
| Ordem explícita de sessões (proposta automática do app) | produto | v2 |
| Sessão livre / RN06 exercício extra | produto | v1.1 |
| Exibir `pse_alvo` — reavaliar após calibração | produto | v2 |
