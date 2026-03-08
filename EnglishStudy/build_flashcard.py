import json, os

BASE = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE, 'flashcard_data.json'), encoding='utf-8') as f:
    data = json.load(f)

json_str = json.dumps(data, ensure_ascii=False)

html = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>英単語フラッシュカード</title>
<style>
:root {
  --primary: #1a5276;
  --primary-light: #2980b9;
  --accent: #e67e22;
  --bg: #f0f4f8;
  --card-bg: #ffffff;
  --text: #2c3e50;
  --text-light: #7f8c8d;
  --border: #dcdde1;
  --known: #27ae60;
  --learning: #f39c12;
  --unknown: #95a5a6;
  --new: #3498db;
}
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:'Segoe UI','Hiragino Kaku Gothic ProN',sans-serif; background:var(--bg); color:var(--text); min-height:100vh; }

header {
  background:linear-gradient(135deg,var(--primary),var(--primary-light));
  color:white; padding:18px; text-align:center;
  box-shadow:0 2px 10px rgba(0,0,0,.15);
}
header h1 { font-size:1.5em; }
header p { font-size:.8em; opacity:.85; margin-top:4px; }

.nav {
  display:flex; justify-content:center; gap:6px; padding:12px;
  flex-wrap:wrap; background:white; border-bottom:1px solid var(--border);
}
.nav button {
  padding:8px 16px; border:2px solid var(--primary); background:white;
  color:var(--primary); border-radius:20px; cursor:pointer; font-size:.85em;
  font-weight:600; transition:all .2s;
}
.nav button:hover,.nav button.active { background:var(--primary); color:white; }

.container { max-width:800px; margin:0 auto; padding:16px; }
.section { display:none; }
.section.active { display:block; }

/* Dashboard */
.stats-grid {
  display:grid; grid-template-columns:repeat(auto-fit,minmax(140px,1fr));
  gap:12px; margin:16px 0;
}
.stat-card {
  background:white; border-radius:12px; padding:16px; text-align:center;
  box-shadow:0 2px 8px rgba(0,0,0,.08);
}
.stat-card .num { font-size:2em; font-weight:700; }
.stat-card .label { font-size:.8em; color:var(--text-light); margin-top:4px; }
.stat-card.known .num { color:var(--known); }
.stat-card.learning .num { color:var(--learning); }
.stat-card.unknown .num { color:var(--unknown); }
.stat-card.total .num { color:var(--primary); }

.progress-bar-container {
  background:#e0e0e0; border-radius:10px; height:24px; margin:16px 0;
  overflow:hidden; display:flex;
}
.progress-bar-container .seg-known { background:var(--known); height:100%; transition:width .3s; }
.progress-bar-container .seg-learning { background:var(--learning); height:100%; transition:width .3s; }

.source-stats { margin:16px 0; }
.source-row {
  display:flex; align-items:center; gap:10px; padding:10px 12px;
  background:white; border-radius:8px; margin:6px 0;
  box-shadow:0 1px 4px rgba(0,0,0,.06);
}
.source-row .name { font-weight:600; min-width:80px; }
.source-row .bar-bg { flex:1; background:#e0e0e0; border-radius:6px; height:16px; overflow:hidden; display:flex; }
.source-row .bar-bg div { height:100%; transition:width .3s; }
.source-row .pct { font-size:.85em; min-width:50px; text-align:right; }

/* Filters */
.filter-bar {
  display:flex; flex-wrap:wrap; gap:8px; margin:12px 0; align-items:center;
}
.filter-bar label { font-weight:600; font-size:.85em; }
.filter-bar select, .filter-bar input {
  padding:6px 10px; border:1px solid var(--border); border-radius:8px;
  font-size:.85em;
}
.filter-bar input[type=text] { flex:1; min-width:120px; }

/* Flashcard */
.card-wrapper {
  perspective:1000px; margin:20px auto; max-width:500px; height:280px; cursor:pointer;
}
.card-inner {
  position:relative; width:100%; height:100%; transition:transform .5s;
  transform-style:preserve-3d;
}
.card-wrapper.flipped .card-inner { transform:rotateY(180deg); }
.card-front,.card-back {
  position:absolute; width:100%; height:100%; backface-visibility:hidden;
  border-radius:16px; display:flex; flex-direction:column;
  align-items:center; justify-content:center; padding:24px;
  box-shadow:0 4px 20px rgba(0,0,0,.1);
}
.card-front {
  background:linear-gradient(135deg,#fff,#f8f9fa); border:2px solid var(--border);
}
.card-back {
  background:linear-gradient(135deg,var(--primary),var(--primary-light));
  color:white; transform:rotateY(180deg);
}
.card-word { font-size:2.2em; font-weight:700; }
.card-source {
  position:absolute; top:12px; right:16px; font-size:.7em; padding:3px 10px;
  border-radius:12px; background:var(--primary-light); color:white;
}
.card-front .card-source { background:#eee; color:var(--text-light); }
.card-def { font-size:1.1em; text-align:center; line-height:1.6; }
.card-jp { font-size:.95em; margin-top:8px; opacity:.9; }
.card-pos { font-size:.8em; margin-top:6px; opacity:.8; font-style:italic; }
.card-status-badge {
  position:absolute; top:12px; left:16px; font-size:.7em; padding:3px 10px;
  border-radius:12px; font-weight:600;
}
.badge-known { background:var(--known); color:white; }
.badge-learning { background:var(--learning); color:white; }
.badge-new { background:var(--new); color:white; }

.card-nav {
  display:flex; justify-content:center; gap:12px; margin:16px 0;
}
.card-nav button {
  padding:10px 20px; border:none; border-radius:10px; cursor:pointer;
  font-size:.9em; font-weight:600; transition:all .2s;
}
.btn-prev,.btn-next { background:#ecf0f1; color:var(--text); }
.btn-prev:hover,.btn-next:hover { background:#d5dbdb; }

.status-buttons {
  display:flex; justify-content:center; gap:10px; margin:12px 0;
}
.status-buttons button {
  padding:10px 18px; border:none; border-radius:10px; cursor:pointer;
  font-weight:600; font-size:.85em; color:white; transition:all .2s;
}
.btn-known { background:var(--known); }
.btn-learning { background:var(--learning); }
.btn-unknown { background:var(--unknown); }
.btn-known:hover { background:#219a52; }
.btn-learning:hover { background:#d68910; }
.btn-unknown:hover { background:#7f8c8d; }

.card-counter {
  text-align:center; font-size:.85em; color:var(--text-light); margin:8px 0;
}

.hint { text-align:center; font-size:.8em; color:var(--text-light); margin:8px 0; }

/* Word list */
.word-table {
  width:100%; border-collapse:collapse; font-size:.85em;
  background:white; border-radius:10px; overflow:hidden;
  box-shadow:0 2px 8px rgba(0,0,0,.08);
}
.word-table th {
  background:var(--primary); color:white; padding:10px 12px; text-align:left;
  position:sticky; top:0;
}
.word-table td { padding:8px 12px; border-bottom:1px solid #f0f0f0; }
.word-table tr:hover { background:#f8f9fa; }
.word-table .st-known { color:var(--known); font-weight:600; }
.word-table .st-learning { color:var(--learning); font-weight:600; }
.word-table .st-new { color:var(--text-light); }
.table-container { max-height:60vh; overflow-y:auto; border-radius:10px; }

.pagination {
  display:flex; justify-content:center; gap:8px; margin:12px 0; align-items:center;
}
.pagination button {
  padding:6px 12px; border:1px solid var(--border); background:white;
  border-radius:6px; cursor:pointer; font-size:.85em;
}
.pagination button.active { background:var(--primary); color:white; border-color:var(--primary); }
.pagination button:disabled { opacity:.4; cursor:default; }

/* Settings */
.danger-zone {
  margin:30px 0; padding:16px; background:#fef0f0; border:1px solid #f5c6cb;
  border-radius:10px;
}
.danger-zone h3 { color:var(--accent); margin-bottom:8px; }
.btn-reset {
  padding:10px 20px; background:#e74c3c; color:white; border:none;
  border-radius:8px; cursor:pointer; font-weight:600;
}
.btn-reset:hover { background:#c0392b; }

@media(max-width:600px) {
  .card-wrapper { height:250px; }
  .card-word { font-size:1.6em; }
  .stats-grid { grid-template-columns:repeat(2,1fr); }
}
</style>
</head>
<body>

<header>
  <h1>英単語フラッシュカード</h1>
  <p>NGSL / NAWL / TSL / Spoken / BSL &mdash; 全 <span id="totalCount">0</span> 語</p>
</header>

<div class="nav">
  <button onclick="showSection('dashboard')" id="nav-dashboard" class="active">ダッシュボード</button>
  <button onclick="showSection('flashcard')" id="nav-flashcard">フラッシュカード</button>
  <button onclick="showSection('wordlist')" id="nav-wordlist">単語一覧</button>
  <button onclick="showSection('settings')" id="nav-settings">設定</button>
</div>

<div class="container">

<!-- Dashboard -->
<div class="section active" id="sec-dashboard">
  <h2 style="margin:12px 0">学習状況</h2>
  <div class="stats-grid">
    <div class="stat-card total"><div class="num" id="ds-total">0</div><div class="label">総単語数</div></div>
    <div class="stat-card known"><div class="num" id="ds-known">0</div><div class="label">覚えた</div></div>
    <div class="stat-card learning"><div class="num" id="ds-learning">0</div><div class="label">学習中</div></div>
    <div class="stat-card unknown"><div class="num" id="ds-new">0</div><div class="label">未学習</div></div>
  </div>
  <div class="progress-bar-container">
    <div class="seg-known" id="pb-known"></div>
    <div class="seg-learning" id="pb-learning"></div>
  </div>
  <p style="text-align:center;font-size:.8em;color:var(--text-light)">
    <span style="color:var(--known)">&block;</span> 覚えた
    <span style="color:var(--learning);margin-left:10px">&block;</span> 学習中
    <span style="color:var(--unknown);margin-left:10px">&block;</span> 未学習
  </p>
  <h3 style="margin:20px 0 8px">リスト別進捗</h3>
  <div class="source-stats" id="source-stats"></div>
</div>

<!-- Flashcard -->
<div class="section" id="sec-flashcard">
  <div class="filter-bar">
    <label>リスト:</label>
    <select id="fc-source" onchange="applyFilter()">
      <option value="all">すべて</option>
      <option value="NGSL">NGSL</option>
      <option value="NAWL">NAWL</option>
      <option value="TSL">TSL</option>
      <option value="Spoken">Spoken</option>
      <option value="BSL">BSL</option>
    </select>
    <label>状態:</label>
    <select id="fc-status" onchange="applyFilter()">
      <option value="all">すべて</option>
      <option value="new">未学習</option>
      <option value="learning">学習中</option>
      <option value="known">覚えた</option>
    </select>
    <button onclick="shuffleDeck()" style="padding:6px 14px;border:1px solid var(--border);border-radius:8px;cursor:pointer;font-size:.85em">シャッフル</button>
  </div>

  <div class="card-counter"><span id="fc-pos">0</span> / <span id="fc-total">0</span></div>

  <div class="card-wrapper" id="card-wrapper" onclick="flipCard()">
    <div class="card-inner" id="card-inner">
      <div class="card-front">
        <span class="card-status-badge" id="fc-badge"></span>
        <span class="card-source" id="fc-source-badge"></span>
        <div class="card-word" id="fc-word">&mdash;</div>
      </div>
      <div class="card-back">
        <span class="card-source" id="fc-source-badge2"></span>
        <div class="card-def" id="fc-def"></div>
        <div class="card-pos" id="fc-pos-label"></div>
        <div class="card-jp" id="fc-jp"></div>
      </div>
    </div>
  </div>

  <p class="hint">クリックまたはスペースでめくる / &larr; &rarr; で移動 / 1:未学習 2:学習中 3:覚えた</p>

  <div class="status-buttons">
    <button class="btn-unknown" onclick="setStatus('new')">未学習</button>
    <button class="btn-learning" onclick="setStatus('learning')">学習中</button>
    <button class="btn-known" onclick="setStatus('known')">覚えた！</button>
  </div>

  <div class="card-nav">
    <button class="btn-prev" onclick="prevCard()">&larr; 前</button>
    <button class="btn-next" onclick="nextCard()">次 &rarr;</button>
  </div>
</div>

<!-- Word List -->
<div class="section" id="sec-wordlist">
  <div class="filter-bar">
    <label>リスト:</label>
    <select id="wl-source" onchange="renderWordList()">
      <option value="all">すべて</option>
      <option value="NGSL">NGSL</option>
      <option value="NAWL">NAWL</option>
      <option value="TSL">TSL</option>
      <option value="Spoken">Spoken</option>
      <option value="BSL">BSL</option>
    </select>
    <label>状態:</label>
    <select id="wl-status" onchange="renderWordList()">
      <option value="all">すべて</option>
      <option value="new">未学習</option>
      <option value="learning">学習中</option>
      <option value="known">覚えた</option>
    </select>
    <input type="text" id="wl-search" placeholder="検索..." oninput="renderWordList()">
  </div>
  <div class="table-container">
    <table class="word-table">
      <thead><tr><th>#</th><th>単語</th><th>定義</th><th>リスト</th><th>状態</th></tr></thead>
      <tbody id="wl-body"></tbody>
    </table>
  </div>
  <div class="pagination" id="wl-pagination"></div>
</div>

<!-- Settings -->
<div class="section" id="sec-settings">
  <h2 style="margin:12px 0">設定</h2>
  <div class="danger-zone">
    <h3>学習データリセット</h3>
    <p style="margin:8px 0;font-size:.9em">すべての学習状況を初期化します。この操作は取り消せません。</p>
    <button class="btn-reset" onclick="resetAll()">リセットする</button>
  </div>
  <div style="margin:20px 0;padding:16px;background:white;border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,.08)">
    <h3 style="margin-bottom:8px">エクスポート / インポート</h3>
    <p style="font-size:.85em;margin:8px 0">学習データをJSON形式で保存・復元できます。</p>
    <button onclick="exportData()" style="padding:8px 16px;background:var(--primary);color:white;border:none;border-radius:8px;cursor:pointer;margin:4px">エクスポート</button>
    <button onclick="document.getElementById('import-file').click()" style="padding:8px 16px;background:var(--accent);color:white;border:none;border-radius:8px;cursor:pointer;margin:4px">インポート</button>
    <input type="file" id="import-file" accept=".json" style="display:none" onchange="importData(event)">
  </div>
</div>

</div>

<script>
const ALL_WORDS = __JSON_DATA__;

const STORAGE_KEY = 'eng_flashcard_status_v1';
let statusMap = {};
let deck = [];
let deckIdx = 0;
const PAGE_SIZE = 50;
let wlPage = 0;

function loadStatus() {
  try {
    const s = localStorage.getItem(STORAGE_KEY);
    if (s) statusMap = JSON.parse(s);
  } catch(e) {}
}
function saveStatus() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(statusMap));
}
function getStatus(word) { return statusMap[word] || 'new'; }

function showSection(name) {
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.nav button').forEach(b => b.classList.remove('active'));
  document.getElementById('sec-' + name).classList.add('active');
  document.getElementById('nav-' + name).classList.add('active');
  if (name === 'dashboard') updateDashboard();
  if (name === 'wordlist') { wlPage = 0; renderWordList(); }
}

function updateDashboard() {
  const counts = { known:0, learning:0, 'new':0 };
  const srcCounts = {};
  ALL_WORDS.forEach(w => {
    const st = getStatus(w.w);
    counts[st]++;
    if (!srcCounts[w.s]) srcCounts[w.s] = { known:0, learning:0, 'new':0, total:0 };
    srcCounts[w.s][st]++;
    srcCounts[w.s].total++;
  });
  const total = ALL_WORDS.length;
  document.getElementById('ds-total').textContent = total;
  document.getElementById('ds-known').textContent = counts.known;
  document.getElementById('ds-learning').textContent = counts.learning;
  document.getElementById('ds-new').textContent = counts['new'];
  document.getElementById('totalCount').textContent = total;

  document.getElementById('pb-known').style.width = (counts.known/total*100)+'%';
  document.getElementById('pb-learning').style.width = (counts.learning/total*100)+'%';

  const container = document.getElementById('source-stats');
  container.innerHTML = '';
  ['NGSL','NAWL','TSL','Spoken','BSL'].forEach(src => {
    const c = srcCounts[src];
    if (!c) return;
    const pct = Math.round(c.known/c.total*100);
    const row = document.createElement('div');
    row.className = 'source-row';
    row.innerHTML =
      '<span class="name">' + src + '</span>' +
      '<span style="font-size:.8em;color:var(--text-light)">' + c.total + '語</span>' +
      '<div class="bar-bg">' +
        '<div style="width:' + (c.known/c.total*100) + '%;background:var(--known)"></div>' +
        '<div style="width:' + (c.learning/c.total*100) + '%;background:var(--learning)"></div>' +
      '</div>' +
      '<span class="pct">' + pct + '%</span>';
    container.appendChild(row);
  });
}

function applyFilter() {
  const src = document.getElementById('fc-source').value;
  const st = document.getElementById('fc-status').value;
  deck = ALL_WORDS.filter(w => {
    if (src !== 'all' && w.s !== src) return false;
    if (st !== 'all' && getStatus(w.w) !== st) return false;
    return true;
  });
  deckIdx = 0;
  renderCard();
}

function shuffleDeck() {
  for (let i = deck.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [deck[i], deck[j]] = [deck[j], deck[i]];
  }
  deckIdx = 0;
  renderCard();
}

function renderCard() {
  const wrapper = document.getElementById('card-wrapper');
  wrapper.classList.remove('flipped');

  document.getElementById('fc-pos').textContent = deck.length ? deckIdx + 1 : 0;
  document.getElementById('fc-total').textContent = deck.length;

  if (!deck.length) {
    document.getElementById('fc-word').textContent = '該当なし';
    document.getElementById('fc-def').textContent = '';
    document.getElementById('fc-pos-label').textContent = '';
    document.getElementById('fc-jp').textContent = '';
    document.getElementById('fc-badge').textContent = '';
    document.getElementById('fc-source-badge').textContent = '';
    document.getElementById('fc-source-badge2').textContent = '';
    return;
  }
  const w = deck[deckIdx];
  const st = getStatus(w.w);
  document.getElementById('fc-word').textContent = w.w;
  document.getElementById('fc-def').textContent = w.d || '(定義なし)';
  document.getElementById('fc-pos-label').textContent = w.p ? '[' + w.p + ']' : '';
  document.getElementById('fc-jp').textContent = w.j || '';
  document.getElementById('fc-source-badge').textContent = w.s;
  document.getElementById('fc-source-badge2').textContent = w.s;

  const badge = document.getElementById('fc-badge');
  if (st === 'known') { badge.textContent = '覚えた'; badge.className = 'card-status-badge badge-known'; }
  else if (st === 'learning') { badge.textContent = '学習中'; badge.className = 'card-status-badge badge-learning'; }
  else { badge.textContent = '未学習'; badge.className = 'card-status-badge badge-new'; }
}

function flipCard() {
  document.getElementById('card-wrapper').classList.toggle('flipped');
}
function nextCard() {
  if (deck.length && deckIdx < deck.length - 1) { deckIdx++; renderCard(); }
}
function prevCard() {
  if (deck.length && deckIdx > 0) { deckIdx--; renderCard(); }
}
function setStatus(st) {
  if (!deck.length) return;
  const w = deck[deckIdx];
  statusMap[w.w] = st;
  saveStatus();
  renderCard();
  // auto-advance after marking
  if (deckIdx < deck.length - 1) {
    setTimeout(function() { deckIdx++; renderCard(); }, 300);
  }
}

function renderWordList() {
  const src = document.getElementById('wl-source').value;
  const st = document.getElementById('wl-status').value;
  const q = document.getElementById('wl-search').value.toLowerCase();
  var filtered = ALL_WORDS.filter(function(w) {
    if (src !== 'all' && w.s !== src) return false;
    if (st !== 'all' && getStatus(w.w) !== st) return false;
    if (q && w.w.toLowerCase().indexOf(q) < 0 && (w.d||'').toLowerCase().indexOf(q) < 0) return false;
    return true;
  });

  var totalPages = Math.ceil(filtered.length / PAGE_SIZE);
  if (wlPage >= totalPages) wlPage = Math.max(0, totalPages - 1);
  var start = wlPage * PAGE_SIZE;
  var page = filtered.slice(start, start + PAGE_SIZE);

  var tbody = document.getElementById('wl-body');
  var rows = '';
  for (var i = 0; i < page.length; i++) {
    var w = page[i];
    var s = getStatus(w.w);
    var cls = s === 'known' ? 'st-known' : s === 'learning' ? 'st-learning' : 'st-new';
    var label = s === 'known' ? '覚えた' : s === 'learning' ? '学習中' : '未学習';
    var defText = w.d || '-';
    if (w.j) defText += ' <small>(' + w.j + ')</small>';
    rows += '<tr><td>' + (start+i+1) + '</td><td><strong>' + w.w + '</strong></td><td>' + defText + '</td><td>' + w.s + '</td><td class="' + cls + '">' + label + '</td></tr>';
  }
  tbody.innerHTML = rows;

  var pag = document.getElementById('wl-pagination');
  if (totalPages <= 1) {
    pag.innerHTML = '<span style="font-size:.85em;color:var(--text-light)">' + filtered.length + '語</span>';
    return;
  }
  var html = '<button ' + (wlPage===0?'disabled':'') + ' onclick="wlPage=0;renderWordList()">&laquo;</button>';
  html += '<button ' + (wlPage===0?'disabled':'') + ' onclick="wlPage--;renderWordList()">&lsaquo;</button>';
  html += '<span style="font-size:.85em">' + (wlPage+1) + ' / ' + totalPages + ' (' + filtered.length + '語)</span>';
  html += '<button ' + (wlPage>=totalPages-1?'disabled':'') + ' onclick="wlPage++;renderWordList()">&rsaquo;</button>';
  html += '<button ' + (wlPage>=totalPages-1?'disabled':'') + ' onclick="wlPage=' + (totalPages-1) + ';renderWordList()">&raquo;</button>';
  pag.innerHTML = html;
}

function resetAll() {
  if (confirm('本当にリセットしますか？すべての学習データが消去されます。')) {
    statusMap = {};
    saveStatus();
    updateDashboard();
    alert('リセットしました');
  }
}
function exportData() {
  var blob = new Blob([JSON.stringify(statusMap, null, 2)], {type:'application/json'});
  var a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'flashcard_progress.json';
  a.click();
}
function importData(e) {
  var file = e.target.files[0];
  if (!file) return;
  var reader = new FileReader();
  reader.onload = function(ev) {
    try {
      statusMap = JSON.parse(ev.target.result);
      saveStatus();
      updateDashboard();
      alert('インポートしました');
    } catch(err) { alert('ファイルが不正です'); }
  };
  reader.readAsText(file);
}

document.addEventListener('keydown', function(e) {
  if (document.getElementById('sec-flashcard').classList.contains('active')) {
    if (e.key === 'ArrowRight') nextCard();
    else if (e.key === 'ArrowLeft') prevCard();
    else if (e.key === ' ') { e.preventDefault(); flipCard(); }
    else if (e.key === '1') setStatus('new');
    else if (e.key === '2') setStatus('learning');
    else if (e.key === '3') setStatus('known');
  }
});

loadStatus();
document.getElementById('totalCount').textContent = ALL_WORDS.length;
updateDashboard();
deck = ALL_WORDS.slice();
renderCard();
</script>
</body>
</html>"""

html = html.replace('__JSON_DATA__', json_str)

out_path = os.path.join(BASE, '英単語フラッシュカード.html')
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'Done! {len(data)} words, file size: {len(html.encode("utf-8")):,} bytes')
print(f'Output: {out_path}')
