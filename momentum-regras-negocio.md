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
Janela rolante de 4 semanas. Comparação S3–S4 vs S1–S2:
- Alta: S3–S4 supera S1–S2 em +10% ou mais
- Estável: variação dentro de ±10%
- Queda: −10% a −20% → alerta PT · −20%+ → alerta urgente + sugestão de deload

**Comportamento especial — DUP:** Ritmo não calculado globalmente. Sistema mantém Ritmos paralelos por tipo de sessão (força · hipertrofia · volume). Alerta só dispara quando a queda aparece em **todos** os tipos simultaneamente. Queda isolada num único tipo é visível no painel analítico mas não gera notificação.

PT pode visualizar três curvas: IC÷PSE_calc · IC÷PSE_relatada · ΔPSE ao longo do tempo.

### RN 21 · Dimensões por sessão e radar do aluno
Fórmula simplificada para radar agregado (calculado sobre o executado):
```
Neural_sessao    = Σ (CargaNorm_i × FC_i × DN_i / 10)
Mecânica_sessao  = Σ (CargaNorm_i × IM_i / 10)
Metabólica_sessao = Σ (CargaNorm_i × FTT_i × SV_i)
```
Radar: janela rolante de 4 semanas, reset no início do mesociclo.
> Esta fórmula simplificada é para o radar agregado. O Modelo Matemático §2 usa a fórmula completa (com CT, explos e FD) para ic_neural por exercício.

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

#### Chips que funcionam com dados existentes

| Chip | Condição | Mensagem |
|------|----------|----------|
| `fadiga_precoce` | PSE médio nos 2 primeiros exercícios > PSE médio nos 2 últimos + 1.5 | "⚠ fadiga precoce — PSE caiu {delta}pts entre início e fim" |
| `sobrecarga_pse` | 3+ exercícios com PSE ≥ 9 na primeira metade da sessão | "⚠ PSE elevado no início — {n} exercícios com PSE ≥ 9 na 1ª metade" |
| `pse_ic_divergência` | PSE esperada ≥ 7.5 com IC simulado abaixo da média histórica (últimas 8 sessões) −15% | "⚠ esforço esperado alto com IC abaixo do usual — sinal de fadiga" |

#### Chips que requerem prescrição com `r_alvo` e `pse_alvo` por série

Esses campos existem no schema mas estão **null em sessões legadas**. São preenchidos automaticamente quando a tela de prescrição (PT) estiver implementada. Sessões sem prescrição: chips silenciosos.

| Chip | Condição | Mensagem |
|------|----------|----------|
| `colapso_de_reps` | r < r_alvo × 0.75 em 2+ séries do mesmo exercício | "⚠ colapso de reps — {nome}: {r} de {r_alvo} em {n} séries" |
| `progressão_ok` | Todas as séries com r ≥ r_alvo e PSE ≤ pse_alvo + 1 | "✓ execução dentro do prescrito — candidato a progressão de carga" |

**Fundamentação do chip `fadiga_precoce`:** PSE alto no início consome reservas neural e metabólica — o aluno sente que treinou forte, mas o estímulo nos exercícios seguintes foi subótimo. É o custo oculto da ordem de exercícios inadequada ou chegada ao treino já fadigado.

---

### RN 27 · Detecção de tendências longitudinais (chips de série temporal)
Chips calculados sobre a janela histórica do aluno — **requerem mínimo de 3 sessões registradas.**

| Chip | Condição | Janela | Mensagem |
|------|----------|--------|----------|
| `delta_pse_crescente` | PSE relatada subindo em 3 sessões consecutivas com última ≥ 7.5 | 3 sessões | "⚠ delta_pse_crescente — PSE {s3}→{s2}→{s1} · fadiga acumulada silenciosa" |
| `ritmo_em_queda` | IC÷PSE médio das últimas 4 sessões inferior às 4 anteriores em −10%+ | 8 sessões | "⚠ ritmo_em_queda — IC÷PSE caiu {delta}% · considerar deload" |
| `ritmo_em_queda_leve` | Mesma lógica, queda entre −5% e −10% | 8 sessões | "⚠ ritmo_em_queda leve — IC÷PSE −{delta}% · monitorar" |

**Fundamentação do `delta_pse_crescente`:** ΔPSE crescendo positivamente ao longo das semanas = aluno relatando consistentemente mais pesado que o calculado. Pode anteceder uma queda no RatioAdaptação em 1–2 semanas — é um sinal precoce que o IC sozinho não detecta. Ver §5b do Modelo Matemático.

**Fundamentação do `ritmo_em_queda`:** Proxy do RitmoAdaptação (RN 20) operando com os dados disponíveis hoje. IC÷PSE é uma versão simplificada de CargaObjetiva÷PSE_ritmo. Quando a tela de prescrição estiver ativa e `duração_min` estiver no schema, substituir pelo RatioAdaptação formal.

> **Dependências de RN 27:**
> - `delta_pse_crescente` → requer campo `pse` por sessão (já existe)
> - `ritmo_em_queda` → requer campos `indice` e `pse` por sessão (já existem)
> - Versão completa de `ritmo_em_queda` → requer `duração_min` no schema (pendente — ver Modelo Matemático §pendências)

---

## 6 · Check-in Pré-treino e Ajuste por Prontidão (RN 28–29)

### RN 28 · Check-in pré-treino

**Fluxo:**
1. Ao tocar em "Iniciar treino", o sistema abre o check-in antes de qualquer coisa
2. Pergunta obrigatória: "Como você está se sentindo hoje?" — 3 botões grandes
   - 😴 Cansado · 😐 Normal · ⚡ Disposto
3. Aluno pode pular — sistema registra `disposicao: null` e `estado_prontidao: 5`
4. Após responder, sistema oferece aprofundamento opcional (3 sub-questionários):
   - **Nível de cansaço** (refina disposição em escala de 3 pontos)
   - **Sono da noite anterior** — Ruim / Normal / Bom
   - **Alimentação do dia** — Ruim / Normal / Boa
5. Sistema calcula `estado_prontidao` (1–10) — ver Modelo Matemático §6a
6. Check-in salvo na coleção `checkins` e vinculado à sessão via `checkin_id`

**Exibição ao aluno após check-in:**
- Estado de prontidão visualizado (barra ou score)
- Ajuste comunicado: "Seu treino de hoje foi ajustado para X% do volume"
- Só exibido se houver ajuste real (prontidão < 8)

**Um check-in por aluno por dia.** Se aluno já fez check-in hoje e iniciar outro treino, sistema reutiliza o check-in existente sem perguntar novamente.

### RN 29 · Ajuste automático de treino por prontidão

**Condição:** `estado_prontidao` calculado no check-in.

| Prontidão | Ajuste de volume | Ajuste de carga | Mensagem ao aluno |
|-----------|-----------------|-----------------|-------------------|
| 8–10 | 100% | 100% | "Você está no nível. Treino completo." |
| 6–7 | 90% | 100% | "Disposição boa. Volume levemente reduzido." |
| 4–5 | 75% | 90% | "Dia moderado. Sessão adaptada." |
| 2–3 | 60% | 85% | "Chegou cansado. Sessão leve — qualidade > quantidade." |
| 1 | 0% | 0% | "Repouso recomendado. Seu corpo pede recuperação." |

**O ajuste não é bloqueante** — aluno pode ignorar e treinar no volume completo. PT vê no dashboard se o aluno ignorou o ajuste sugerido.

**`ic_ajustado` vs `ic_executado`:** diferença entre o que foi sugerido e o que foi feito fica registrada na sessão. Alimenta os chips de divergência.

**PT pode desativar ajuste automático por aluno** — campo `auto_adjust: false` no perfil.

> **Dependências de RN 28–29:**
> - Check-in requer tela de check-in no app do aluno (CK3)
> - Ajuste automático requer `ic_planejado` na sessão — disponível quando tela de prescrição existir
> - Enquanto `ic_planejado` não existir, ajuste usa média histórica como referência

---

## 6 · Insight Engine — Slot do Hero (RN 27–38)

Motor de seleção do destaque visual do hero card. Mantém uma biblioteca de fatos celebráveis e sinais de atenção. A cada virada de semana (ou evento relevante), seleciona o fato/sinal mais pertinente via score composto.

Fórmulas matemáticas em **Modelo Matemático §6**.

### RN 27 · Acúmulo neural sustentado

- **Gatilho fisiológico:** sistema nervoso tolerando carga e recuperando entre sessões consecutivas — adaptação neural em fase produtiva.
- **Critérios:** `percentil_N ≥ 65` por `≥ 3 semanas consecutivas`, fora de deload.
- **Raridade:** Comum
- **Headline:** "Neural firme há 3 semanas"
- **Contexto exibido:** "Seu sistema nervoso está absorvendo bem a carga — esse é o sinal que sustenta progressão real"
- **Número do slot:** percentil_N atual

### RN 28 · Aderência ao plano ondulatório

- **Gatilho fisiológico:** aluno em DUP ou periodização assimétrica respeitando os tipos de sessão prescritos (volume vs intensidade) — não "puxando todo dia".
- **Critérios:** modelo de periodização em `dup` ou perfil assimétrico, tipo_serie executado conforme planejado em `≥ 80%` das sessões, `≥ 2 semanas`.
- **Raridade:** Contextual (só dispara para periodizações ondulatórias)
- **Headline:** "Plano ondulatório em dia"
- **Contexto exibido:** "Você está respeitando os dias certos de volume e intensidade — é assim que a ondulação rende"
- **Número do slot:** % de aderência ao tipo_serie

### RN 29 · Crescimento mecânico

- **Gatilho fisiológico:** progressão clássica — tensão mecânica subindo via aumento de Volume Load semanal.
- **Critérios:** `VolumeLoad_semanal` subindo `≥ 5%` em `3 semanas consecutivas`, fora de deload.
- **Raridade:** Comum
- **Headline:** "Volume crescendo há 3 semanas"
- **Contexto exibido:** "Carga total subindo de forma sustentada — o estímulo clássico de hipertrofia e força"
- **Número do slot:** delta % vs 3 semanas atrás

### RN 30 · Recuperação no deload

- **Gatilho fisiológico:** semana de deload cumprindo seu propósito — PSE caindo e sinais de fadiga normalizando.
- **Critérios:** fase = `deload`, `PSE_médio` caindo `≥ 1 ponto` vs semana anterior, FC pós-sessão menor que baseline do mesociclo.
- **Raridade:** Contextual (só em deload)
- **Headline:** "Deload em ação"
- **Contexto exibido:** "Esforço percebido e cardio voltando ao baseline — recuperação está acontecendo como planejado"
- **Número do slot:** delta de PSE médio

### RN 31 · Consolidação técnica

- **Gatilho fisiológico:** execução de qualidade — RIR controlado, cadência estável, baixa falha de rep mesmo sob carga real.
- **Critérios:** RIR planejado vs realizado dentro de `±1`, cadência dentro da tolerância prescrita, em `≥ 3 sessões consecutivas`.
- **Raridade:** Comum
- **Headline:** "Execução afiada"
- **Contexto exibido:** "Carga real com técnica precisa — você está consolidando padrão motor"
- **Número do slot:** % de séries dentro do prescrito

### RN 32 · Streak de aderência

- **Gatilho fisiológico:** consistência comportamental — frequência alta com sessões completas. O fator que mais move o resultado a longo prazo.
- **Critérios:** `≥ 7 dias` com sessões completas conforme plano (sem perdidas).
- **Raridade:** Comum
- **Headline:** "{n} dias seguidos"
- **Contexto exibido:** "Frequência sustentada — consistência é o multiplicador silencioso do treino"
- **Número do slot:** n de dias

### RN 33 · Percentil cruzando threshold

- **Gatilho fisiológico:** marco de progressão dimensional — cruzar 50 ou 75 pela primeira vez no mesociclo significa mudança qualitativa de patamar.
- **Critérios:** qualquer dimensão (N/M/Met) cruzando 50 ou 75 pela primeira vez no mesociclo atual.
- **Raridade:** Raro
- **Headline:** "Cruzou o p{threshold} em {dim}"
- **Contexto exibido:** "Primeira vez que sua {dim} entra nesse patamar nesse ciclo — patamar novo, não pico isolado"
- **Número do slot:** percentil da dimensão

### RN 34 · Resiliência à carga

- **Gatilho fisiológico:** mesma carga, custo menor — adaptação neural completa. O sistema absorveu o estímulo a ponto de torná-lo "barato".
- **Critérios:** sessão de alta intensidade (top set, ou dia de força em DUP) executada com PSE médio igual ou `< PSE médio` de sessões anteriores de mesma intensidade prescrita, na janela das últimas `4 sessões` do mesmo tipo.
- **Raridade:** Raro
- **Headline:** "Carga ficou mais leve"
- **Contexto exibido:** "Mesmo peso, esforço percebido caiu — adaptação neural completa nesse padrão"
- **Número do slot:** delta de PSE

### RN 35 · Equilíbrio dimensional

- **Gatilho fisiológico:** as três dimensões progredindo juntas — ausência de sobre-ênfase. Especialmente valioso para perfis de hipertrofia/recomp.
- **Critérios:** variância entre percentis N/M/Met `≤ 0.15` (em escala 0–1), `≥ 2 semanas`.
- **Raridade:** Contextual (mais relevante para hipertrofia/recomp; menos para força pura)
- **Headline:** "Três dimensões alinhadas"
- **Contexto exibido:** "Neural, mecânica e metabólica caminhando juntas — sem buracos de estímulo"
- **Número do slot:** variância dimensional

### RN 36 · Retorno de fadiga

- **Gatilho fisiológico:** auto-regulação funcionando — o aluno saiu de um estado de fadiga (baixo/sobrecarga) sem intervenção crítica, por recuperação ativa.
- **Critérios:** `ritmo_estado` anterior em `baixo` ou `sobrecarga`, atual em `estável` ou `alta`, sem deload formal no intervalo.
- **Raridade:** Raro
- **Headline:** "Voltou ao ritmo"
- **Contexto exibido:** "Depois de uma semana de fadiga, o sistema se reorganizou sozinho — sinal de boa reserva fisiológica"
- **Número do slot:** ritmo_estado atual (label)

### RN 37 · Sinais de atenção (fallback negativo)

Quando nenhum fato celebrável dispara **e** há sinal de atenção ativo, o hero entra em modo alerta.

| Sinal | Critério | Headline | Contexto |
|-------|----------|----------|----------|
| Ritmo em queda | `ritmo_estado = baixo` por `≥ 1 semana` | "Ritmo abaixo do normal" | "Algumas sessões com mais esforço relatado que o habitual — vale conversar com seu PT" |
| Sobrecarga | `ritmo_estado = sobrecarga` | "Carga acumulada" | "Sinais de fadiga acumulada — pode ser hora de uma semana mais leve" |
| Aderência caindo | aderência semanal `< 60%` por `2 semanas` | "Frequência abaixo do plano" | "Você está deixando treinos passar — quer ajustar o plano com seu PT?" |
| Divergência PSE/IC | chip `pse_ic_divergência` ativo em `≥ 2` sessões da semana | "Esforço alto com pouco volume" | "Você está sentindo mais carga do que o registrado mostra — sinal de fadiga subjetiva" |

Quando nenhum fato celebrável dispara **e** não há sinal de atenção, o hero exibe **estado neutro contextualizado pela fase do mesociclo**:

- Deload → "Semana de descarga — cargas mais leves, execução precisa"
- Acumulação → "Semana de acúmulo — volume é o protagonista"
- Intensificação → "Semana de intensificação — cargas próximas do limite"
- Realização/Pico → "Semana de realização — qualidade acima de quantidade"

### RN 38 · Seleção via score composto

Quando múltiplos fatos disparam simultaneamente, a headline é decidida por score composto:
Score(fato) = Relevância × wR + Raridade × wRA + Recency × wRE

Componentes em **Modelo Matemático §6**.

**Regra de anti-repetição:** se o fato foi headline nas últimas 2 semanas consecutivas, seu Recency vai a 0 nessa semana (excluindo-o de fato da disputa). Exceção: fatos de raridade "Raro" ignoram anti-repetição — quando disparam, vencem sempre.

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
| Chip pse_ic_divergência | PT | Dashboard | 26 |
| Chip delta_pse_crescente | PT | Dashboard | 27 |
| Chip ritmo_em_queda | PT | Push + Dashboard | 27 |
| Check-in realizado | PT | Dashboard (badge) | 28 |
| Check-in pulado | PT | Dashboard (badge) | 28 |
| Ajuste de treino por prontidão | Aluno | Tela check-in | 29 |
| Aluno ignorou ajuste sugerido | PT | Dashboard | 29 |
| Insight Engine — fato celebrável selecionado | Aluno | Hero card | 27–36 |
| Insight Engine — sinal de atenção | Aluno + PT | Hero + Push | 37 |
