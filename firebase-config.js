// Momentum — Firebase Config (compat, sem módulos ES)
// Deixe em branco por enquanto — dashboard funciona sem Firebase
window.db   = null;
window.auth = null;

function authSignIn(e,p){ return Promise.reject({code:'auth/not-configured'}); }
function authSignOut(){ return Promise.resolve(); }
function onAuthReady(cb){ cb(null); }
function isAdmin(){ return false; }
