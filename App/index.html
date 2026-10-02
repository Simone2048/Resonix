<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
  <meta name="theme-color" content="#090a0f">
  <title>Resonix — Advanced Motion Theremin</title>
  <link rel="manifest" href="manifest.json">
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; touch-action: none; }
    body {
      background: #090a0f;
      color: #e6edf3;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      height: 100vh;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }

    /* Top Control Bar */
    header {
      padding: 10px 15px;
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      justify-content: space-between;
      align-items: center;
      background: rgba(18, 22, 32, 0.85);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
      z-index: 10;
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    h1 {
      font-size: 1.2rem;
      letter-spacing: 1px;
      background: linear-gradient(135deg, #00f2fe, #ff007f);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    .badge {
      font-size: 0.7rem;
      background: rgba(0, 242, 254, 0.15);
      border: 1px solid #00f2fe;
      color: #00f2fe;
      padding: 2px 6px;
      border-radius: 10px;
      font-family: monospace;
    }
    .controls {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }
    select, button.tool-btn {
      background: #161b22;
      color: #c9d1d9;
      border: 1px solid rgba(255, 255, 255, 0.15);
      padding: 6px 10px;
      border-radius: 6px;
      font-size: 0.75rem;
      font-weight: 600;
      cursor: pointer;
      outline: none;
    }
    button.tool-btn.active {
      background: #ff007f;
      color: #fff;
      border-color: #ff007f;
      box-shadow: 0 0 10px rgba(255, 0, 127, 0.5);
    }

    /* Canvas Playing Arena */
    #arena {
      flex: 1;
      position: relative;
      cursor: crosshair;
    }
    canvas {
      display: block;
      width: 100%;
      height: 100%;
    }

    /* Floating HUD Info */
    .hud {
      position: absolute;
      bottom: 15px;
      left: 15px;
      font-family: monospace;
      font-size: 0.85rem;
      color: #8b949e;
      pointer-events: none;
      background: rgba(0,0,0,0.5);
      padding: 6px 12px;
      border-radius: 6px;
      border: 1px solid rgba(255,255,255,0.05);
    }

    /* Start / Permission Overlay */
    #overlay {
      position: absolute;
      inset: 0;
      background: rgba(9, 10, 15, 0.95);
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 15px;
      z-index: 20;
    }
    .start-btn {
      background: linear-gradient(135deg, #00f2fe, #ff007f);
      border: none;
      color: #fff;
      padding: 14px 32px;
      font-size: 1.1rem;
      font-weight: bold;
      border-radius: 30px;
      cursor: pointer;
      box-shadow: 0 0 25px rgba(0, 242, 254, 0.4);
    }
  </style>
</head>
<body>

  <header>
    <div class="brand">
      <h1>RESONIX</h1>
      <span class="badge" id="modeBadge">PC / Touch</span>
    </div>

    <div class="controls">
      <!-- Timbre -->
      <select id="voiceSelect">
        <option value="sine">Theremin (Sine)</option>
        <option value="sawtooth">Analog Lead (Saw)</option>
        <option value="square">8-Bit Arcade</option>
        <option value="triangle">Warm Sub</option>
      </select>

      <!-- Scale Quantizer -->
      <select id="scaleSelect">
        <option value="free">Freeform (Glide)</option>
        <option value="major">Major Scale</option>
        <option value="minor">Minor Scale</option>
        <option value="pentatonic">Pentatonic</option>
      </select>

      <!-- Effects & Octaves -->
      <button class="tool-btn active" id="delayBtn">Delay: ON</button>
      <button class="tool-btn" id="octDown">-1 Oct</button>
      <button class="tool-btn" id="octUp">+1 Oct</button>

      <!-- Recorder -->
      <button class="tool-btn" id="recBtn">● REC</button>
    </div>
  </header>

  <div id="arena">
    <canvas id="renderCanvas"></canvas>
    <div class="hud" id="hud">Pitch: -- Hz | Note: -- | Vol: 0%</div>
  </div>

  <div id="overlay">
    <h2>Resonix Motion Theremin</h2>
    <p style="color:#8b949e; font-size:0.9rem; text-align:center; max-width:300px;">
      Move mouse / finger or <b>tilt phone in air</b> to play music.
    </p>
    <button class="start-btn" id="startBtn">START PLAYING</button>
  </div>

  <script>
    // Audio Engine
    let audioCtx = null;
    let osc = null;
    let gainNode = null;
    let delayNode = null;
    let feedbackNode = null;
    let isRunning = false;
    let octaveShift = 0;

    // Recorder
    let mediaRecorder = null;
    let recordedChunks = [];
    let isRecording = false;

    // Canvas & Particles
    const canvas = document.getElementById('renderCanvas');
    const ctx = canvas.getContext('2d');
    let particles = [];
    let curX = 0.5, curY = 0.8, curVol = 0, curFreq = 440;

    const scales = {
      free: null,
      major: [0, 2, 4, 5, 7, 9, 11],
      minor: [0, 2, 3, 5, 7, 8, 10],
      pentatonic: [0, 2, 4, 7, 9]
    };

    function initAudio() {
      audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      osc = audioCtx.createOscillator();
      gainNode = audioCtx.createGain();

      // Space Echo / Delay Setup
      delayNode = audioCtx.createDelay();
      feedbackNode = audioCtx.createGain();
      delayNode.delayTime.value = 0.28; // 280ms echo
      feedbackNode.gain.value = 0.4;    // 40% feedback

      delayNode.connect(feedbackNode);
      feedbackNode.connect(delayNode);
      feedbackNode.connect(audioCtx.destination);

      osc.type = document.getElementById('voiceSelect').value;
      gainNode.gain.setValueAtTime(0, audioCtx.currentTime);

      osc.connect(gainNode);
      gainNode.connect(audioCtx.destination);
      gainNode.connect(delayNode); // Echo send
      osc.start();

      // Audio Recorder destination
      const dest = audioCtx.createMediaStreamDestination();
      gainNode.connect(dest);
      mediaRecorder = new MediaRecorder(dest.stream);
      mediaRecorder.ondataavailable = (e) => recordedChunks.push(e.data);
      mediaRecorder.onstop = exportAudio;

      isRunning = true;
    }

    function quantize(freq, scaleType) {
      if (scaleType === 'free') return freq;
      // Convert Hz to MIDI note
      let midi = 69 + 12 * Math.log2(freq / 440);
      let rounded = Math.round(midi);
      let semitone = rounded % 12;
      const allowed = scales[scaleType];

      // Find closest note in scale
      let closest = allowed.reduce((prev, curr) => Math.abs(curr - semitone) < Math.abs(prev - semitone) ? curr : prev);
      rounded = rounded - semitone + closest;
      return 440 * Math.pow(2, (rounded - 69) / 12);
    }

    function updateSound(normX, normY) {
      if (!isRunning) return;

      let baseFreq = 130 + normX * (880 - 130);
      baseFreq *= Math.pow(2, octaveShift);

      const scale = document.getElementById('scaleSelect').value;
      curFreq = quantize(baseFreq, scale);
      curVol = Math.max(0, Math.min(1, 1 - normY));

      const now = audioCtx.currentTime;
      osc.frequency.setTargetAtTime(curFreq, now, 0.025);
      gainNode.gain.setTargetAtTime(curVol * 0.35, now, 0.025);

      document.getElementById('hud').innerText = 
        `Pitch: ${Math.round(curFreq)} Hz | Vol: ${Math.round(curVol * 100)}% | Oct: ${octaveShift >= 0 ? '+' : ''}${octaveShift}`;

      // Spawn reactive visual particles
      if (curVol > 0.05) {
        for (let i = 0; i < 2; i++) {
          particles.push({
            x: curX * canvas.width,
            y: curY * canvas.height,
            vx: (Math.random() - 0.5) * 4,
            vy: (Math.random() - 0.5) * 4,
            radius: Math.random() * 8 + 4,
            alpha: 1,
            color: document.getElementById('voiceSelect').value === 'sawtooth' ? '#ff007f' : '#00f2fe'
          });
        }
      }
    }

    // Particle Animation Loop
    function animate() {
      ctx.fillStyle = 'rgba(9, 10, 15, 0.2)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Draw Glowing Theremin Cursor
      if (isRunning && curVol > 0.02) {
        let px = curX * canvas.width;
        let py = curY * canvas.height;
        let grad = ctx.createRadialGradient(px, py, 5, px, py, 40 + curVol * 40);
        grad.addColorStop(0, '#ffffff');
        grad.addColorStop(0.3, '#00f2fe');
        grad.addColorStop(1, 'transparent');
        ctx.fillStyle = grad;
        ctx.beginPath();
        ctx.arc(px, py, 40 + curVol * 40, 0, Math.PI * 2);
        ctx.fill();
      }

      // Draw and update particles
      particles.forEach((p, idx) => {
        p.x += p.vx;
        p.y += p.vy;
        p.alpha -= 0.02;
        ctx.save();
        ctx.globalAlpha = p.alpha;
        ctx.fillStyle = p.color;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
        if (p.alpha <= 0) particles.splice(idx, 1);
      });

      requestAnimationFrame(animate);
    }

    function resize() {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight - 60;
    }
    window.addEventListener('resize', resize);
    resize();
    animate();

    // Interaction Handlers (Mouse / Touch)
    window.addEventListener('pointermove', (e) => {
      if (e.clientY < 60) return;
      curX = Math.max(0, Math.min(1, e.clientX / window.innerWidth));
      curY = Math.max(0, Math.min(1, (e.clientY - 60) / (window.innerHeight - 60)));
      updateSound(curX, curY);
    });

    // Mobile Gyroscope
    function setupTilt() {
      window.addEventListener('deviceorientation', (e) => {
        if (e.gamma === null) return;
        document.getElementById('modeBadge').innerText = "Gyro Tilt Mode";
        curX = Math.max(0, Math.min(1, (e.gamma + 35) / 70));
        curY = Math.max(0, Math.min(1, 1 - ((e.beta - 15) / 45)));
        updateSound(curX, curY);
      });
    }

    // UI Buttons
    document.getElementById('voiceSelect').onchange = (e) => { if (osc) osc.type = e.target.value; };
    document.getElementById('octUp').onclick = () => octaveShift = Math.min(2, octaveShift + 1);
    document.getElementById('octDown').onclick = () => octaveShift = Math.max(-2, octaveShift - 1);

    document.getElementById('delayBtn').onclick = (e) => {
      const active = e.target.classList.toggle('active');
      feedbackNode.gain.value = active ? 0.4 : 0.0;
      e.target.innerText = `Delay: ${active ? 'ON' : 'OFF'}`;
    };

    // Performance Recording
    const recBtn = document.getElementById('recBtn');
    recBtn.onclick = () => {
      if (!isRecording) {
        recordedChunks = [];
        mediaRecorder.start();
        isRecording = true;
        recBtn.innerText = "■ STOP";
        recBtn.classList.add('active');
      } else {
        mediaRecorder.stop();
        isRecording = false;
        recBtn.innerText = "● REC";
        recBtn.classList.remove('active');
      }
    };

    function exportAudio() {
      const blob = new Blob(recordedChunks, { type: 'audio/webm' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `resonix_recording_${Date.now()}.webm`;
      a.click();
    }

    // Start / Permission
    document.getElementById('startBtn').onclick = async () => {
      initAudio();
      document.getElementById('overlay').style.display = 'none';

      if (typeof DeviceOrientationEvent !== 'undefined' && typeof DeviceOrientationEvent.requestPermission === 'function') {
        try {
          const res = await DeviceOrientationEvent.requestPermission();
          if (res === 'granted') setupTilt();
        } catch(err) { console.error(err); }
      } else {
        setupTilt();
      }
    };

    // PWA Service Worker
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('sw.js');
    }
  </script>
</body>
</html>