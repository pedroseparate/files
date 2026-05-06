# Momentum · Regras de Negócio
**v0.1 · Mar 2026**

Define o comportamento do sistema em resposta a eventos — o que dispara, o que muda, quem é notificado. Complementa o modelo matemático e o mapa de entidades.

---

## 1 · Estados e Transições (RN 01–07)

### RN 01 · Divisão prioritária pulada
**Condição:** Divisão com `prioridade=alta` chega ao fim do microciclo sem sessão executada.
**Ação:** Divisão inserida no início do próximo microciclo como primeira divisão. Status → `pulada_reinserida`.
**Notificação PT:** "X pulou [Divisão A] — reinserida no início da semana seguinte."
> Prioridade definida pelo PT na criação do microciclo. Sistema sugere com base nos coeficientes da valência dominante.

### RN 02 · Divisão não prioritária pulada
**Condição:** Divisão com `prioridade=normal` ou `baixa` chega ao fim do microciclo sem sessão executada.
**Ação:** Status → `pulada_perdida`. Microciclo avança normalmente. Aderência recalculada.
**Notificação PT (push):** "X não realizou [Divisão C] nesta semana."

### RN 03 · Sessão abandonada no meio
**Comportamento:** Sair da tela ou fechar o app não encerra a sessão — continua em `em_andamento` com sinalização para retomar.
Séries já encerradas são imutáveis e computadas imediatamente.
**Timeout:** 10 minutos sem interação → status → `abandonada`. IC, dimensões e aderência calculados com o executado. Nada é apagado.
**Notificação PT (push):** "X não finalizou [Sessão Y] — Z de W exercícios registrados."
> Série encerrada = permanente, não editável pelo aluno. PT pode editar via RN 11 com log de alteração.

### RN 04 · Mesociclo encerrado
**Condição:** Último microciclo encerrado — todas as divisões executadas ou puladas.
**Ação:** Planilha → `arquivada`. Sistema compila resumo (volume total, PRs, RatioAdaptação médio, aderência). Aluno vê tela de transição. Fica sem planilha ativa até PT criar próximo.
**Notificações:** PT: prompt para criar próximo. Aluno: tela de celebração com resumo.

### RN 05 · Mesociclo encerrando em breve
**Condição:** Faltam 7 dias para o fim do mesociclo ativo.
**Ação:** Badge de aviso no card do aluno no painel do PT.
**Notificação PT (push):** "Mesociclo de X encerra em 7 dias — prepare o próximo."

### RN 06 · Exercício extra adicionado pelo aluno
**Condição:** Aluno adiciona exercício não prescrito durante a sessão.
**Ação:** `ExercícioExecutado` criado com `extra=true`. Entra no volume total da sessão mas **não na aderência**. Componentes calculados normalmente.
**Notificação PT (push):** "X adicionou [Exercício] fora da prescrição em [Divisão A]."
> Comportamento autônomo do aluno é sinal relevante — pode indicar objetivo específico, desequilíbrio percebido ou hábito a corrigir.

### RN 07 · Aluno sem treinar há X dias
**Condição:** Nenhuma sessão registrada nos últimos X dias. X configurável pelo PT por aluno (padrão: 5 dias).
**Ação:** Badge de alerta no card do aluno. Streak zerado se aplicável.
**Notificação PT (push):** "X não treina há X dias."

---

## 2 · Limites e Validações (RN 08–13)

### RN 08 · Carga prescrita acima do limite de segurança
**Limites por nível:**
- Iniciante → 85% 1RM
- Intermediário → 95% 1RM
- Avançado/Elite → 100% 1RM

**Ação:** Sistema bloqueia a criação da sessão e exibe modal de confirmação. PT precisa confirmar explicitamente. Confirmação registrada com timestamp.
> O bloqueio protege contra erros acidentais, não impede prescrição intencional. PT sempre tem a palavra final.

### RN 09 · Volume semanal acima do teto de overtraining
**Condição:** Soma de CargaObjetiva ultrapassa 120% da CargaObjetiva_alvo do microciclo (configurável pelo PT por aluno).
**Ação:** Alerta no painel do PT e no dashboard do aluno. **Não bloqueia — apenas sinaliza.**
> Atletas avançados em semanas de intensificação podem operar acima intencionalmente.

### RN 10 · Entrada absurda de carga pelo aluno
**Condição:** Aluno registra carga > 150% do 1RM estimado, ou acima de limite por grupo muscular.
**Ação:** Sistema rejeita o valor e exibe mensagem de erro. Valor não salvo.

### RN 11 · Edição de sessão executada pelo PT
**Ação:** Edição salva com `editado_por_pt=true` e timestamp. Todos os valores calculados são recalculados automaticamente (CargaObjetiva, CargaInterna, RatioAdaptação, aderência, records). Histórico de edição preservado. Aluno não é notificado da edição.

### RN 12 · Detecção de PR — confirmação dupla
**Condição:** Valor calculado de RM ou Componente supera o record atual no mesmo exercício.
**Ação:** Record criado com `status=pendente_1x`. Na próxima sessão do mesmo exercício, se valor superar novamente → `status=confirmado`. Record anterior só substituído após confirmação.
Estimativa cruzada ativa: melhora em NRM gera alerta de 1RM via Epley.
**Notificações ao confirmar:** Aluno: "🏆 Novo recorde confirmado." PT: "[Aluno] confirmou PR em [Exercício]."
> Regra de confirmação dupla **não** se aplica a: conquistas de iniciante, records de performance (tempo, reps, rounds) — esses confirmados imediatamente.

### RN 13 · Progressão semiautomática — gatilho e aprovação
**Condição:** PSE das últimas N sessões consecutivas do mesmo padrão de divisão ficou abaixo do threshold configurado (padrão: 6.0). N configurado pelo PT por microciclo.
**Ação:** Sistema cria entidade `Progressão` com carga sugerida calculada pelo tipo de progressão da planilha.

Status inicial depende da configuração do PT:
- `manual` → `pendente` — aguarda aprovação do PT
- `automático` → `aprovada` — aplica direto na próxima sessão

**Notificações (modo manual):** PT: "Progressão sugerida para X em [Divisão] — aguardando aprovação." Após aprovação, aluno: "Sua carga foi atualizada pelo seu PT."
> Aluno pode comentar na Progressão antes ou depois da aprovação. PT vê o comentário junto com o RatioAdaptação para decidir.

---

## 3 · Notificações (RN 14–18)

### RN 14 · Lembrete de treino
Push ao aluno quando divisão planejada para hoje não foi executada e horário preferido foi atingido. "Hoje é dia de [Push A] 💪 — sua sessão está pronta."
> Horário preferido configurável pelo aluno. PT pode desativar por aluno.

### RN 15 · Novo mesociclo disponível
Planilha anterior arquivada → nova ativada → push ao aluno. "Novo ciclo disponível — [Nome da Planilha]."

### RN 16 · Comentário do PT em progressão
PT adiciona comentário em `Progressão` → push ao aluno com preview.

### RN 17 · Canais e preferências de notificação
Canal principal: push. Canal secundário: painel interno (histórico permanente). PT configura preferências por tipo de evento.

### RN 18 · Tela de transição — fim de mesociclo
Aluno abre o app após mesociclo arquivado → tela de celebração com: sessões realizadas vs planejadas · PRs confirmados · evolução de CargaObjetiva (1º vs último microciclo) · RatioAdaptação médio · streak máximo. Aluno pode compartilhar o resumo.

---

## 4 · Cálculo e Adaptação (RN 19–22)

### RN 19 · Cálculo do Índice de Carga
Ver fórmula completa em **Modelo Matemático §∑**.
- Séries de aquecimento não entram — só séries de trabalho
- Exercícios com `explos=true` não recebem multiplicador extra — SV alto já reflete o custo
- IC acumulado semanal calculado na hora de exibir — não armazenado separadamente
- Diferença `ic_planejado` vs `ic_executado` visível no painel do PT

### RN 20 · Ritmo de Adaptação
```
Ritmo = CargaObjetiva ÷ PSE_ritmo
```
Janela rolante de 4 semanas. Comparação metade recente vs metade antiga das sessões válidas.

**Estados (nomenclatura unificada em todo o sistema):**
- `alta`: delta ≥ +10% → corpo adaptado, candidato a progressão
- `estavel`: delta −10% a +10% → dentro do esperado
- `baixo`: delta −20% a −10% → alerta PT, possível fadiga
- `sobrecarga`: delta < −20% → alerta urgente, sugestão de deload

> **Importante:** `PSE_ritmo` (blend de PSE_calc e PSE_relatada, com α por nível) é obrigatório. Uso de `pse` cru é incorreto — ver Modelo Matemático §5b.

**Adapter de periodização — o ritmo adapta a janela de comparação ao modelo:**

| Modelo | Comportamento |
|--------|--------------|
| **Linear** | Global — todas as sessões, sem filtro |
| **Block** | Compara dentro da fase atual. Queda de IC na transição Acum→Int é esperada e NÃO é queda de ritmo |
| **DUP** | Ritmos paralelos por tipo_sessao. Alerta global só se TODOS os tipos em queda simultaneamente |
| **Conjugado** | Ritmo por exercício principal. Progressão é por exercício, não por sessão |
| **Assimétrico** | Ritmo por divisão (A/B/C/D/E). Compara cada dia consigo mesmo |

**Campo:** `modelo_periodizacao` no student doc. Fallback: inferido do nome do mesociclo. Default: `linear`.

PT pode visualizar três curvas: IC÷PSE_calc · IC÷PSE_relatada · ΔPSE ao longo do tempo.

### RN 21 · Dimensões por sessão e radar do aluno
**Fórmula única** — mesma para IC por exercício, soma da sessão, e radar. Ver Modelo Matemático §2.
```
Neural_sessao     = Σ (CargaNorm_i × FC_i × DN_i × (1 + CT_i×0.05 + SV_i×explos_i×0.05))
Mecânica_sessao   = Σ (CargaNorm_i × IM_i)
Metabólica_sessao = Σ (CargaNorm_i × FTT_i × SV_i × FD_i)
```
Radar do aluno: normaliza pela soma total (Neural/soma, Mecânica/soma, Metabólica/soma) — proporção, não valor absoluto.

> **Fórmulas "simplificadas" foram eliminadas.** A diferença entre IC detalhado e radar é apenas a camada de apresentação (absoluto vs proporção).

### RN 21b · Scores do aluno (0–10)
Scores são **computados dinamicamente** a partir dos dados de sessão. Nunca hardcoded.
```
Score(dimensão) = percentil_rolling(últimas 4 sessões no histórico total) × 10
```
Score de Momentum = média ponderada: 0.25×Neural + 0.30×Mecânica + 0.25×Metabólica + 0.20×Ritmo.

Ver Modelo Matemático §7 para tabela completa.

### RN 22 · Competência Técnica — propriedade do exercício
CT é fixo no banco — propriedade do movimento, não do aluno. Score de Técnica no radar reflete a composição dos exercícios treinados. CT não é modificável por PT ou aluno.

---

## 5 · Progressão e PSE (RN 23–26)

### RN 23 · Modelos de progressão intra-mesociclo
Hierarquia: modelo definido na sessão (padrão), sobrescrito por exercício individual via campo `modelo` na prescrição. Quando nulo, herda o modelo da sessão.

| Modelo | Referência | Observação |
|--------|-----------|------------|
| Linear | Sessão anterior do mesmo exercício | Avança quando aluno completa o prescrito |
| Block | Sessão equivalente da fase anterior | Fases: Acumulação → Intensificação → Realização |
| DUP | Mesma sessão da semana anterior | Ritmo calculado por tipo separadamente |
| Conjugado | Por exercício, não por padrão de movimento | PR e RM por exercício |

Semana de deload marcada na criação da planilha. Sistema não a usa como referência e não dispara alerta de queda.

Estrutura de dados — prescrição de exercício:
```json
{
  "exercise_id": "string",
  "modelo": null | "linear" | "block" | "dup" | "conjugado",
  "tipo_sessao": null | "forca" | "hipertrofia" | "volume",
  "series": [{ "numero", "reps_alvo", "carga_alvo", "tipo", "zona" }]
}
```

### RN 24 · Interpretação dimensional por nível do aluno
- Iniciante/Intermediário: variações dimensionais lidas como absolutas
- Avançado: sistema considera o contexto do modelo de progressão ao interpretar variações — evita falsos alertas

Nível atribuído manualmente pelo PT. **Não existe promoção automática.**

### RN 25 · Sistema PSE — série, sessão e percepção
PSE capturado por série na tela de execução — permanente e base de todos os cálculos.

Ver fórmulas completas em **Modelo Matemático §5b** (PSE_calc, PSE_relatada, PSE_ritmo, ΔPSE).

**ΔPSE crescendo positivamente ao longo das semanas** = aluno relatando consistentemente mais pesado que o calculado → sinal de acúmulo de fadiga que o IC sozinho não detecta. Pode aparecer antes de uma queda no Ritmo de Adaptação.

### RN 26 · Detecção automática de padrões na sessão
Chips automáticos por sessão no PT Dashboard — **nenhum campo extra precisa ser preenchido.**

| Chip | Condição | Mensagem |
|------|----------|----------|
| `fadiga_precoce` | PSE médio nos 2 primeiros exercícios > PSE médio nos 2 últimos + 1.5 | "⚠ fadiga precoce — PSE caiu {delta}pts entre início e fim" |
| `colapso_de_reps` | r < r_alvo × 0.75 em 2+ séries do mesmo exercício | "⚠ colapso de reps — {nome}: {r} de {r_alvo} em {n} séries" |
| `sobrecarga_pse` | 3+ exercícios com PSE ≥ 9 na primeira metade da sessão | "⚠ PSE elevado no início — {n} exercícios com PSE ≥ 9 na 1ª metade" |
| `progressão_ok` | Todas as séries com r ≥ r_alvo e PSE ≤ pse_alvo + 1 | "✓ execução dentro do prescrito — candidato a progressão de carga" |
| `pse_ic_divergência` | PSE ≥ 9 com IC abaixo da média histórica −15% para aquele tipo | "⚠ esforço percebido alto com volume abaixo do usual — sinal de fadiga" |

> `colapso_de_reps` e `progressão_ok` requerem `r_alvo` e `pse_alvo` por série — campo existe no schema, null nas sessões legacy.

**Fundamentação do chip `fadiga_precoce`:** PSE alto no início consome reservas neural e metabólica — o aluno sente que treinou forte, mas o estímulo nos exercícios seguintes foi subótimo. É o custo oculto da ordem de exercícios inadequada ou chegada ao treino já fadigado.

---

## ∑ · Tabela Consolidada de Eventos

| Evento | Destinatário | Canal | RN |
|--------|-------------|-------|----|
| Divisão prioritária pulada | PT | Push | 01 |
| Divisão não prioritária pulada | PT | Push | 02 |
| Sessão abandonada | PT | Push | 03 |
| Mesociclo encerrado | PT + Aluno | Push + Tela | 04 |
| Mesociclo encerrando (7 dias) | PT | Push + Badge | 05 |
| Exercício extra adicionado | PT | Push | 06 |
| Aluno sem treinar | PT | Push + Badge | 07 |
| Carga acima do limite | PT | Modal bloqueio | 08 |
| Volume acima do teto | PT + Aluno | Alerta painel | 09 |
| Entrada absurda de carga | Aluno | Erro inline | 10 |
| PR confirmado | PT + Aluno | Push | 12 |
| Progressão sugerida (manual) | PT + Aluno | Push | 13 |
| Lembrete de treino | Aluno | Push | 14 |
| Novo mesociclo ativo | Aluno | Push | 15 |
| Comentário PT em progressão | Aluno | Push | 16 |
| Fim de mesociclo (resumo) | Aluno | Tela transição | 18 |
| Ritmo em queda crítica | PT | Push urgente | 20 |
| Chip fadiga precoce | PT | Dashboard | 26 |
| Chip colapso de reps | PT | Dashboard | 26 |
| Chip progressão ok | PT | Dashboard | 26 |
