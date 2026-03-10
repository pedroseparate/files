// MOMENTUM — Firebase Config
// compat SDK (sem import/export — funciona direto no browser)

const FIREBASE_CONFIG = {
  apiKey:            "AIzaSyAYwneFYZ7uEn-vKzcCSPQ10oprJ0adGLs",
  authDomain:        "momentum-br.firebaseapp.com",
  projectId:         "momentum-br",
  storageBucket:     "momentum-br.firebasestorage.app",
  messagingSenderId: "942527884359",
  appId:             "1:942527884359:web:eb926e57ccfe40c61c5562"
};

(function() {
  if(typeof firebase === 'undefined') {
    console.warn('[Momentum] Firebase SDK não carregado.');
    window.db = null; window.auth = null;
    return;
  }
  try {
    firebase.initializeApp(FIREBASE_CONFIG);
    window.db   = firebase.firestore();
    window.auth = firebase.auth();
    console.log('[Momentum] Firebase conectado ✓');
  } catch(e) {
    console.warn('[Momentum] Firebase init falhou:', e.message);
    window.db = null; window.auth = null;
  }
})();

function authSignIn(email, password) {
  if(!window.auth) return Promise.reject({code:'auth/not-configured'});
  return auth.signInWithEmailAndPassword(email, password);
}
function authSignOut() {
  if(!window.auth) return Promise.resolve();
  return auth.signOut();
}
function onAuthReady(cb) {
  if(!window.auth) { cb(null); return; }
  auth.onAuthStateChanged(cb);
}
