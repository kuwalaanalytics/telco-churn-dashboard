// Makes the two sound stems for the video: a music bed and the effects.
// Run from the video folder:  node scripts/gen-audio.mjs   (or npm run audio)
// Writes assets/audio/music.wav and assets/audio/sfx.wav (48 kHz, 16 bit, stereo).
// Everything is synthesised here, so the same script always gives the same sound.
//
// All times come from the timing block and the typed lines in index.html,
// so moving something there and re-running this keeps sound and picture in step.

import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const OUT = join(ROOT, "assets", "audio");
const html = readFileSync(join(ROOT, "index.html"), "utf8");
const T = JSON.parse(html.match(/<script type="application\/json" id="timing">([\s\S]*?)<\/script>/)[1]);
const A = T.at;
const E = T.ends;
const CPS = T.cps;
const LINES = Object.entries(T.lines).map(([id, start]) => {
  const text = html.match(new RegExp(`id="${id}" data-text="([^"]*)"`))[1].replace(/[{}]/g, "");
  return [start, text];
});

const SR = 48000;
const DUR = T.duration;
const N = Math.round(SR * DUR);

// Overall level. Set so the two stems together sit near -14 LUFS with peaks under -1 dB.
const MUSIC_GAIN = Number(process.env.MUSIC_GAIN ?? 1.5);
const SFX_GAIN = Number(process.env.SFX_GAIN ?? 1.3);

// Seeded random numbers, so noise is identical on every run.
let seed = 20261013;
const rnd = () => ((seed = (seed * 1664525 + 1013904223) >>> 0) / 4294967296) * 2 - 1;

const stem = () => [new Float32Array(N), new Float32Array(N)];
const TAU = Math.PI * 2;

// Add a sound to a stem. fn(t) returns a sample; pan runs from -1 (left) to 1 (right).
function add(buf, start, length, pan, fn) {
  const i0 = Math.round(start * SR);
  const n = Math.round(length * SR);
  const gl = Math.cos(((pan + 1) * Math.PI) / 4);
  const gr = Math.sin(((pan + 1) * Math.PI) / 4);
  for (let i = 0; i < n; i++) {
    const j = i0 + i;
    if (j < 0 || j >= N) continue;
    const v = fn(i / SR);
    buf[0][j] += v * gl;
    buf[1][j] += v * gr;
  }
}

// ---------- music ----------
const music = stem();
const BEAT = 0.6; // 100 beats a minute
const BAR = BEAT * 4;
const CHORDS = [
  [146.83, 185.0, 220.0, 277.18, 329.63], // D major 9
  [123.47, 146.83, 185.0, 220.0, 277.18], // B minor 9
  [98.0, 123.47, 146.83, 185.0, 220.0], // G major 9
  [110.0, 138.59, 164.81, 185.0, 246.94], // A 6/9
];

// How loud the band is over time: quiet under the opening question, dropped right
// down under the revenue scene (the most important line), faded out on the end card.
const ramp = (a, b, x) => Math.min(1, Math.max(0, (x - a) / (b - a)));
function level(t) {
  let g = 0.55 + 0.45 * ramp(E.s1 - 0.4, E.s1 + 0.4, t);
  g *= 1 - 0.85 * (ramp(E.s3 - 0.3, E.s3 + 0.1, t) - ramp(E.s4 - 0.3, E.s4 + 0.2, t));
  g *= 1 - ramp(E.s10 - 1.6, E.s10 - 0.1, t);
  return g;
}
const drums = (t) => (t >= E.s1 && (t < E.s3 - 0.2 || t >= E.s4) && t < E.s9 - 0.2 ? 1 : 0);

const bars = Math.ceil(DUR / BAR);
for (let b = 0; b < bars; b++) {
  const chord = CHORDS[b % CHORDS.length];
  const t0 = b * BAR;

  // Pad: soft sustained chord, slow in and out so bars overlap.
  chord.forEach((f, k) => {
    const pan = (k / (chord.length - 1)) * 1.2 - 0.6;
    add(music, t0 - 0.25, BAR + 0.9, pan, (t) => {
      const env = Math.min(1, t / 0.55) * Math.min(1, (BAR + 0.9 - t) / 0.75);
      const vib = 1 + 0.0015 * Math.sin(TAU * 0.8 * t + k);
      const p = TAU * f * vib * t;
      return 0.085 * env * (Math.sin(p) + 0.28 * Math.sin(2 * p) + 0.1 * Math.sin(3 * p));
    });
  });

  // Pluck: an eighth note pattern over the chord, an octave up.
  const pattern = [0, 2, 4, 2, 3, 2, 4, 1];
  pattern.forEach((idx, s) => {
    const ts = t0 + s * (BEAT / 2);
    const f = chord[idx] * 2;
    add(music, ts, 0.5, s % 2 ? 0.35 : -0.35, (t) => {
      const env = Math.exp(-t / 0.13) * Math.min(1, t / 0.004);
      return 0.16 * env * (Math.sin(TAU * f * t) + 0.35 * Math.sin(TAU * 2 * f * t) * Math.exp(-t / 0.05));
    });
  });

  for (let q = 0; q < 4; q++) {
    const tb = t0 + q * BEAT;
    // Kick on beats 1 and 3: a sine that falls from about 118 Hz to 48 Hz.
    if (q % 2 === 0 && drums(tb)) {
      add(music, tb, 0.3, 0, (t) => 0.42 * Math.exp(-t / 0.11) * Math.sin(TAU * (48 * t + 70 * 0.035 * (1 - Math.exp(-t / 0.035)))));
    }
    // Shaker on the off beats.
    if (drums(tb + BEAT / 2)) {
      let last = 0;
      add(music, tb + BEAT / 2, 0.07, 0.2, (t) => {
        const n = rnd();
        const hp = n - last;
        last = n;
        return 0.05 * Math.exp(-t / 0.018) * hp;
      });
    }
  }
}
for (let i = 0; i < N; i++) {
  const g = level(i / SR);
  music[0][i] *= g;
  music[1][i] *= g;
}

// ---------- effects ----------
const sfx = stem();

const tick = (t0) => {
  const f = 1500 + 500 * rnd();
  const amp = 0.1 + 0.03 * rnd();
  add(sfx, t0, 0.03, 0.15 * rnd(), (t) => amp * Math.exp(-t / 0.006) * (0.6 * rnd() + 0.4 * Math.sin(TAU * f * t)));
};
// A short chirp that rises from 520 Hz to 820 Hz (times pitch).
const pop = (t0, pan = 0, pitch = 1) =>
  add(sfx, t0, 0.16, pan, (t) => 0.3 * Math.exp(-t / 0.05) * Math.sin(TAU * pitch * (520 * t + (300 * Math.min(t, 0.05) ** 2) / 0.1)));
const thud = (t0) =>
  add(sfx, t0, 0.5, 0, (t) => {
    const body = Math.sin(TAU * (52 * t + 60 * 0.05 * (1 - Math.exp(-t / 0.05))));
    return 0.75 * Math.exp(-t / 0.14) * body + 0.2 * Math.exp(-t / 0.004) * rnd();
  });
const swish = (t0, pan = 0) => {
  let lp = 0;
  add(sfx, t0, 0.26, pan, (t) => {
    lp += 0.35 * (rnd() - lp);
    return 0.22 * Math.sin((Math.PI * t) / 0.26) ** 2 * lp;
  });
};
const drop = (t0) => add(sfx, t0, 0.2, 0.3, (t) => 0.28 * Math.exp(-t / 0.07) * Math.sin(TAU * (620 * t - 600 * t * t)));
const chime = (t0) =>
  [587.33, 880.0, 1174.66].forEach((f, k) =>
    add(sfx, t0 + k * 0.07, 1.6, k * 0.3 - 0.3, (t) => 0.2 * Math.exp(-t / 0.5) * Math.min(1, t / 0.004) * Math.sin(TAU * f * t)),
  );

// Typing: one tick for each letter of each typed line.
for (const [t0, text] of LINES) {
  [...text].forEach((c, i) => {
    if (c !== " ") tick(t0 + i / CPS);
  });
}

// Things landing. Each one finishes before its line starts typing.
swish(A.s2In); // dashboard rises in
swish(A.s2Pan + 0.2, 0.3); // and pans down
[0, 1, 2, 3].forEach((i) => pop(A.s3In + i * 0.06, i * 0.3 - 0.45, 1 + i * 0.06)); // four people and the card
drop(A.s3Left); // one of them leaves
thud(A.s4In); // revenue card
swish(A.s5In);
pop(A.s5Mark, -0.3, 0.9); // ring on the month to month bar
pop(A.s5Mark + 0.05, 0.2, 1.2); // "43% leave"
swish(A.s6In);
pop(A.s6Mark, -0.4, 0.9); // ring on the first 6 months
pop(A.s6Mark + 0.05, 0.2, 1.2); // "53% in the first 6 months"
swish(A.s7In);
[0, 1, 2, 3].forEach((i) => pop(A.s7Rows + i * 0.12, -0.2, 1.3 - i * 0.08)); // rows in rank order
pop(A.s7Mark, 0.4, 1.3); // "Call first"
swish(A.s8In);
pop(A.s8Box, 0, 0.9); // box around the top 20%
drop(A.s8Top); // leavers inside the box
drop(A.s8Rest); // the rest
pop(A.s8Half, 0.4, 1.2); // "51% of leavers"
chime(A.endIn); // end card
[0, 1, 2].forEach((i) => pop(A.endIcons + i * 0.1, i * 0.4 - 0.4, 1.1 + i * 0.08)); // social icons

// ---------- write ----------
function writeWav(name, buf, gain) {
  const data = Buffer.alloc(44 + N * 4);
  data.write("RIFF", 0);
  data.writeUInt32LE(36 + N * 4, 4);
  data.write("WAVEfmt ", 8);
  data.writeUInt32LE(16, 16);
  data.writeUInt16LE(1, 20);
  data.writeUInt16LE(2, 22);
  data.writeUInt32LE(SR, 24);
  data.writeUInt32LE(SR * 4, 28);
  data.writeUInt16LE(4, 32);
  data.writeUInt16LE(16, 34);
  data.write("data", 36);
  data.writeUInt32LE(N * 4, 40);
  let peak = 0;
  for (let i = 0; i < N; i++) {
    for (let ch = 0; ch < 2; ch++) {
      // Soft limit so a loud moment rounds off instead of clipping.
      const v = Math.tanh(buf[ch][i] * gain * 1.1) / 1.1;
      peak = Math.max(peak, Math.abs(v));
      data.writeInt16LE(Math.round(Math.max(-1, Math.min(1, v)) * 32767), 44 + (i * 2 + ch) * 2);
    }
  }
  mkdirSync(OUT, { recursive: true });
  writeFileSync(join(OUT, name), data);
  console.log(`${name}: ${DUR}s, peak ${(20 * Math.log10(peak)).toFixed(1)} dB`);
}

writeWav("music.wav", music, MUSIC_GAIN);
writeWav("sfx.wav", sfx, SFX_GAIN);
