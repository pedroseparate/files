# Momentum · Contexto para Claude Code

Personal Training platform desenvolvida por João Pedro (PT + dev).
Este arquivo é lido automaticamente pelo Claude Code a cada sessão. Não remova.

---

## Quem é João Pedro

Personal Trainer com domínio fisiológico técnico fluente. Trabalha como PT e desenvolvedor simultaneamente. Comunica-se em português brasileiro, tom casual, respostas diretas. Explica o raciocínio fisiológico por trás de decisões de produto.

---

## Regras de ouro — comportamento obrigatório

1. **Nunca assuma o estado atual do sistema.** Antes de sugerir qualquer mudança, pergunte ou consulte a documentação. Assunções levam a retrabalho.
2. **Decisões arquiteturais fechadas estão em `momentum-arquitetura-estado.md`.** Não reproponha o que já está decidido sem justificativa fisiológica explícita. Para trabalho no app do aluno, a subseção relevante é **"Decisões v1 client-side (set/2026)"** — ela contém as decisões D1.x, D2.x e D3.x do lançamento.
3. **Design system não muda.** Cormorant Garamond + IBM Plex Mono + Bebas Neue, paleta gold/copper/night. Não proponha mudanças visuais fora dessa identidade.

---

## Documentação de referência — consulte antes de implementar

| Arquivo | Conteúdo |
|---------|----------|
| `momentum-arquitetura-estado.md` | Decisões fechadas, pendências, estado do projeto |
| `momentum-modelo-matematico.md` | Fórmulas completas, coeficientes, pendências de calibração |
| `momentum-regras-negocio.md` | 26 regras de negócio, estados, validações, chips automáticos |
| `momentum-schema-firestore.md` | Estrutura real das coleções, campo a campo, com divergências e campos legados mapeados |

---

## Estrutura da pasta

```
momentum-claude-code/
├── serviceAccountKey.json     ← NUNCA commitar · fica FORA do repo (o repo é files/)
├── package.json               ← firebase-admin ^13.8.0
├── backups/                   ← dumps do Firestore · fora do repo
├── files/                     ← ★ ESTE É O REPOSITÓRIO GIT (pedroseparate/files)
│   ├── CLAUDE.md                     ← este arquivo · versionado junto com o que ele descreve
│   ├── firebase.json                 ← Functions: source, runtime nodejs22
│   ├── functions/                    ← Cloud Functions · deploy roda a partir de files/
│   │   ├── functions_index.js        ← onSessionWrite: IC dimensional por sessão (D1.4 fase 1)
│   │   ├── index.js                  ← entry point (encadeia functions_index)
│   │   └── package.json              ← firebase-admin ^12.0.0 (diverge da raiz)
│   ├── docs/decisoes/                ← handoffs de decisão · registro histórico
│   ├── momentum-aluno.html           ← ★ APP PRINCIPAL — foco do MVP
│   ├── momentum-dashboard-v5.html    ← Dashboard PT — v2
│   ├── momentum-pt-dashboard.html    ← variante dashboard PT — v2
│   ├── login.html, index.html
│   ├── firebase-config.js
│   ├── momentum-arquitetura-estado.md
│   ├── momentum-modelo-matematico.md
│   ├── momentum-regras-negocio.md
│   └── DEPLOY-TUTORIAL.md
└── scripts utilitários (raiz):
    ├── fix_all.js             ← correção geral (duplicatas, datas, IDs)
    ├── fill_missing_sessions.js
    ├── add_tipo_serie_prescricoes.js
    ├── audit.js               ← auditoria do banco (6 checks)
    ├── fix_ic.js
    ├── fix_remaining.js
    ├── fix_prescricoes.js
    ├── seed_ic_planejado.js
    ├── import.js              ← popula exercises com doc id determinístico (.doc(id).set())
    └── reset_jacqueline.js    ← prescrição prospectiva da primeira aluna real
```

Versões antigas (v2, v3, v4, aluno3, _1, _2, _5) existem na pasta mas **não são a referência ativa**. Sempre confirme com João Pedro antes de editar qualquer versão não-canônica.

---

## Firestore — coleções (projeto: momentum-br)

| Coleção | Docs | Status | Descrição |
|---------|------|--------|-----------|
| `sessions` | **0** | ★ MVP ativo | Sessões executadas pelos alunos. **Esvaziada em set/2026** — as 355 sessões legadas foram apagadas para não conviverem com a escala nova de Metabólica (§2c). Backup em `backups/sessions-2026-09-19.json`, fora do repo. A primeira sessão da Jacqueline será a primeira do corpus. |
| `checkins` | **0** | ★ MVP ativo | Check-ins pré-treino. **Esvaziada em set/2026** junto com `sessions` — zero-state completo para o lançamento. Backup em `backups/`. Docs novos nascem em ISO com id determinístico `{student_id}_{data_iso}` (D2.3). |
| `exercises` | 85 | ★ MVP ativo | Banco de exercícios com coeficientes |
| `students` | 10 | ★ MVP ativo | Perfis de alunos. `scores.*`, `ritmo_estado` e `momentum_snapshot` foram **removidos de todos** em set/2026 — eram seed sem sessão por trás. Voltam com a Fase 2 de D1.4. |
| `prescricoes` | 10 | ★ MVP ativo | Origem única do treino do aluno (D3.1). 9 dos 10 docs foram gerados retroativamente a partir do histórico; só o da **Jacqueline** é prescrição prospectiva genuína. |
| `pt_interactions` | 241 | v2 / analytics | Tracking de cliques do PT no dashboard — só escrita, nunca leitura operacional |
| `academias` | 1 | v2 | Dados da academia/estúdio |

---

## Stack

- **Frontend:** Single-file HTML (sem framework JS), mobile-first 375–430px, bottom-nav
- **Banco:** Firebase Firestore, `onSnapshot()` para real-time
- **Admin scripts:** Node.js + `firebase-admin ^13.8.0` (auth via `serviceAccountKey.json`)
- **Cloud Functions:** `firebase-functions ^4.9`, Node 22
- **Hosting:** Firebase Hosting (`/files` como root)
- **Autenticação:** `serviceAccountKey.json` local — sem `.env`

---

## Gotchas técnicos do banco

- **`exercise_id` é o campo autoritativo de exercícios** (D3.2, set/2026). `nome` é gravado junto na sessão como snapshot de exibição, nunca como chave. Doc ids de `exercises` são slugs semânticas determinísticas (`import.js` usa `.doc(ex.id).set(ex)`). Sessões anteriores ao corte não existem mais — não há regime legado. `EX_NAME_MAP` e lookup por nome estão descontinuados no caminho de escrita.
- **Granularidade de `exercises` = granularidade do modelo.** Um doc por variação (`supino-reto-barra`, `supino-reto-halteres`, `supino-reto-maquina`) — CT, IM, DN, SV e FC diferem entre elas. Agrupamento vem do campo `pattern`, nunca do slug.
- **`mesociclo_inicio` deve ser explícito** no documento do aluno — nunca inferido de datas de sessões.
- **Aquecimento (`tipo: 'aquecimento'`)** armazenado mas excluído do cálculo de IC.

---

## Modelo matemático — dimensões

| Dimensão | Captura |
|----------|---------|
| Neural (N) | FC, falhas de rep, RIR |
| Mecânica (M) | Tensão mecânica: kg × reps × séries × IM × DN |
| Metabólica (Met) | TUT, descanso, cadência |

Regras críticas do modelo — ver detalhes em `momentum-modelo-matematico.md`:
- FC não entra em CargaNorm — apenas no componente Neural
- CT e SV somam no amplificador: `(1 + CT×0.05 + SV×explos×0.05)`
- RatioAdaptação sempre como tendência relativa ao histórico do aluno — nunca valor absoluto

---

## Design system (imutável)

| Elemento | Valor |
|---------|-------|
| Fonte display | Cormorant Garamond (serif, itálico) |
| Fonte mono | IBM Plex Mono |
| Fonte hero | Bebas Neue |
| Primária | `--gold: #c8a060` |
| Secundária | `--copper: #8a6030` |
| Background dark | `#0e0b08` |
| Background page | `#f5f0e6` |

---

## Foco atual — MVP

**`momentum-aluno.html`** é o único arquivo em desenvolvimento ativo. É a dashboard do aluno pós-login.

**Bottleneck imediato:** a *leitura* de `prescricoes` por `momentum-aluno.html` — não existe
hoje e é pré-requisito de lançamento (D3.1).

**Próxima prioridade após MVP:** Tela de Prescrição do PT (`momentum-dashboard-v5.html`) — a
*escrita*, que fecha o ciclo PT → Atleta → Banco.

---

## Contexto de lançamento — v1 (set/2026)

O app está sendo preparado para a **primeira aluna real**, Jacqueline. Isso muda como
tratar o banco:

- O doc de `prescricoes` da Jacqueline é o **único prospectivo** — escrito antes de
  qualquer execução (`reset_jacqueline.js`). Os outros nove foram gerados retroativamente
  por `add_tipo_serie_prescricoes.js`, inferindo prescrição a partir de sessões já
  executadas: são documentação do passado, não plano.
- Ela está em **estado zero** — sem histórico de sessões. Lógica que assume histórico denso
  (percentis, tendências, médias móveis) precisa de comportamento explícito para N=0.
- As sessões que ela executar são o **corpus de calibração** dos coeficientes ainda
  pendentes (`wN/wM/wMet`, IM em isolados). Dado incompleto ou contaminado nessa fase é
  caro de um jeito que não aparece na lista de tarefas.
- **Sem autenticação na v1** (D1.1) — decisão declarada para fase de teste com uma aluna.
  Gatilho de revisão: entrada da segunda aluna real.

---

## Git

- Mensagens de commit em português, imperativo, < 72 chars
- **Nunca commitar `serviceAccountKey.json`**
- Arquivos de chave (`*Key.json`, `*.env`) sempre no `.gitignore`

---

## Princípio estratégico

> "A tecnicidade do Momentum deve ser demonstravelmente real — cada output de prescrição deve ser auditável, com inputs e métricas contextuais visíveis."

Diferencia o Momentum de concorrentes que usam linguagem sofisticada mas números estáticos e não rastreáveis.
