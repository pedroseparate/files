> **Registro histórico — não é documento vivo.**
> Este arquivo registra uma rodada de revisão de decisões (set/2026) e serve como fonte do
> *porquê* de cada decisão: alternativas descartadas, razão fisiológica, pontos de tensão.
> **O documento vivo é `momentum-arquitetura-estado.md`**, subseção "Decisões v1 client-side
> (set/2026)" — é lá que status, supersessões e decisões novas são registrados.
> Não editar este arquivo para atualizar uma decisão. Correções de erro factual na redação
> original são a única edição prevista, e devem vir acompanhadas de nota explicando a causa.

# Momentum · Decisões v1 — Bloco 1: Entrada no app

**Data:** set/2026
**Escopo:** v1 aluno (`momentum-aluno.html`) — lançamento Jacqueline
**Origem:** revisão de decisões macro do client-side, Bloco 1 (identidade, estado zero, âncora temporal)
**Destino:** incorporar em `momentum-arquitetura-estado.md`, seção *Decisões Arquiteturais Fechadas*, como subseção "Decisões v1 client-side (set/2026)"

> Todas as sete são **decisões fechadas**. Reproposta exige justificativa fisiológica ou de produto explícita.

---

## D1.1 · Sem autenticação na v1 — declarado, não acidental

**Estado atual.** `momentum-aluno.html:720` — `STUDENT_ID` vem de query param (`?id=`) com fallback hardcoded `'enrique'`. Nenhuma leitura de `firebase.auth()`. `login.html` existe mas não é validado pelo dashboard.

**Decisão.** Manter como está. A v1 roda com uma aluna, em fase de teste. Isso passa de comportamento acidental a comportamento declarado.

**Consequências aceitas.**
- Qualquer pessoa com a URL e um `id` válido lê o dashboard completo de qualquer aluno.
- Se as Firestore Security Rules estiverem abertas, o banco é legível por qualquer um que tenha a config do Firebase — que está no cliente por definição.

**Gatilho de revisão.** A entrada da **segunda aluna real** reabre esta decisão. Não esperar o terceiro caso.

**Ação v1.1 (não agora).** Firebase Auth + campo `firebase_uid` em `students` + Security Rules restringindo leitura ao próprio documento.

---

## D1.2 · ISO `YYYY-MM-DD` é o formato canônico de data

**Estado atual.** Duas chaves (`date`, `data`) e dois formatos (ISO e pt-BR `DD/MM/YYYY`) convivem. `finishTreino()` (`:2483`) grava pt-BR. O cálculo de aderência (`:1041`) compara lexicograficamente contra strings ISO — `"01/09/2026" >= "2026-09-01"` é `false`, então **toda sessão criada pelo próprio app é filtrada para fora de `realizados`** e a aderência lê 0%.

**Decisão.** `data` em ISO `YYYY-MM-DD`, sempre. Formatação pt-BR é responsabilidade exclusiva da camada de exibição (`fmtSessDate()`).

**Implementação.**
1. `finishTreino()` passa a gravar `new Date().toISOString().slice(0,10)`.
2. Script de migração das sessões legadas em pt-BR → ISO.
3. Auditoria dos ~6 pontos que hoje fazem `x.date || x.data`; consolidar em `data`.
4. Decidir o destino de `date` (descontinuar após migração).

**Princípio derivado — aplica-se além desta decisão.**
> Toda duplicidade de campo legado/atual descoberta é **migrada no momento da descoberta**, não acumulada. Vale para os pares já documentados: `indice_carga`/`ic_executado`, `updated_at`/`atualizado_em`, `date`/`data`.

---

## D1.3 · `S.sessions` passa a ser ordenado crescente

**Estado atual.** O `onSnapshot` (`:767`) ordena decrescente (`tb - ta`). Dentro de `buildHeroCard()`:
- `dimPercentile()` usa `vals.slice(-4)` → pega as **4 mais antigas**, não as 4 recentes.
- `dimTrend()` usa `r4 = vals.slice(-4)` e `p4 = vals.slice(-8,-4)` → `r4` é anterior a `p4`, **sinal da tendência invertido**.

Isso alimenta `dimEstado()` → `heroKey`/`heroReason` → a frase da primeira dobra da home. Aluno progredindo aparece como `queda`.

Três convenções coexistem no mesmo arquivo: `buildICChart()` (`:1821`, `slice(0,10).reverse()`) e `renderMemoriaPositiva()` (`slice(0,5)`) estão corretas; o hero não.

**Decisão.** Inverter a convenção: `S.sessions` ordenado **crescente** (mais antigo primeiro). `slice(-n)` passa a significar literalmente "últimas n".

**Implementação.**
1. Inverter o comparador no `onSnapshot` (`ta - tb`).
2. Ajustar todos os consumidores que hoje assumem decrescente — no mínimo: `buildICChart()`, `renderMemoriaPositiva()`, `buildHeroCard()` (bloco de aderência, `sess[sess.length-1]` como mais antigo), `buildWeekStrip()`, `openHistSession()` e a indexação de `S.sessions` usada no `onclick`.
3. Remover o comentário desatualizado da `:1009`.

**Nota de método.** Este erro não seria detectado por simulação de cenário — projetar o hero "com a lógica real" reproduz a inversão junto. Auditoria de código e simulação macro são complementares, não substitutas.

---

## D1.4 · Cálculo dimensional em Cloud Function `onCreate`

**Estado atual.** `finishTreino()` grava `student_id`, `tipo`, `data`, `timestamp`, `pse`, `duracao_min`, `estado_prontidao_entrada`, `checkin_id`, `exercicios`. **Não grava `indice`, `indice_carga`, `ic_neural`, `ic_mecanica`, `ic_metabolica`.**

`buildHeroCard():862` filtra: `x => !x.simulado && (x.indice||x.indice_carga) && x.pse`. Logo, a sessão recém-executada é **invisível** para percentis, tendências e trajetória dimensional. A aluna treina, o app confirma que salvou, e a home não muda.

Resolve a pendência aberta: *onde `scores.*` e `ritmo_estado` são computados*. Resposta estrutural até aqui: em lugar nenhum dentro do cliente — são valores estáticos de seed.

**Decisão.** Cloud Function disparada em `onCreate` de `sessions`.

**Responsabilidades da função.**
1. Resolver cada exercício da sessão via `exercise_id` contra `exercises` (D3.2). O campo é
   autoritativo e validado na escrita por `finishTreino()`; `nome` é snapshot de exibição e
   não deve ser usado como chave de lookup.
2. Calcular `ic_neural` / `ic_mecanica` / `ic_metabolica` conforme `momentum-modelo-matematico.md` §2 (aquecimento excluído; FC só no Neural, fora de CargaNorm).
3. Escrever os `ic_*` de volta no documento da sessão.
4. Recalcular `scores.*` e `ritmo_estado` no doc do aluno (RN20, RN21b), respeitando o adapter de periodização por `modelo_periodizacao`.
5. O `onSnapshot` já existente propaga para a home sem mudança no cliente.

**Razão.** Mantém os coeficientes (CT/IM/DN/SV/FC — propriedade do Momentum) fora do cliente, e a home atualiza sozinha via listener.

**Riscos a tratar na implementação.**
- Janela de inconsistência entre `.add()` e a escrita da função: a home deve tolerar sessão sem `ic_*` por alguns segundos sem renderizar estado falso.
- Exercícios que não resolvem em `exercises` precisam de comportamento explícito (log + sessão marcada, nunca IC parcial silencioso).
- Primeira dependência de backend do projeto — documentar deploy e rollback.

**Dependência de ordem.** Ver §Ordem de implementação.

**Correção de set/2026 — responsabilidade 1.** A redação original dizia lookup por `nome`
normalizado (Unicode + trim + lowercase), com a justificativa de que `exercise_id` legado era
não-confiável. O Bloco 1 é anterior a **D3.2** (Bloco 3), que inverteu o campo autoritativo:
`exercise_id` passou a ser a chave e `nome` virou snapshot de exibição. Transcrever a redação
original faria a Cloud Function nascer implementando a regra que D3.2 substituiu. Corrigido
em set/2026; ver o status em `momentum-arquitetura-estado.md`.

---

## D1.5 · Zero-state dedicado, com hero didático ancorado na prescrição

**Estado atual.** `dimPercentile()` retorna `0.5` com menos de 4 sessões; `dimTrend()` retorna `0` com menos de 8. Resultado: `dimEstado(0.5, 0)` = `'estavel'` nas três dimensões, e o hero renderiza a rota de "estável" com um número no meio da escala — **um valor exibido sem dado de origem**, violação direta do pilar de auditabilidade.

**Decisão.** Zero-state dedicado. A camada de intenção do hero renderiza normalmente (mesociclo, semana, foco declarado). A camada de sinal é **substituída**, não atenuada.

**Conteúdo do zero-state — direcionamento definido.** O hero de primeira-contato é **didático sobre a periodização prescrita**, não sobre desempenho inexistente. Ele antecipa o desenho do ciclo em vez de relatar o passado. Exemplos do tipo de leitura pretendida:
- elevação ondulada estimada nos exercícios de peitoral ao longo do mesociclo;
- volume metabólico acumulado projetado para o ciclo como um todo;
- distribuição dimensional planejada (onde o ciclo carrega Neural vs. Mecânica vs. Metabólica).

**Implicação estrutural.** Tudo isso é derivado de `prescricoes` (`alvo.carga_kg`, `.reps`, `series`, `tipo_serie`) cruzado com os coeficientes de `exercises`. Hoje **nenhuma tela lê `prescricoes`** — a estrutura existe, o caminho de leitura não. Este é o pré-requisito de D1.5 e conecta com D1.7 e com o Bloco 3.

**Threshold.** A camada de sinal não aparece até **4 sessões com dado dimensional válido**. Abaixo disso, home = intenção + check-in + entrada de treino.

**Pendente de você.** Copy final do zero-state e definição de quais das leituras didáticas entram na v1.

---

## D1.6 · Fim de mesociclo: estado mínimo na home, RN18 vira v1.1

**Estado atual.** `:1068` — `semanaAtual` é clampado por `Math.min(..., semanas_total)`. Passado o fim do ciclo, a home congela em "semana N de N" indefinidamente, com `diasRestantes` em 0. RN04 e RN18 estão classificadas como **v1** em `momentum-regras-negocio.md`, e nenhuma das duas existe no código.

**Decisão.** Versão mínima na v1: a home ganha um estado explícito **"mesociclo encerrado — aguardando novo ciclo"**. A aluna continua podendo treinar; as sessões param de contar para a aderência do ciclo encerrado. Sem tela de celebração, sem arquivamento automático.

**RN18 (tela de transição com resumo) → v1.1.** Razão: o resumo depende de evolução de CargaObjetiva, que depende de D1.4 estar rodando e estabilizado.

**Correção acoplada — `diasDecorr` tem duas semânticas.**
- `:1020` → dias de calendário desde `mesociclo_inicio`.
- `:1428` (`buildMesoDots`) → `sess.length`, contagem de sessões.
- `:1462` exibe `dia ${diasDecorr} de ${totalDias}`, misturando numerador de sessão com denominador de calendário.

Renomear para desambiguar (`diasDecorridos` vs. `sessoesRealizadas`) e corrigir o rótulo da `:1462`.

---

## D1.7 · `frequencia_semanal` em `prescricoes` como denominador de aderência

**Estado atual.** `FREQ` é montado por parse de texto livre de `anamnese.disponibilidade` via `DIAS_MAP`, e contém índices de dia da semana do JS (0=Dom…6=Sáb). O cálculo (`:1030`):

```js
for (let i = 0; i < diasDecorr; i++) {
  if (FREQ.includes(i % 7)) planejados++;
}
```

`i` conta dias desde `mesociclo_inicio`, então `i % 7` só coincide com o dia da semana real se o início cair num domingo. O mesmo arquivo faz certo trinta linhas depois (`:1104`, `FREQ.includes(dayDate.getDay())`). Se o parse falha, `FREQ` cai silenciosamente no default `[1,3,5]`.

**Decisão.** Campo `frequencia_semanal` (número) em `prescricoes`, escrito pelo PT. Aderência passa a ser `sessões da semana ÷ frequencia_semanal`, independente de qual dia.

**Razões.**
- Desacopla do calendário: a aluna não é penalizada por treinar terça em vez de segunda.
- Elimina o parse frágil de texto livre e o default silencioso.
- Move o denominador de um campo que registra **preferência declarada pela aluna** para um campo que registra **prescrição do PT** — auditável, com autor.

**Consequência.** `anamnese.disponibilidade` deixa de alimentar qualquer cálculo e volta a ser contexto de leitura humana.

**Fora de escopo v1 (decidido).** `dias_treino[]` (array explícito de dias) **não** entra agora. Ele é pré-requisito de **RN14 (lembrete de treino)**, que depende de o sistema saber que hoje é dia dela. Se RN14 entrar no lançamento, esta decisão precisa ser reaberta e `frequencia_semanal` vira derivado (`dias_treino.length`).

---

## Ordem de implementação

A sequência importa em dois pontos:

1. **D1.2 antes de D1.4.** A Cloud Function precisa nascer escrevendo e lendo ISO. Se entrar antes da migração de formato, cria uma terceira geração de dado.
2. **Leitura de `prescricoes` antes de D1.5 e D1.7.** Ambas consomem a coleção, e hoje não existe caminho de leitura no cliente. O contrato de leitura é tratado no Bloco 3 da revisão.

Sugestão de ordem:

```
1. D1.2  migração de formato de data + consolidação date/data
2. D1.3  inversão de ordenação de S.sessions + ajuste dos consumidores
3. D1.6  correção de diasDecorr (duas semânticas) + estado de fim de mesociclo
4. D1.4  Cloud Function onCreate
5. —     contrato de leitura de prescricoes (Bloco 3)
6. D1.7  frequencia_semanal
7. D1.5  zero-state didático
   D1.1  nenhuma ação (decisão de não fazer)
```

D1.3 e D1.6 são independentes entre si e de D1.2 — podem ir em paralelo.

---

## Pendências geradas por este bloco

| Item | Tipo | Bloqueia |
|---|---|---|
| Contrato de leitura de `prescricoes` no cliente | arquitetura | D1.5, D1.7, Bloco 3 |
| Copy final do zero-state didático | conteúdo | D1.5 |
| Definir quais leituras didáticas entram na v1 | produto | D1.5 |
| Comportamento para exercício que não resolve em `exercises` | infra | D1.4 |
| Destino do campo `date` após migração | schema | D1.2 |
| Deploy/rollback da primeira Cloud Function | infra | D1.4 |
