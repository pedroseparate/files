// momentum-cloud-functions/index.js
// Cloud Function: calcula ICs, chips e scores ao salvar uma sessão
// Deploy: firebase deploy --only functions
// Requer: plano Blaze + firebase-functions + firebase-admin

const functions = require('firebase-functions');
const admin = require('firebase-admin');
admin.initializeApp();
const db = admin.firestore();

let EX_CACHE = null;
async function getExerciseCoefs() {
  if (EX_CACHE) return EX_CACHE;
  const snap = await db.collection('exercises').get();
  EX_CACHE = {};
  snap.docs.forEach(d => {
    const e = d.data();
    EX_CACHE[(e.name||e.nome||'').trim().toLowerCase()] = e;
  });
  return EX_CACHE;
}

function getCoef(coefs, nome) {
  return coefs[(nome||'').trim().toLowerCase()] ||
    { CT:4, IM:5, DN:5, SV:3, FC:0.6, explos:false };
}

function r2(v) { return Math.round(v * 100) / 100; }

function calcExIC(coefs, nome, s, r, kg, descanso_s = 90) {
  const c = getCoef(coefs, nome);
  const cn = kg * r * s;
  const exp = c.explos ? 1 : 0;
  const FD  = descanso_s > 0 ? 90 / descanso_s : 1;
  return {
    ic_neural:     r2(cn * c.FC * c.DN * (1 + c.CT*0.05 + c.SV*exp*0.05)),
    ic_mecanica:   r2(cn * c.IM),
    ic_metabolica: r2(cn * FD),  // Metabólica = CargaNorm × FTT × FD (FTT=1 quando cadência não prescrita)
  };
}

function getWeights(tipo) {
  const t = (tipo||'').toLowerCase();
  if (/força|forca|lower|neural|dup|powerlifting|técnica/.test(t)) return [0.50,0.35,0.15];
  if (/upper|hipertrofia|ppl|push|pull/.test(t))                   return [0.30,0.45,0.25];
  if (/full|funcional|reab|metabólico/.test(t))                    return [0.25,0.40,0.35];
  return [0.30,0.40,0.30];
}

async function calcChips(sess, exs) {
  const chips = [];

  // colapso_de_reps
  const colapso = {};
  exs.forEach(ex => {
    (ex.series||[]).forEach(sr => {
      if(sr.r_alvo && sr.r && sr.r < sr.r_alvo * 0.75) {
        const nome = (ex.nome||'?').split(' ')[0].toLowerCase();
        colapso[nome] = (colapso[nome]||0) + 1;
      }
    });
  });
  Object.entries(colapso).forEach(([nome, n]) => {
    if(n >= 2) chips.push({c:'alert', short:`colapso ${nome}`});
  });

  // adaptacao_positiva e pse_ic_divergencia (longitudinal)
  try {
    const histSnap = await db.collection('sessions')
      .where('student_id','==', sess.student_id)
      .where('tipo','==', sess.tipo)
      .orderBy('date','desc')
      .limit(7)
      .get();
    const hist = histSnap.docs.map(d=>({id:d.id,...d.data()})).filter(s=>s.id !== sess.id);
    if(hist.length >= 3) {
      const avgIC  = hist.reduce((a,s)=>a+(s.indice_carga||0),0)/hist.length;
      const avgPSE = hist.reduce((a,s)=>a+(s.pse||7),0)/hist.length;
      const icAtual  = sess.indice_carga||0;
      const pseAtual = sess.pse||7;
      if(icAtual >= avgIC && pseAtual <= avgPSE + 0.3)
        chips.push({c:'ok', short:'adaptação positiva'});
      if(pseAtual >= 7.5 && icAtual < avgIC * 0.85)
        chips.push({c:'alert', short:'esforço alto · IC abaixo do usual'});
    }
  } catch(e) { console.warn('chips longitudinal:', e.message); }

  return chips;
}

function percentile(recent, hist) {
  if(!hist.length || !recent.length) return 5.0;
  const avg = recent.reduce((a,b)=>a+b,0)/recent.length;
  return r2(hist.filter(x=>x<=avg).length/hist.length*10);
}

async function recalcStudentScores(studentId) {
  const snap = await db.collection('sessions')
    .where('student_id','==',studentId)
    .orderBy('date','asc')
    .get();
  const sessions = snap.docs.map(d=>d.data());
  if(sessions.length < 4) return null;

  const allN = sessions.map(s=>s.ic_neural||0);
  const allM = sessions.map(s=>s.ic_mecanica||0);
  const allMet = sessions.map(s=>s.ic_metabolica||0);
  const allR = sessions.map(s=>s.ratio_adaptacao||0);
  const r4  = sessions.slice(-4);
  const p4  = sessions.length>=8 ? sessions.slice(-8,-4) : sessions.slice(0,Math.max(sessions.length-4,1));

  const neural     = percentile(r4.map(s=>s.ic_neural||0), allN);
  const mecanica   = percentile(r4.map(s=>s.ic_mecanica||0), allM);
  const metabolica = percentile(r4.map(s=>s.ic_metabolica||0), allMet);
  const ritmo      = percentile(r4.map(s=>s.ratio_adaptacao||0), allR);

  const avgRec  = r4.reduce((a,s)=>a+(s.ratio_adaptacao||0),0)/4;
  const avgPrev = p4.reduce((a,s)=>a+(s.ratio_adaptacao||0),0)/Math.max(p4.length,1);
  const pct     = (avgRec-avgPrev)/Math.max(avgPrev,0.001);
  const ritmo_estado = pct>=0.10?'alta':pct<=-0.20?'sobrecarga':pct<=-0.10?'baixo':'estavel';
  const momentum = r2(Math.min(Math.max(ritmo*0.40+Math.min(r4.length/4*7,10)*0.35+5*0.25,0),10));

  return {
    scores: { neural, mecanica, metabolica, tecnica:5, ritmo, momentum },
    ritmo_estado,
    momentum_snapshot: {
      valor: momentum,
      data: sessions[sessions.length-1].date||'',
      sessao_id: sessions[sessions.length-1].id||'',
    },
  };
}

exports.onSessionWrite = functions.firestore
  .document('sessions/{sessionId}')
  .onWrite(async (change, context) => {
    if(!change.after.exists) return null;
    const sess = { id: context.params.sessionId, ...change.after.data() };

    // Evita loop: se já recalculado e exercícios não mudaram, pula
    if(sess._recalculated && change.before.exists) {
      const before = change.before.data()||{};
      if(JSON.stringify(before.exercicios) === JSON.stringify(sess.exercicios)) return null;
    }

    const exs = (sess.exercicios||[]).filter(e=>e.nome && e.tipo !== 'aquecimento');
    if(!exs.length) return null;

    const coefs = await getExerciseCoefs();
    let tn=0, tm=0, tmet=0;

    const exsCalc = exs.map(ex => {
      const ics = calcExIC(coefs, ex.nome, ex.s||3, ex.r||10, ex.kg||0, ex.descanso_s||90);
      tn+=ics.ic_neural; tm+=ics.ic_mecanica; tmet+=ics.ic_metabolica;
      return {...ex, ...ics, ic: r2(ics.ic_neural+ics.ic_mecanica+ics.ic_metabolica)};
    });

    const [wN,wM,wMet] = getWeights(sess.tipo||'');
    const ic_obj = r2(wN*tn+wM*tm+wMet*tmet);
    const soma = tn+tm+tmet||1;
    const dims = {neural:tn, mecanica:tm, metabolica:tmet};
    const pse  = sess.pse||7;

    const update = {
      ic_neural:r2(tn), ic_mecanica:r2(tm), ic_metabolica:r2(tmet),
      indice_carga:ic_obj, ic_executado:ic_obj,
      n:r2(tn/soma), m:r2(tm/soma), met:r2(tmet/soma),
      dim_dominante: Object.keys(dims).reduce((a,b)=>dims[a]>dims[b]?a:b),
      ratio_adaptacao: r2(ic_obj/Math.max(pse,0.1)),
      exercicios: exsCalc,
      _recalculated: true,
    };

    const chips = await calcChips({...sess,...update}, exsCalc);
    if(chips.length) update.chips = chips;

    await change.after.ref.set(update, {merge:true});

    const scores = await recalcStudentScores(sess.student_id);
    if(scores) await db.collection('students').doc(sess.student_id).set(scores, {merge:true});

    console.log(`✓ ${sess.student_id} | ${sess.id} | IC=${ic_obj} | chips=${chips.length}`);
    return null;
  });
