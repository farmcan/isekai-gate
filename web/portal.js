const $ = id => document.getElementById(id);
const styles = {
  anime: {name: '动画番剧', file: 'cat-ai-anime.png', line: '像误入了一帧夏日番剧。'},
  clay: {name: '黏土小剧场', file: 'cat-ai-clay.png', line: '这只猫，好像可以捏一下。'},
};
let selected = 'anime';
const select = id => {
  if (!styles[id]) return;
  selected = id;
  $('aiAfter').src = './media/' + styles[id].file;
  $('aiStyleName').textContent = styles[id].name;
  $('aiStyleLine').textContent = styles[id].line;
  document.querySelectorAll('[data-ai-style]').forEach(button => {
    const active = button.dataset.aiStyle === id;
    button.setAttribute('aria-pressed', String(active));
    button.classList.toggle('chosen', active);
  });
};
document.querySelectorAll('[data-ai-style]').forEach(button => button.addEventListener('click', () => select(button.dataset.aiStyle)));
$('useAiCover').addEventListener('click', async () => {
  const button = $('useAiCover'); button.disabled = true;
  $('aiActionStatus').textContent = '正在装入 AI 封面与原片…';
  try {
    await window.isekaiStudio.useAiCover('./media/' + styles[selected].file, styles[selected].name);
    $('aiActionStatus').textContent = '已装入：AI 静态封面 + 原片动态。可以长按预览或导出。';
    $('makerDetails').open = true;
    $('studio').scrollIntoView({behavior: 'smooth', block: 'start'});
  } catch (error) { $('aiActionStatus').textContent = error.message || '装入失败，请重试。'; }
  finally { button.disabled = false; }
});
for (const id of ['studioNav', 'quickImport']) $(id).addEventListener('click', () => { $('makerDetails').open = true; });
$('sampleNav').addEventListener('click', () => $('inspiration').scrollIntoView({behavior: 'smooth', block: 'start'}));
async function candidates() {
  const response = await fetch('./media/meme-candidates.json');
  if (!response.ok) throw new Error('候选列表暂未加载');
  const data = await response.json();
  const selectedIds = new Set();
  const ideas = {'oiia-apt': '跟着节拍转一圈，穿越到太空舞台。', huh: '那一声“啊？”，变成像素 NPC 的困惑。', 'bongo-bad-guy': '让猫猫乐队登上毛毡小舞台。', 'surprised-kitty': '双爪一展开，魔法刚好发生。', 'keyboard-cat': '给经典橘猫换一个霓虹演奏厅。', 'happy-happy-cat': '毛绒跳跳猫，快乐弹进星空。', 'huh-universes': '同一种困惑，来自三个不同宇宙。'};
  const emoji = {'oiia-apt': '🌀', huh: '❔', 'bongo-bad-guy': '🎹', 'surprised-kitty': '🙌', 'keyboard-cat': '🎵', 'happy-happy-cat': '✨', 'huh-universes': '🪐'};
  for (const item of data.candidates) {
    const card = document.createElement('article'); card.className = 'meme-card';
    const motif = document.createElement('div'); motif.className = 'meme-motif'; motif.textContent = emoji[item.id] || '✦'; motif.setAttribute('aria-hidden', 'true');
    const meta = document.createElement('p'); meta.className = 'meme-meta'; meta.textContent = item.platform + ' / ' + item.published_at.slice(0, 4);
    const heading = document.createElement('h3'); heading.textContent = item.title;
    const count = document.createElement('p'); count.className = 'meme-count';
    const engagement = item.engagement, live = engagement.evidence_type === 'live_primary_ui';
    count.textContent = (live ? '' : '历史记载 ') + (engagement.operator === '>' ? '超过 ' : '') + (engagement.likes / 10000).toFixed(1) + ' 万赞';
    const proof = document.createElement('small'); proof.textContent = live ? '2026.10.31 原帖页面核验' : '历史二级证据 · 当前数值未知';
    const description = document.createElement('p'); description.className = 'meme-description'; description.textContent = ideas[item.id] || item.ai_direction;
    const actions = document.createElement('div'); actions.className = 'meme-actions';
    const link = document.createElement('a'); link.href = item.url; link.target = '_blank'; link.rel = 'noopener noreferrer'; link.textContent = '去原帖看 ↗';
    const choose = document.createElement('button'); choose.type = 'button'; choose.textContent = '想试这个 ＋'; choose.setAttribute('aria-pressed', 'false');
    choose.addEventListener('click', () => {
      if (selectedIds.has(item.id)) selectedIds.delete(item.id); else selectedIds.add(item.id);
      choose.setAttribute('aria-pressed', String(selectedIds.has(item.id)));
      choose.textContent = selectedIds.has(item.id) ? '已选 ✓' : '想试这个 ＋';
      const names = data.candidates.filter(candidate => selectedIds.has(candidate.id)).map(candidate => candidate.title);
      $('candidateSelection').textContent = names.length ? '我的候选：' + names.join('、') + '。选好后可复制名称发给我。' : '你来挑：可以同时选择几个喜欢的梗。';
      $('copyCandidates').disabled = !names.length;
      $('copyCandidates').dataset.selection = names.join('、');
    });
    actions.append(link, choose); card.append(motif, meta, heading, count, proof, description, actions); $('memeGrid').append(card);
  }
}
$('copyCandidates').addEventListener('click', async () => {
  try { await navigator.clipboard.writeText('我想先做：' + $('copyCandidates').dataset.selection); $('candidateSelection').textContent = '已复制，可以粘贴到聊天里。'; }
  catch { $('candidateSelection').textContent = '请手动复制候选名称：' + $('copyCandidates').dataset.selection; }
});
candidates().catch(() => { $('candidateSelection').textContent = '候选加载失败，可刷新后重试。'; });
