// files/functions/functions_index.js
// Cloud Function: calcula ICs e chips ao salvar uma sessão
// Deploy: firebase deploy --only functions   (a partir de files/)
// Requer: plano Blaze + firebase-functions + firebase-admin

const functions = require('firebase-functions');
const admin = require('firebase-admin');
admin.initializeApp();
const db = admin.firestore();

// ═══════════════════════════════════════════════════════════════
// D1.4 · FASE 2 — scores.* e ritmo_estado no doc do aluno.
// Desligada deliberadamente até depois do lançamento. A decisão registrada
// em momentum-arquitetura-estado.md coloca a Fase 2 depois da Fase 1, e ela
// só passa a importar na 4ª sessão com dado dimensional, quando a camada de
// sinal do hero destrava (D1.5). Ligar exige também o índice composto
// (student_id + date) declarado em firestore.indexes.json, que não existe.
// ═══════════════════════════════════════════════════════════════
const FASE_2_ATIVA = false;

function r2(v) { return Math.round(v * 100) / 100; }

// ── Catálogo ───────────────────────────────────────────────────
// Indexado por doc id (D3.2 — exercise_id é autoritativo). O índice por nome
// existe apenas como caminho de compatibilidade com o corpus legado, onde
// 60% dos exercise_id não resolvem contra `exercises`.
let EX_CACHE = null;
async function getCatalogo() {
  if (EX_CACHE) return EX_CACHE;
  const snap = await db.collection('exercises').get();
  const byId = {}, byNome = {};
  snap.docs.forEach(d => {
    const e = d.data();
    byId[d.id] = e;
    const k = (e.name || e.nome || '').trim().toLowerCase();
    if (k) byNome[k] = d.id;
  });
  EX_CACHE = { byId, byNome };
  return EX_CACHE;
}

// Resolve a identidade do exercício. Sem fallback de coeficientes genéricos:
// número plausível sem origem é o oposto do pilar de auditabilidade.
function resolverExercicio(cat, ex) {
  const id = ex.exercise_id;
  if (id && cat.byId[id]) return { id, coefs: cat.byId[id], via: 'exercise_id' };

  // Compatibilidade legada: onde ambos os caminhos resolvem, eles concordam
  // em 633 de 633 casos — cair para o nome aqui não introduz ambiguidade.
  const porNome = cat.byNome[(ex.nome || '').trim().toLowerCase()];
  if (porNome) return { id: porNome, coefs: cat.byId[porNome], via: 'nome-legado' };

  return null;
}

// ── CargaNorm (modelo §1) ──────────────────────────────────────
// CargaNorm_i = Σ_j (kg_j × reps_j) sobre as séries registradas.
// Generalização exata de `kg × reps × séries`, que assumia implicitamente
// séries uniformes: no caso uniforme as duas formas são idênticas. Médias
// foram descartadas — kg e reps são anticorrelacionadas dentro de um
// exercício, então o produto das médias superestima sistematicamente
// (+27% em drop set), com viés correlacionado ao sinal medido.
function cargaNorm(ex) {
  const temSeries = Array.isArray(ex.series) && ex.series.length > 0;
  const temAchatado = ex.kg != null && ex.r != null && ex.s != null;

  // series[] é a fonte quando é o registro completo da execução. No corpus
  // legado, 176 de 1556 exercícios têm series[] truncado (menos entradas que
  // `s`) — ali os campos achatados são o registro mais completo, e somar as
  // séries parciais subcontaria o volume em até 75%.
  const seriesCompleta = temSeries && (!temAchatado || ex.series.length === ex.s);

  if (seriesCompleta) {
    const cn = ex.series.reduce((a, sr) => a + (sr.kg || 0) * (sr.r != null ? sr.r : (sr.reps || 0)), 0);
    return { cn: r2(cn), series_executadas: ex.series.length, forma: 'soma_series' };
  }
  if (temAchatado) {
    return { cn: r2(ex.kg * ex.r * ex.s), series_executadas: ex.s, forma: 'achatado' };
  }
  if (temSeries) {
    const cn = ex.series.reduce((a, sr) => a + (sr.kg || 0) * (sr.r != null ? sr.r : (sr.reps || 0)), 0);
    return { cn: r2(cn), series_executadas: ex.series.length, forma: 'soma_series_parcial' };
  }
  return null; // sem dado de execução: não inventar defaults
}

// FD usa o descanso executado quando existir; cai para o prescrito em
// `alvo.descanso_s` (D3.5). Ramificação explícita, não fallback silencioso.
// O cliente ainda não grava o descanso real — ver pendências.
function resolverDescanso(ex) {
  if (ex.descanso_s != null) return { descanso_s: ex.descanso_s, fonte: 'executado' };
  if (ex.alvo && ex.alvo.descanso_s != null) return { descanso_s: ex.alvo.descanso_s, fonte: 'prescrito' };
  return { descanso_s: 90, fonte: 'referencia' }; // 90s é a referência do modelo
}

// ── Componentes (modelo §2) ────────────────────────────────────
// FC entra só no Neural, nunca em CargaNorm.
// Metabólica segue §2c completo: CargaNorm × FTT × SV × FD.
// FTT = 1 enquanto cadência não é prescrita (decisão fechada).
function calcExIC(coefs, cn, descanso_s) {
  const exp = coefs.explos ? 1 : 0;
  const FTT = 1;
  const FD = descanso_s > 0 ? 90 / descanso_s : 1;
  return {
    ic_neural:     r2(cn * coefs.FC * coefs.DN * (1 + coefs.CT * 0.05 + coefs.SV * exp * 0.05)),
    ic_mecanica:   r2(cn * coefs.IM),
    ic_metabolica: r2(cn * FTT * coefs.SV * FD),
  };
}

// ── Pesos por tipo de sessão ───────────────────────────────────
// Mapa explícito. A versão anterior casava por regex no campo `tipo`, o que
// funcionava por acidente de nomenclatura: com D3.6 `tipo` grava slug, e
// 'lower-a' casava /lower/ por coincidência. Um slug como 'full-body-a' ou
// 'deload-1' não casaria nada e cairia no default em silêncio.
// Os valores reproduzem exatamente o comportamento anterior para todas as
// chaves conhecidas — nenhum número muda. Os pesos em si seguem pendentes de
// revisão fisiológica (wN/wM/wMet), o que não é escopo desta correção.
const PESOS_DEFAULT = [0.30, 0.40, 0.30];
const PESOS_POR_TIPO = {
  'upper-a': [0.30,0.45,0.25], 'upper-b': [0.30,0.45,0.25], 'upper-c': [0.30,0.45,0.25],
  'upper a': [0.30,0.45,0.25], 'upper b': [0.30,0.45,0.25],
  'upper a · deload': [0.30,0.45,0.25], 'upper b · deload': [0.30,0.45,0.25],
  'upper · hipertrofia': [0.30,0.45,0.25],
  'push': [0.30,0.45,0.25], 'push a': [0.30,0.45,0.25], 'push b': [0.30,0.45,0.25],
  'pull': [0.30,0.45,0.25], 'pull a': [0.30,0.45,0.25],

  'lower-a': [0.50,0.35,0.15], 'lower-b': [0.50,0.35,0.15], 'lower-c': [0.50,0.35,0.15],
  'lower a': [0.50,0.35,0.15], 'lower b': [0.50,0.35,0.15],
  'lower a · deload': [0.50,0.35,0.15], 'lower b · deload': [0.50,0.35,0.15],
  'lower a · pr agachamento': [0.50,0.35,0.15],
  'lower · força': [0.50,0.35,0.15], 'lower · volume': [0.50,0.35,0.15],
  'upper · força': [0.50,0.35,0.15], 'força': [0.50,0.35,0.15], 'técnica': [0.50,0.35,0.15],

  'full a': [0.25,0.40,0.35], 'full b': [0.25,0.40,0.35], 'full c': [0.25,0.40,0.35],
  'full body a': [0.25,0.40,0.35], 'full body b': [0.25,0.40,0.35], 'full body c': [0.25,0.40,0.35],
  'metabólico': [0.25,0.40,0.35],

  'legs': [0.30,0.40,0.30], 'volume': [0.30,0.40,0.30],
  'treino a': [0.30,0.40,0.30], 'treino b': [0.30,0.40,0.30], 'treino c': [0.30,0.40,0.30],
  'treino d': [0.30,0.40,0.30], 'treino e': [0.30,0.40,0.30],
};
function getWeights(tipo) {
  const k = (tipo || '').trim().toLowerCase();
  const p = PESOS_POR_TIPO[k];
  if (p) return { pesos: p, mapeado: true };
  return { pesos: PESOS_DEFAULT, mapeado: false };
}

// ── Chips ──────────────────────────────────────────────────────
async function calcChips(sess, exs) {
  const chips = [];

  const colapso = {};
  exs.forEach(ex => {
    (ex.series || []).forEach(sr => {
      if (sr.r_alvo && sr.r && sr.r < sr.r_alvo * 0.75) {
        const nome = (ex.nome || '?').split(' ')[0].toLowerCase();
        colapso[nome] = (colapso[nome] || 0) + 1;
      }
    });
  });
  Object.entries(colapso).forEach(([nome, n]) => {
    if (n >= 2) chips.push({ c: 'alert', short: `colapso ${nome}` });
  });

  // Bloco longitudinal: exige índice composto (student_id + tipo + date) que
  // não está declarado, então hoje sempre cai no catch. Ver pendências.
  try {
    const histSnap = await db.collection('sessions')
      .where('student_id', '==', sess.student_id)
      .where('tipo', '==', sess.tipo)
      .orderBy('date', 'desc')
      .limit(7)
      .get();
    const hist = histSnap.docs.map(d => ({ id: d.id, ...d.data() })).filter(s => s.id !== sess.id);
    if (hist.length >= 3) {
      const avgIC = hist.reduce((a, s) => a + (s.indice_carga || 0), 0) / hist.length;
      const avgPSE = hist.reduce((a, s) => a + (s.pse || 7), 0) / hist.length;
      const icAtual = sess.indice_carga || 0;
      const pseAtual = sess.pse || 7;
      if (icAtual >= avgIC && pseAtual <= avgPSE + 0.3)
        chips.push({ c: 'ok', short: 'adaptação positiva' });
      if (pseAtual >= 7.5 && icAtual < avgIC * 0.85)
        chips.push({ c: 'alert', short: 'esforço alto · IC abaixo do usual' });
    }
  } catch (e) { console.warn('chips longitudinal:', e.message); }

  return chips;
}

// ── Fase 2 (desligada) ─────────────────────────────────────────
function percentile(recent, hist) {
  if (!hist.length || !recent.length) return 5.0;
  const avg = recent.reduce((a, b) => a + b, 0) / recent.length;
  return r2(hist.filter(x => x <= avg).length / hist.length * 10);
}

async function recalcStudentScores(studentId) {
  const snap = await db.collection('sessions')
    .where('student_id', '==', studentId)
    .orderBy('date', 'asc')
    .get();
  const sessions = snap.docs.map(d => d.data());
  if (sessions.length < 4) return null;

  const allN = sessions.map(s => s.ic_neural || 0);
  const allM = sessions.map(s => s.ic_mecanica || 0);
  const allMet = sessions.map(s => s.ic_metabolica || 0);
  const allR = sessions.map(s => s.ratio_adaptacao || 0);
  const r4 = sessions.slice(-4);
  const p4 = sessions.length >= 8 ? sessions.slice(-8, -4) : sessions.slice(0, Math.max(sessions.length - 4, 1));

  const neural = percentile(r4.map(s => s.ic_neural || 0), allN);
  const mecanica = percentile(r4.map(s => s.ic_mecanica || 0), allM);
  const metabolica = percentile(r4.map(s => s.ic_metabolica || 0), allMet);
  const ritmo = percentile(r4.map(s => s.ratio_adaptacao || 0), allR);

  const avgRec = r4.reduce((a, s) => a + (s.ratio_adaptacao || 0), 0) / 4;
  const avgPrev = p4.reduce((a, s) => a + (s.ratio_adaptacao || 0), 0) / Math.max(p4.length, 1);
  const pct = (avgRec - avgPrev) / Math.max(avgPrev, 0.001);
  const ritmo_estado = pct >= 0.10 ? 'alta' : pct <= -0.20 ? 'sobrecarga' : pct <= -0.10 ? 'baixo' : 'estavel';
  const momentum = r2(Math.min(Math.max(ritmo * 0.40 + Math.min(r4.length / 4 * 7, 10) * 0.35 + 5 * 0.25, 0), 10));

  return {
    scores: { neural, mecanica, metabolica, tecnica: 5, ritmo, momentum },
    ritmo_estado,
    momentum_snapshot: {
      valor: momentum,
      data: sessions[sessions.length - 1].date || '',
      sessao_id: sessions[sessions.length - 1].id || '',
    },
  };
}

// ── Guard de loop ──────────────────────────────────────────────
// Projeta apenas os campos de ENTRADA — identidade e valores de execução.
// A versão anterior comparava o array `exercicios` inteiro, que a própria
// função muta ao anexar os ic_*, então a comparação nunca dava igual e o
// corpo rodava duas vezes por sessão. Esta projeção é estável sob a escrita.
function assinaturaEntrada(exercicios) {
  return JSON.stringify((exercicios || []).map(e => [
    e.exercise_id || e.nome || '',
    e.tipo || null,
    e.s != null ? e.s : null,
    e.r != null ? e.r : null,
    e.kg != null ? e.kg : null,
    e.descanso_s != null ? e.descanso_s : (e.alvo && e.alvo.descanso_s != null ? e.alvo.descanso_s : null),
    (e.series || []).map(sr => [sr.kg != null ? sr.kg : null, sr.r != null ? sr.r : (sr.reps != null ? sr.reps : null)]),
  ]));
}

exports.onSessionWrite = functions.firestore
  .document('sessions/{sessionId}')
  .onWrite(async (change, context) => {
    if (!change.after.exists) return null;
    const sess = { id: context.params.sessionId, ...change.after.data() };

    if (sess._recalculated && change.before.exists) {
      const before = change.before.data() || {};
      if (assinaturaEntrada(before.exercicios) === assinaturaEntrada(sess.exercicios)) return null;
    }

    const originais = sess.exercicios || [];
    if (!originais.length) return null;

    const cat = await getCatalogo();
    let tn = 0, tm = 0, tmet = 0;
    let seriesExecutadas = 0, seriesPrescritas = 0, prescritasConhecidas = true;
    const naoResolvidos = [];
    const semExecucao = [];
    let algumCalculado = false;

    // Preserva toda entrada no documento; anexa ic_* só às calculadas.
    // Aquecimento é armazenado mas fica fora do cálculo de IC (CLAUDE.md).
    const exsOut = originais.map(ex => {
      if (ex.tipo === 'aquecimento') return ex;
      if (!ex.nome && !ex.exercise_id) return ex;

      const res = resolverExercicio(cat, ex);
      if (!res) { naoResolvidos.push(ex.exercise_id || ex.nome); return ex; }

      const cn = cargaNorm(ex);
      if (!cn) { semExecucao.push(ex.exercise_id || ex.nome); return ex; }

      const { descanso_s } = resolverDescanso(ex);
      const ics = calcExIC(res.coefs, cn.cn, descanso_s);

      tn += ics.ic_neural; tm += ics.ic_mecanica; tmet += ics.ic_metabolica;
      seriesExecutadas += cn.series_executadas;
      if (ex.s != null) seriesPrescritas += ex.s; else prescritasConhecidas = false;
      algumCalculado = true;

      return {
        ...ex, ...ics,
        ic: r2(ics.ic_neural + ics.ic_mecanica + ics.ic_metabolica),
        series_executadas: cn.series_executadas,
      };
    });

    if (!algumCalculado) {
      console.error(`✗ ${sess.student_id} | ${sess.id} | nenhum exercício calculável` +
        ` | não resolvidos: [${naoResolvidos.join(', ')}] | sem execução: [${semExecucao.join(', ')}]`);
      await change.after.ref.set({
        ic_incompleto: true,
        ic_nao_resolvidos: naoResolvidos,
        ic_sem_execucao: semExecucao,
        _recalculated: true,
      }, { merge: true });
      return null;
    }

    const { pesos: [wN, wM, wMet], mapeado } = getWeights(sess.tipo || '');
    const ic_obj = r2(wN * tn + wM * tm + wMet * tmet);
    const soma = tn + tm + tmet || 1;
    const dims = { neural: tn, mecanica: tm, metabolica: tmet };
    const pse = sess.pse || 7;

    const update = {
      ic_neural: r2(tn), ic_mecanica: r2(tm), ic_metabolica: r2(tmet),
      indice_carga: ic_obj, ic_executado: ic_obj,
      n: r2(tn / soma), m: r2(tm / soma), met: r2(tmet / soma),
      dim_dominante: Object.keys(dims).reduce((a, b) => dims[a] > dims[b] ? a : b),
      ratio_adaptacao: r2(ic_obj / Math.max(pse, 0.1)),
      exercicios: exsOut,
      series_executadas: seriesExecutadas,
      series_prescritas: prescritasConhecidas ? seriesPrescritas : null,
      _recalculated: true,
    };

    // Visível, nunca silencioso.
    update.ic_incompleto = (naoResolvidos.length + semExecucao.length) > 0;
    update.ic_nao_resolvidos = naoResolvidos;
    update.ic_sem_execucao = semExecucao;
    update.pesos_mapeados = mapeado;

    if (!mapeado) {
      console.warn(`⚠ ${sess.id} | tipo "${sess.tipo}" fora de PESOS_POR_TIPO — usando default ${JSON.stringify(PESOS_DEFAULT)}`);
    }
    if (naoResolvidos.length) {
      console.warn(`⚠ ${sess.id} | sem identidade no catálogo: [${naoResolvidos.join(', ')}]`);
    }

    const chips = await calcChips({ ...sess, ...update }, exsOut);
    if (chips.length) update.chips = chips;

    await change.after.ref.set(update, { merge: true });

    if (FASE_2_ATIVA) {
      const scores = await recalcStudentScores(sess.student_id);
      if (scores) await db.collection('students').doc(sess.student_id).set(scores, { merge: true });
    }

    console.log(`✓ ${sess.student_id} | ${sess.id} | IC=${ic_obj} | chips=${chips.length}` +
      ` | séries=${seriesExecutadas} | incompleto=${update.ic_incompleto}`);
    return null;
  });
