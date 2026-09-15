> **Registro histórico — não é documento vivo.**
> Este arquivo registra uma rodada de revisão de decisões (set/2026) e serve como fonte do
> *porquê* de cada decisão: alternativas descartadas, razão fisiológica, pontos de tensão.
> **O documento vivo é `momentum-arquitetura-estado.md`**, subseção "Decisões v1 client-side
> (set/2026)" — é lá que status, supersessões e decisões novas são registrados.
> Não editar este arquivo para atualizar uma decisão. Correções de erro factual na redação
> original são a única edição prevista, e devem vir acompanhadas de nota explicando a causa.

# Momentum · Decisões v1 — Bloco 2: Check-in e prontidão

**Data:** set/2026
**Escopo:** v1 aluno (`momentum-aluno.html`) — lançamento Jacqueline
**Origem:** revisão de decisões macro do client-side, Bloco 2
**Destino:** incorporar em `momentum-arquitetura-estado.md`, seção *Decisões Arquiteturais Fechadas*, subseção "Decisões v1 client-side (set/2026)" — mesma subseção do Bloco 1
**Depende de:** `momentum-decisoes-v1-bloco1.md` (D1.2 — formato ISO de data)

---

## Resumo do bloco

A modulação de prontidão **já está implementada e rodando**. A decisão central deste bloco é **desligá-la na v1**, mantendo toda a captura de dados. Adiar sem desligar não seria adiamento — seria lançar o comportamento atual.

| Decisão | O quê |
|---|---|
| D2.1 | Modulação de prontidão **desligada** na v1. Captura mantida. |
| D2.2 | Pular check-in grava `estado_prontidao: null`, não `5`. |
| D2.3 | Listener em `checkins` + ID determinístico. |
| — | Perguntas 2.1 / 2.3 / 2.5 movidas para v2, contexto preservado abaixo. |

---

## D2.1 · Modulação de prontidão desligada na v1

**Estado atual.** `fatorProntidao()` (`:3401`) retorna `{volume, carga}` por faixa de prontidão. `iniciarTreinoComCheckin()` (`:3624`) aplica apenas o volume, e apenas sobre reps:

```js
r: Math.max(1, Math.round(ex.r * f.volume)),
```

`f.carga` **não é usado em nenhum ponto do arquivo**, apesar de a tela de resultado (`:3511`) e o banner de execução (`:2150`) afirmarem à aluna que a carga foi reduzida.

**Decisão.** A modulação não altera a prescrição na v1. `fatorProntidao()` retorna `1.00` em todas as faixas, ou o ponto de aplicação é removido.

**Razão — calibração, não UX.** Os multiplicadores (0.90 / 0.75 / 0.60) são defaults não calibrados, mesma classe dos `wN/wM/wMet` já marcados para revisão com dados reais. Aplicar um modulador não calibrado durante o período em que o modelo está sendo calibrado torna impossível separar:

- variação de IC que veio do estado real da aluna, de
- variação que o próprio sistema injetou ao encolher a prescrição.

Com a modulação desligada, o primeiro mesociclo produz o corpus limpo que torna a calibração possível: **prontidão declarada × execução real, sem intervenção**. O `fatorProntidao` da v2 passa a nascer de dado.

**O que SAI da v1**
- Aplicação de `f.volume` sobre `ex.r` em `iniciarTreinoComCheckin()`.
- Bloco "Treino ajustado: X% do volume · Y% da carga" da tela de resultado (`renderCheckinResultado`, `:3511`).
- Banner de prontidão da tela de execução na parte que afirma ajuste (`renderTreino`, `:2150`) — vira informativo puro ou sai.
- Qualquer copy que afirme ajuste de volume ou carga. Não haverá ajuste; o texto não pode dizer que há.
- `ex.s_original` / `ex.r_original` / `ex.ajustado` perdem função — remover ou manter inertes, decidir na implementação.

**O que PERMANECE na v1**
- Captura completa dos quatro campos (disposição, cansaço, sono, alimentação).
- `calcEstadoProntidao()` e a exibição do número para a aluna — ela vê seu próprio estado.
- Gravação do documento em `checkins`.
- `estado_prontidao_entrada` e `checkin_id` na sessão (`finishTreino`).
- `buildCheckinCorrelacao()` na tela de Evolução — passa a ter dado não-contaminado para mostrar.

**Precondição para reativação (v2).** Só volta quando existirem as três:
1. Corpus de ≥1 mesociclo completo com prontidão declarada e execução não-modulada.
2. Multiplicadores derivados desse corpus, não default.
3. D2.5 resolvida — o fator aplicado precisa ser gravado na sessão (ver §Movido para v2).

---

## D2.2 · Pular o check-in grava `null`, não `5`

**Estado atual.** `checkinSkip()` no passo 1 (`:3577`):

```js
CI.estado_prontidao = 5;
iniciarTreinoComCheckin(null);
```

Prontidão 5 aciona a faixa "Sessão adaptada" (volume 0.75). Ou seja: **"não quero responder" era interpretado como "dia moderado"**, e ela recebia um treino 25% menor sem ter declarado nada.

**Decisão.** Ausência de informação não é informação. Pular grava `estado_prontidao: null`.

**Razão.** Com D2.1 aplicada isso não altera mais o treino — mas altera o corpus. Um `5` que ninguém declarou polui exatamente o dataset que vai calibrar a modulação da v2. `null` é honesto e filtrável.

**Implementação.**
- `checkinSkip()` passo 1 → `estado_prontidao: null`, sem criar documento em `checkins` (ou criando com todos os campos null — decidir; a segunda opção torna a recusa rastreável).
- `finishTreino()` já grava `estado_prontidao_entrada: S.treino.estado_prontidao || null` — verificar que o `|| null` não converte `0` indevidamente.
- Toda leitura downstream precisa tolerar `null` sem cair em default numérico silencioso.

**Correção acoplada — dois caminhos de entrada.** `startTreino()` (`:2071`) e `iniciarTreinoComCheckin()` (`:3624`) são ambos alcançáveis e produzem sessões diferentes a partir do mesmo estado: o primeiro não seta `estado_prontidao` nem `fator`. Consolidar em um único caminho de entrada de treino. Dois entry points divergentes são a origem de sessões inexplicáveis no histórico.

---

## D2.3 · Listener em `checkins` + ID determinístico

**Estado atual.** `openCheckin()` (`:3412`) verifica se já houve check-in no dia:

```js
const jaFez = S.checkinHoje && S.checkinHoje.data === hoje;
```

Mas **não existe query nem listener em `checkins`** no arquivo — há `onSnapshot` em `students` e em `sessions`, e só. `S.checkinHoje` nasce `null` (`:729`) e só é preenchido por `saveCheckinAndStart()` dentro da mesma sessão de navegador.

Consequências:
- Recarregar a página zera o estado → `jaFez` volta a `false` → ela responde de novo → **segundo documento em `checkins` para o mesmo dia**. A escrita é `.add()`, sem id determinístico.
- A home não tem nenhum indicador de check-in feito; o `estado_prontidao` do dia não aparece fora do fluxo de treino.

**Decisão.** Listener em `checkins`, no mesmo padrão dos outros dois.

**Implementação.**
1. `onSnapshot` em `checkins` filtrado por `student_id`, com limite. `S.checkinHoje` derivado da lista pela data de hoje.
2. **ID determinístico** — `checkins/{student_id}_{data_iso}` com `.set()`, nunca `.add()`. Torna a duplicata impossível por construção, não por checagem. Mesmo padrão já usado com sucesso nos scripts de seed.
3. **A comparação de data em `openCheckin` usa `toLocaleDateString('pt-BR')`** — cai sob **D1.2** e migra para ISO junto. Não migrar aqui recria o bug de formato de data numa segunda coleção.
4. Deduplicar os documentos existentes em `checkins` durante a migração.

**Desbloqueia.** Exibir o estado de prontidão do dia na home, e `buildCheckinCorrelacao()` passar a ler de listener em vez de depender do que veio junto com `sessions`.

---

## Movido para v2 — contexto preservado

As três questões abaixo foram levantadas, discutidas e **deliberadamente adiadas**. Ficam registradas para não serem redescobertas do zero.

### V2-A · O que a prontidão modula: reps, séries ou carga?

Volume estava sendo cortado em **reps**, não em séries — escolha implícita, nunca decidida. Reduzir reps mantendo carga preserva intensidade e corta volume; cortar séries corta volume preservando a qualidade das primeiras execuções. Efeitos distintos sobre densidade e sobre o componente Metabólico (`FD = 90/descanso`; número de séries entra em `CargaNorm` direto).

Alternativas registradas:
- Só volume, e volume = séries (preserva a zona de estímulo prescrita: 4 reps a 85% ainda é força; 4 reps a 76% não é nada).
- Volume em reps + carga como sugestão visível e editável no widget.
- **Modulação dependente de `tipo_serie`** — em `forca_pura`/`forca_max` a carga é intocável e o corte é em séries; em `hipertrofia`/`volume`, corte em reps; em `tecnica`, nenhum ajuste (o objetivo já é qualidade sobre carga).

A terceira é a fisiologicamente correta e depende de `tipo_serie` estar disponível no cliente — ou seja, de `prescricoes` ser lido (Bloco 3).

### V2-B · Estado de "repouso recomendado"

Prontidão <2 retorna `volume: 0.00`, que passa por `Math.max(1, Math.round(ex.r * 0))` e vira **1 repetição por série** — um treino completo de singles. O texto diz "considere descansar", o botão diz "Iniciar treino →", e a tela de execução abre normalmente.

Com D2.1, a faixa deixa de ter efeito mecânico. Fica em aberto para v2: se o Momentum quer ter uma opinião sobre **não treinar**, o estado precisa ser terminal (recomendação + saída explícita "treinar mesmo assim", registrada) ou virar sessão de recuperação real. E, se existir, **um dia de descanso recomendado pelo sistema não pode contar como falta na aderência** — conecta com D1.7 e RN02.

### V2-C · O ajuste precisa ser gravado (pré-requisito da reativação)

`finishTreino()` grava `estado_prontidao_entrada` e `checkin_id`, mas **não o fator aplicado** nem os valores originais (`s_original`/`r_original` morrem em memória).

Enquanto nada compara executado contra prescrito, isso não dói. Assim que `prescricoes` for lido, tudo que depende da comparação lê errado: aderência, RN26 `colapso_de_reps` (`r < r_alvo × 0.75`), RN26 `progressão_ok` (`r ≥ r_alvo`), RN13. Um mesociclo de dias de prontidão média produziria uma aluna que "nunca bate o alvo".

Estrutura registrada como preferida:
- `prescricoes` mantém o alvo prescrito intocado;
- a sessão grava `alvo_dia` (ajustado) por série **e** `ajuste_prontidao: {volume, carga, aplicado_em}`.

Assim a cadeia fica auditável ponta a ponta — **prescrição → modulação → execução** — e a pergunta *"por que ela fez 9 e não 10?"* é lida do banco, não reconstruída. É a mesma estrutura que habilita a leitura mais interessante do check-in: correlação entre prontidão declarada e desvio de execução. Se ela declara prontidão baixa e entrega volume cheio, o mal calibrado é o `fatorProntidao`, não ela.

**Esta é precondição de D2.1 voltar.** Reativar a modulação sem gravar o fator recria o mesmo problema de auditabilidade.

---

## Ordem de implementação

```
1. D2.1  desligar modulação (subtração — reps, copy da tela de resultado, banner)
2. D2.2  pular = null + consolidar os dois entry points de treino
3. D2.3  listener em checkins + ID determinístico ISO + dedupe dos existentes
```

D2.3 depende de **D1.2** (formato ISO) já estar aplicado, ou pelo menos de nascer em ISO.
D2.1 e D2.2 são independentes de tudo — podem ir primeiro, e são as mais baratas do conjunto.

---

## Pendências geradas por este bloco

| Item | Tipo | Bloqueia |
|---|---|---|
| Pular check-in cria documento com campos null, ou não cria? | produto | D2.2 |
| Destino de `s_original`/`r_original`/`ajustado` após D2.1 | código | D2.1 |
| Consolidação dos dois entry points de treino | código | D2.2, Bloco 3 |
| Dedupe dos `checkins` duplicados existentes | dado | D2.3 |
| Exibir prontidão do dia na home — entra na v1? | produto | — |
| Corpus de ≥1 mesociclo para calibrar `fatorProntidao` | calibração | reativação v2 |
