import {pairedJpeg, packagePlist} from './live-pair.js';

const $ = id => document.getElementById(id);
const video = $('video');
const preview = $('preview');
const state = {source: null, sourceUrl: null, sourceName: '', start: 0, length: 3, duration: 0, coverTime: 0, coverBlob: null, customCover: null, coverUrl: null, busy: false, playing: false, ready: false, revision: 0, sourceToken: 0, exportKind: 'live'};
let engine = null, loadingEngine = null, loadController = null, playingTimer = null, captureRevision = 0;
const downloadUrls = new Set();
const text = (id, value) => $(id).textContent = value;
const status = (message, error = false) => { text('status', message); $('status').classList.toggle('error', error); text('exportStatus', message); $('exportStatus').classList.toggle('error', error); };
const seconds = n => `${n.toFixed(1)} s`;
const clock = n => `${Math.floor(n / 60)}:${String(Math.floor(n % 60)).padStart(2, '0')}`;
const blobOf = (canvas, type = 'image/jpeg', quality = .94) => new Promise((resolve, reject) => canvas.toBlob(b => b ? resolve(b) : reject(new Error('图片导出失败')), type, quality));
const dimensions = () => {
  const ratio = $('ratio').value;
  const aspect = ratio === 'original' ? video.videoWidth / video.videoHeight : Number(ratio.split(':')[0]) / Number(ratio.split(':')[1]);
  const h = Math.round(Math.min(video.videoHeight, 960, 960 / aspect) / 2) * 2;
  return {width: Math.max(2, Math.round(h * aspect / 2) * 2), height: Math.max(2, h)};
};

function cropDraw(ctx, image, x, y, w, h) {
  const iw = image.videoWidth || image.naturalWidth || image.width;
  const ih = image.videoHeight || image.naturalHeight || image.height;
  const scale = Math.max(w / iw, h / ih);
  const sw = w / scale, sh = h / scale;
  ctx.drawImage(image, (iw - sw) / 2, (ih - sh) / 2, sw, sh, x, y, w, h);
}

async function seek(time, element = video) {
  await new Promise((resolve, reject) => {
    const cleanup = () => { clearTimeout(timer); element.removeEventListener('seeked', done); };
    const done = () => { cleanup(); resolve(); };
    const timer = setTimeout(() => { cleanup(); reject(new Error('视频定位超时，请换一个 MP4 片段')); }, 12000);
    element.addEventListener('seeked', done, {once: true});
    const target = Math.min(time, Math.max(0, element.duration - .04));
    element.currentTime = Math.abs(element.currentTime - target) < .001 ? Math.min(target + .01, element.duration - .02) : target;
  });
  // A loaded/seeked frame can precede the composited frame on WebKit. Waiting
  // for presentation avoids black canvas covers on the initial paused frame.
  await new Promise(resolve => {
    let callback;
    const done = () => { clearTimeout(timer); if (callback) element.cancelVideoFrameCallback(callback); resolve(); };
    const timer = setTimeout(done, 180);
    if (element.requestVideoFrameCallback) callback = element.requestVideoFrameCallback(done);
    else requestAnimationFrame(() => requestAnimationFrame(done));
  });
}

async function captureCover() {
  if (!state.ready) return;
  stopPlaying();
  const revision = ++captureRevision;
  let source = video;
  if (state.customCover) {
    source = await createImageBitmap(state.customCover);
  } else {
    await seek(state.coverTime);
  }
  const {width, height} = dimensions();
  const canvas = document.createElement('canvas'); canvas.width = width; canvas.height = height;
  cropDraw(canvas.getContext('2d'), source, 0, 0, width, height);
  if (source !== video) source.close();
  const blob = await blobOf(canvas);
  if (revision !== captureRevision) return;
  if (state.coverUrl) URL.revokeObjectURL(state.coverUrl);
  state.coverBlob = blob; state.coverUrl = URL.createObjectURL(blob);
  $('cover').src = state.coverUrl; $('cover').hidden = false;
  preview.style.aspectRatio = `${width}/${height}`;
  preview.style.width = `min(100%, ${Math.min(500, 330 * width / height)}px)`;
  text('coverLabel', state.customCover ? '自选图片封面 → 长按播放' : '视频帧封面 → 长按播放');
}

function invalidate() {
  state.revision++;
  $('downloads').replaceChildren();
  for (const url of downloadUrls) URL.revokeObjectURL(url);
  downloadUrls.clear();
}

function update() {
  const end = Math.min(state.duration, state.start + state.length);
  const ready = state.ready && !state.busy;
  $('start').max = Math.max(0, state.duration - Math.min(state.length, state.duration));
  $('start').value = state.start;
  $('coverTime').min = state.start;
  $('coverTime').max = Math.max(state.start, end - .05);
  state.coverTime = Math.min(Math.max(state.coverTime, state.start), Number($('coverTime').max));
  $('coverTime').value = state.coverTime;
  text('startLabel', seconds(state.start)); text('coverTimeLabel', seconds(state.coverTime));
  text('durationLabel', state.ready ? `${(end - state.start).toFixed(1)} 秒` : '—');
  text('timelineStart', clock(0)); text('timelineMiddle', clock(state.duration / 2)); text('timelineEnd', clock(state.duration));
  text('endLabel', seconds(end)); text('lengthLabel', state.ready ? seconds(end - state.start) : '—');
  text('clipBadge', state.ready ? `${seconds(state.start)} — ${seconds(end)}` : '先选一个视频');
  text('exportSummary', state.ready ? `${(end - state.start).toFixed(1)} 秒 · ${dimensions().width} × ${dimensions().height}` : '选好素材就可以导出');
  text('mobileSummary', state.ready ? `${(end - state.start).toFixed(1)} 秒 · ${dimensions().width} × ${dimensions().height}` : '选择一个视频开始');
  for (const id of ['start', 'coverTime', 'capture', 'playToggle', 'exportLive', 'exportVideo', 'exportCover', 'exportPoster', 'copyPost', 'openExport', 'openExportMobile', 'exportNow', 'soundToggle']) $(id).disabled = !ready;
  if (state.ready) {
    $('selectionWindow').hidden = false; $('coverMarker').hidden = false;
    $('selectionWindow').style.left = `${100 * state.start / state.duration}%`;
    $('selectionWindow').style.width = `${100 * (end - state.start) / state.duration}%`;
    $('coverMarker').style.left = `${100 * state.coverTime / state.duration}%`;
  } else { $('selectionWindow').hidden = true; $('coverMarker').hidden = true; }
  preview.disabled = !ready;
  for (const id of ['file', 'coverFile', 'ratio', 'quickImport']) $(id).disabled = state.busy;
  document.querySelectorAll('[data-duration], .sample, .filmstrip button').forEach(b => b.disabled = state.busy);
}

async function loadSource(source, name, sampleId = null) {
  if (state.busy) return;
  const token = ++state.sourceToken; ++captureRevision;
  stopPlaying(); state.ready = false; state.customCover = null; state.coverBlob = null; invalidate(); update();
  if (state.sourceUrl) URL.revokeObjectURL(state.sourceUrl);
  state.source = source; state.sourceName = name;
  state.sourceUrl = URL.createObjectURL(source);
  video.src = state.sourceUrl;
  status('正在读取视频…');
  await new Promise((resolve, reject) => {
    const cleanup = () => { clearTimeout(timer); video.removeEventListener('loadeddata', done); video.removeEventListener('error', fail); };
    const done = () => { cleanup(); resolve(); };
    const fail = () => { cleanup(); reject(new Error('浏览器无法播放这个视频。请先转为 H.264 MP4 再试。')); };
    const timer = setTimeout(fail, 15000);
    video.addEventListener('loadeddata', done, {once: true}); video.addEventListener('error', fail, {once: true});
    video.load();
  });
  if (token !== state.sourceToken) return false;
  if (!Number.isFinite(video.duration) || video.duration < .25 || video.duration > 180) throw new Error('请选择 0.25 秒至 3 分钟的视频。');
  state.duration = video.duration; state.start = 0; state.coverTime = 0; state.ready = true;
  $('emptyPreview').hidden = true; $('holdHint').hidden = false;
  text('fileLabel', name);
  document.querySelectorAll('.sample').forEach(b => b.classList.toggle('active', b.dataset.id === sampleId));
  update(); await captureCover();
  if (token !== state.sourceToken) return false;
  status('封面已准备好。按住画面，看看这几秒。');
  generateFilmstrip(token).catch(() => { if (token === state.sourceToken) text('timelineHint', '缩略帧暂不可用，可使用滑条选段'); });
  return true;
}

async function play() {
  if (!state.ready || state.busy || state.playing) return;
  state.playing = true;
  try {
    await seek(state.start);
    if (!state.playing) return;
    preview.classList.add('is-playing');
    await video.play();
    text('playToggle', 'Ⅱ'); $('playToggle').setAttribute('aria-label', '停止预览');
    playingTimer = setTimeout(stopPlaying, Math.min(state.length, state.duration - state.start) * 1000 + 30);
  } catch (error) { stopPlaying(); status(error.message, true); }
}
function stopPlaying() {
  state.playing = false; video.pause(); clearTimeout(playingTimer);
  preview.classList.remove('is-playing'); text('playToggle', '▷'); $('playToggle').setAttribute('aria-label', '播放预览');
}
video.addEventListener('timeupdate', () => { if (state.playing && video.currentTime >= state.start + state.length) stopPlaying(); });
video.addEventListener('ended', stopPlaying);
preview.addEventListener('pointerdown', e => { if (e.button !== 0) return; e.preventDefault(); preview.setPointerCapture(e.pointerId); play(); });
for (const event of ['pointerup', 'pointercancel', 'lostpointercapture', 'blur']) preview.addEventListener(event, stopPlaying);
preview.addEventListener('keydown', e => { if (e.code === 'Space' || e.code === 'Enter') { e.preventDefault(); if (!e.repeat) play(); } });
preview.addEventListener('keyup', stopPlaying);
$('playToggle').addEventListener('click', () => state.playing ? stopPlaying() : play());
document.addEventListener('visibilitychange', () => { if (document.hidden) stopPlaying(); });

async function importFile(file) {
  if (!file || state.busy) return;
  if (file.size > 120 * 1024 * 1024) throw new Error('文件超过 120 MB，请先选一段较短的视频。');
  if (!/\.(mp4|mov|webm|m4v)$/i.test(file.name)) throw new Error('请选择 MP4、MOV、M4V 或 WebM 视频。');
  await loadSource(file, file.name);
}
const safely = fn => async (...args) => { try { await fn(...args); } catch (e) { status(e.message || '操作失败，请重试。', true); update(); } };
$('file').addEventListener('change', safely(async e => { await importFile(e.target.files[0]); e.target.value = ''; }));
for (const type of ['dragover', 'dragenter']) $('dropzone').addEventListener(type, e => { e.preventDefault(); if (!state.busy) $('dropzone').classList.add('drag'); });
for (const type of ['dragleave', 'drop']) $('dropzone').addEventListener(type, e => { e.preventDefault(); $('dropzone').classList.remove('drag'); });
$('dropzone').addEventListener('drop', safely(e => importFile(e.dataTransfer.files[0])));
$('start').addEventListener('input', safely(async e => {
  stopPlaying(); state.start = Number(e.target.value); state.coverTime = Math.max(state.start, state.coverTime); invalidate(); update(); await captureCover();
}));
$('coverTime').addEventListener('input', safely(async e => { state.customCover = null; state.coverTime = Number(e.target.value); invalidate(); update(); await captureCover(); }));
$('capture').addEventListener('click', safely(async () => { state.customCover = null; invalidate(); await captureCover(); status('已使用这一帧作封面。'); }));
$('coverFile').addEventListener('change', safely(async e => {
  const file = e.target.files[0]; if (!file || !state.ready) return;
  if (file.size > 15 * 1024 * 1024) throw new Error('封面图片请小于 15 MB。');
  state.customCover = file; invalidate(); await captureCover(); e.target.value = '';
}));
$('ratio').addEventListener('change', safely(async () => { invalidate(); update(); await captureCover(); }));
document.querySelectorAll('[data-duration]').forEach(b => b.addEventListener('click', safely(async () => {
  stopPlaying(); state.length = Number(b.dataset.duration); state.start = Math.min(state.start, Math.max(0, state.duration - state.length));
  document.querySelectorAll('[data-duration]').forEach(x => x.classList.toggle('selected', x === b));
  invalidate(); update(); await captureCover();
})));

function progress(message, value = null) {
  text('progressText', message);
  if (value === null) $('progressBar').removeAttribute('value'); else $('progressBar').value = value;
}
async function timed(operation, milliseconds, message) {
  let timer;
  try { return await Promise.race([operation, new Promise((_, reject) => { timer = setTimeout(() => { terminateEngine(); reject(new Error(message)); }, milliseconds); })]); }
  finally { clearTimeout(timer); }
}
function terminateEngine() {
  loadController?.abort(); loadController = null;
  engine?.terminate(); engine = null; loadingEngine = null;
}
async function getEngine() {
  if (engine?.loaded) return engine;
  if (loadingEngine) return loadingEngine;
  engine = new FFmpegWASM.FFmpeg();
  const candidate = engine;
  loadController = new AbortController();
  const loadSignal = AbortSignal.any([loadController.signal, AbortSignal.timeout(60000)]);
  engine.on('progress', e => progress('正在制作这几秒…', Math.min(98, Math.max(0, e.progress * 100))));
  loadingEngine = (async () => {
    progress('首次加载转码工具，约 32 MB。素材不会上传。');
    const parts = await Promise.all([0, 1].map(async i => {
      const response = await fetch(`./vendor/ffmpeg-core.wasm.part${i}`, {signal: loadSignal});
      if (!response.ok) throw new Error('转码工具加载失败。登录可能已过期，请刷新后重试。');
      return response.arrayBuffer();
    }));
    const wasmURL = URL.createObjectURL(new Blob(parts, {type: 'application/wasm'}));
    try {
      await candidate.load({coreURL: new URL('./vendor/ffmpeg-core.js', location.href).href, wasmURL});
      return candidate;
    } finally { URL.revokeObjectURL(wasmURL); }
  })();
  try { return await timed(loadingEngine, 90000, '转码工具加载超时，请刷新后重试。'); }
  catch (error) { terminateEngine(); throw error; }
  finally { loadingEngine = null; }
}

function download(blob, name, label = name) {
  const url = URL.createObjectURL(blob); downloadUrls.add(url);
  const link = document.createElement('a'); link.href = url; link.download = name; link.textContent = `下载 ${label} ↓`;
  $('downloads').append(link); link.click();
}

async function runExport(kind) {
  if (!state.ready || state.busy) return;
  stopPlaying(); state.busy = true; update(); $('progress').hidden = false;
  let ff = null, inputName = null, outputName = null;
  try {
    await captureCover();
    const snapshot = {source: state.source, start: state.start, duration: Math.min(state.length, state.duration - state.start), cover: state.coverBlob, ...dimensions()};
    ff = await getEngine();
    const id = crypto.randomUUID();
    inputName = 'source.' + (state.sourceName.match(/\.(mp4|mov|webm|m4v)$/i)?.[1] || 'mp4').toLowerCase();
    outputName = kind === 'live' ? 'motion.mov' : 'clip.mp4';
    progress('正在读取素材…');
    await ff.writeFile(inputName, new Uint8Array(await snapshot.source.arrayBuffer()));
    const vf = `scale=${snapshot.width}:${snapshot.height}:force_original_aspect_ratio=increase,crop=${snapshot.width}:${snapshot.height},setsar=1`;
    const args = ['-ss', String(snapshot.start), '-i', inputName, '-t', String(snapshot.duration), '-map', '0:v:0', '-map', '0:a?', '-vf', vf, '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '22', '-pix_fmt', 'yuv420p', '-r', '30', '-c:a', 'aac', '-b:a', '128k', '-map_metadata', '-1'];
    if (kind === 'live') args.push('-metadata', `com.apple.quicktime.content.identifier=${id}`, '-movflags', 'use_metadata_tags');
    else args.push('-movflags', '+faststart');
    args.push('-y', outputName);
    const result = await timed(ff.exec(args), 120000, '转码超过两分钟，已停止。可换更小的视频或电脑再试。');
    if (result !== 0) throw new Error('视频转码失败，请换一个 H.264 MP4 片段重试。');
    const motion = await ff.readFile(outputName);
    if (kind === 'live') {
      progress('正在打包封面和动态片段…', 99);
      const jpeg = pairedJpeg(new Uint8Array(await snapshot.cover.arrayBuffer()), id);
      const manifest = {tool: 'isekai-live', version: '0.3.0', asset_id: id, duration_seconds: snapshot.duration, width: snapshot.width, height: snapshot.height, photos_validation: 'device_import_not_verified'};
      const files = {
        'livephoto.pvt/livephoto.jpg': jpeg,
        'livephoto.pvt/livephoto.mov': motion,
        'livephoto.pvt/metadata.plist': new TextEncoder().encode(packagePlist),
        'manifest.json': fflate.strToU8(JSON.stringify(manifest, null, 2)),
        '保存说明.txt': fflate.strToU8('解压后，在 Mac 上打开 livephoto.pvt，导入「照片」。\n图片与视频已写入相同配对标识。iPhone直接保存、壁纸及小红书原生实况上传尚待设备实测。\n原素材只在浏览器处理，不上传服务器。\n'),
      };
      download(new Blob([fflate.zipSync(files, {level: 0})], {type: 'application/zip'}), 'isekai-live-photo.zip', 'Live Photo 包');
      status('已打包。解压后在 Mac 打开 livephoto.pvt，导入「照片」。');
    } else {
      download(new Blob([motion], {type: 'video/mp4'}), 'isekai-live-clip.mp4', '视频片段 MP4');
      status('视频片段已准备好，可以搭配封面发布笔记。');
    }
  } catch (error) { status(error.message || '导出失败，请重试。', true); }
  finally {
    if (ff?.loaded) for (const name of [inputName, outputName].filter(Boolean)) { try { await ff.deleteFile(name); } catch {} }
    state.busy = false; $('progress').hidden = true; update();
  }
}
$('cancelExport').addEventListener('click', () => { terminateEngine(); status('已取消导出。'); });
async function exportCover() { await captureCover(); download(state.coverBlob, 'isekai-live-cover.jpg', '封面 JPG'); status('封面已准备好。'); }

function wrapText(ctx, value, maxWidth) {
  const rows = [''];
  for (const ch of value) {
    if (ctx.measureText(rows[rows.length - 1] + ch).width > maxWidth) rows.push(ch); else rows[rows.length - 1] += ch;
  }
  return rows.slice(0, 3);
}
async function exportPoster() {
  await captureCover();
  const canvas = document.createElement('canvas'); canvas.width = 1080; canvas.height = 1440;
  const ctx = canvas.getContext('2d'), image = await createImageBitmap(state.coverBlob);
  ctx.fillStyle = '#f4f6fb'; ctx.fillRect(0, 0, 1080, 1440);
  cropDraw(ctx, image, 48, 48, 984, 1010); image.close();
  ctx.fillStyle = '#253449'; ctx.font = '600 58px sans-serif';
  const caption = $('caption').value.trim() || '喜欢的瞬间，值得再看一次';
  wrapText(ctx, caption, 920).forEach((line, i) => ctx.fillText(line, 64, 1160 + i * 76));
  ctx.fillStyle = '#8093ba'; ctx.font = '24px sans-serif'; ctx.fillText('isekai-live  /  留住喜欢的那几秒', 64, 1380);
  download(await blobOf(canvas), 'isekai-live-share-cover.jpg', '3:4 分享封面'); status('3:4 分享封面已准备好。');
}
$('copyPost').addEventListener('click', safely(async () => {
  const caption = $('caption').value.trim() || '喜欢的瞬间，值得再看一次';
  const content = `${caption}\n\n从视频里挑出最想循环的 ${Math.min(state.length, state.duration - state.start).toFixed(1)} 秒，再选一张喜欢的封面。\n用 isekai-live 留住这个瞬间。\n\n#生活碎片 #视频选段 #LivePhoto #实况图`;
  try { await navigator.clipboard.writeText(content); status('笔记文案已复制。搭配导出的视频和封面，即可准备发布。'); }
  catch { download(new Blob([content], {type: 'text/plain;charset=utf-8'}), 'isekai-live-note.txt', '笔记文案'); }
}));

async function loadSamples() {
  const response = await fetch('./media/public-sources.json');
  if (!response.ok) return;
  const payload = await response.json();
  const samples = payload.items || [];
  for (const sample of samples) {
    const button = document.createElement('button'); button.type = 'button'; button.className = 'sample'; button.dataset.id = sample.id;
    const img = document.createElement('img'); img.src = './media/' + sample.cover; img.alt = sample.title; img.loading = 'lazy';
    const title = document.createElement('strong'); title.textContent = sample.title;
    const note = document.createElement('small'); note.textContent = sample.subtitle || '公开示例 · 点击试做';
    const description = document.createElement('span'); description.className = 'sample-text'; description.append(title, note);
    button.append(img, description);
    button.addEventListener('click', safely(async () => {
      const r = await fetch('./media/' + sample.video); if (!r.ok) throw new Error('示例暂时无法读取，请刷新后重试。');
      if (!(await loadSource(await r.blob(), sample.video, sample.id))) return;
      if (sample.start !== undefined) { state.start = sample.start; state.length = sample.length; state.coverTime = sample.coverTime ?? sample.start; update(); await captureCover(); }
      $('studio').scrollIntoView({behavior: 'smooth', block: 'start'});
    }));
    $('samples').append(button);
  }
  const own = document.createElement('button'); own.type = 'button'; own.className = 'sample sample-own';
  own.innerHTML = '<span class="sample-plus">＋</span><span><strong>接下来，试试你的。</strong><small>选一段相册里的视频</small></span>';
  own.addEventListener('click', () => $('file').click()); $('samples').append(own);
  if (samples[0] && !state.source) {
    const sample = samples[0], r = await fetch('./media/' + sample.video);
    if (r.ok && !state.source) await loadSource(await r.blob(), sample.video, sample.id);
  }
}
const thumbnailUrls = new Set();
let rangeDrag = null;
$('selectionWindow').addEventListener('pointerdown', e => {
  if (!state.ready || state.busy || e.button !== 0) return;
  e.preventDefault(); stopPlaying();
  const selection = $('selectionWindow'); selection.setPointerCapture(e.pointerId);
  const children = [...selection.children];
  rangeDrag = {x: e.clientX, start: state.start, length: state.length,
    mode: e.target === children[0] ? 'start' : e.target === children[1] ? 'end' : 'move'};
});
$('selectionWindow').addEventListener('pointermove', e => {
  if (!rangeDrag) return;
  const track = $('timelineTrack').getBoundingClientRect();
  const delta = (e.clientX - rangeDrag.x) / track.width * state.duration;
  const end = Math.min(state.duration, rangeDrag.start + rangeDrag.length);
  if (rangeDrag.mode === 'start') {
    state.start = Math.min(end - .5, Math.max(0, end - 5, rangeDrag.start + delta));
    state.length = end - state.start;
  } else if (rangeDrag.mode === 'end') {
    state.length = Math.min(5, state.duration - state.start, Math.max(.5, rangeDrag.length + delta));
  } else {
    state.start = Math.max(0, Math.min(state.duration - rangeDrag.length, rangeDrag.start + delta));
  }
  update();
});
for (const event of ['pointerup', 'pointercancel', 'lostpointercapture']) $('selectionWindow').addEventListener(event, safely(async e => {
  if (!rangeDrag) return;
  const drag = rangeDrag; rangeDrag = null;
  if (event === 'pointerup' && Math.abs(e.clientX - drag.x) < 3 && drag.mode === 'move') {
    const track = $('timelineTrack').getBoundingClientRect();
    state.coverTime = (e.clientX - track.left) / track.width * state.duration;
    state.customCover = null;
  }
  document.querySelectorAll('[data-duration]').forEach(item => item.classList.toggle('selected', Math.abs(Number(item.dataset.duration) - state.length) < .01));
  invalidate(); update(); await captureCover();
}));
async function generateFilmstrip(token) {
  const reader = document.createElement('video'); reader.muted = true; reader.playsInline = true;
  reader.src = state.sourceUrl;
  try {
    await new Promise((resolve, reject) => {
      const timeout = setTimeout(() => reject(new Error('Thumbnail load timed out')), 12000);
      reader.onloadeddata = () => { clearTimeout(timeout); resolve(); };
      reader.onerror = () => { clearTimeout(timeout); reject(new Error('Thumbnail load failed')); };
      reader.load();
    });
    if (token !== state.sourceToken) return;
    for (const url of thumbnailUrls) URL.revokeObjectURL(url);
    thumbnailUrls.clear(); $('filmstrip').replaceChildren();
    const duration = reader.duration, canvas = document.createElement('canvas'); canvas.width = 140; canvas.height = 88;
    for (let i = 0; i < 8; i++) {
      if (token !== state.sourceToken) return;
      const time = Math.min(duration - .08, duration * (i + .15) / 8);
      await seek(time, reader);
      if (token !== state.sourceToken) return;
      cropDraw(canvas.getContext('2d'), reader, 0, 0, 140, 88);
      const url = URL.createObjectURL(await blobOf(canvas, 'image/jpeg', .7)); thumbnailUrls.add(url);
      const button = document.createElement('button'); button.type = 'button'; button.setAttribute('aria-label', `选择 ${time.toFixed(1)} 秒附近的片段`);
      const img = document.createElement('img'); img.src = url; img.alt = ''; button.append(img);
      button.addEventListener('click', safely(async () => {
        if (state.busy) return;
        stopPlaying(); state.start = Math.min(Math.max(0, time - state.length / 2), Math.max(0, state.duration - state.length));
        state.coverTime = time; state.customCover = null; invalidate(); update(); await captureCover();
      }));
      $('filmstrip').append(button);
    }
    text('timelineHint', '点击缩略帧定位，拖动滑条微调');
  } finally { reader.removeAttribute('src'); reader.load(); }
}

document.querySelectorAll('[data-panel]').forEach(tab => tab.addEventListener('click', () => {
  document.querySelectorAll('[data-panel]').forEach(item => {
    const active = tab === item; item.classList.toggle('selected', active); item.setAttribute('aria-selected', String(active)); item.tabIndex = active ? 0 : -1;
    $(item.dataset.panel).hidden = !active;
  });
}));
document.querySelectorAll('[data-panel]').forEach((tab, index, tabs) => tab.addEventListener('keydown', e => {
  if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(e.key)) return;
  e.preventDefault();
  const next = e.key === 'Home' ? 0 : e.key === 'End' ? tabs.length - 1 : (index + (e.key === 'ArrowRight' ? 1 : -1) + tabs.length) % tabs.length;
  tabs[next].click(); tabs[next].focus();
}));
$('soundToggle').addEventListener('click', () => {
  video.muted = !video.muted;
  text('soundToggle', video.muted ? '静音预览' : '声音已开');
  $('soundToggle').setAttribute('aria-label', video.muted ? '开启预览声音' : '关闭预览声音');
});
$('caption').addEventListener('input', () => { invalidate(); text('captionPreview', $('caption').value || '写一句，只属于这个瞬间的话'); });
$('quickImport').addEventListener('click', () => $('file').click());
$('studioNav').addEventListener('click', () => $('studio').scrollIntoView({behavior: 'smooth', block: 'start'}));
$('sampleNav').addEventListener('click', () => $('sampleSection').scrollIntoView({behavior: 'smooth', block: 'start'}));
const dialog = $('exportDialog');
for (const id of ['openExport', 'openExportMobile', 'helpButton']) $(id).addEventListener('click', () => { stopPlaying(); dialog.showModal(); });
$('closeExport').addEventListener('click', () => dialog.close());
dialog.addEventListener('click', e => { if (e.target === dialog) { const box = dialog.getBoundingClientRect(); if (e.clientX < box.left || e.clientX > box.right || e.clientY < box.top || e.clientY > box.bottom) dialog.close(); } });
const exportFormats = {
  live: ['生成 Live Photo 包 ↓', 'Mac 解压后打开 livephoto.pvt，导入「照片」。iPhone 直接保存、壁纸和小红书原生实况上传仍待设备验证。'],
  video: ['导出视频片段 ↓', '通用 MP4，可用于图文笔记、视频发布和聊天。它是普通短视频，不会被标成已经验证的原生实况图。'],
  poster: ['生成 3:4 分享封面 ↓', '使用当前图片封面与「分享」设置中的文案，生成 1080 × 1440 JPG。'],
  cover: ['导出图片封面 ↓', '导出你选择的视频帧或自选图片，使用当前作品的比例。'],
};
document.querySelectorAll('[data-kind]').forEach(button => button.addEventListener('click', () => {
  state.exportKind = button.dataset.kind;
  document.querySelectorAll('[data-kind]').forEach(item => { const active = item === button; item.classList.toggle('selected', active); item.setAttribute('aria-pressed', String(active)); });
  text('exportNow', exportFormats[state.exportKind][0]); text('formatHelp', exportFormats[state.exportKind][1]);
}));
$('exportNow').addEventListener('click', safely(async () => {
  if (!state.ready || state.busy) return;
  if (state.exportKind === 'cover') await exportCover();
  else if (state.exportKind === 'poster') await exportPoster();
  else await runExport(state.exportKind);
}));
loadSamples().catch(() => status('可以直接放入自己的视频开始制作。'));
