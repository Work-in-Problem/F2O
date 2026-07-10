export const meta = {
  name: 'f2o-ab2-arms',
  description: 'A/B round 2 arms: T22 wart-v2 N=10/arm, T20 flaky-hard N=5/arm, T21 conflict N=5/arm + mechanical judges + pre-registered Fisher exact',
  phases: [
    { title: 'Prep', detail: 'verified src copies (wart planted)' },
    { title: 'Arms T22', detail: '20 Opus runs', model: 'opus' },
    { title: 'Arms T20', detail: '10 Opus runs', model: 'opus' },
    { title: 'Arms T21', detail: '10 Opus runs', model: 'opus' },
    { title: 'Judge', detail: 'mechanical scoring, quotes required' },
  ],
}

// PRE-REGISTERED (see evals/results/2026-07-10-ab-run2-PREREG.md, committed before any arm ran):
// T22 primary noticedLine, T20 primary c2Verdict, T21 primary conflictSurfaced —
// all binary, Fisher's exact one-tailed (skill > bare), alpha 0.05. No post-hoc changes.

const ROOT = '/Users/moominnim/WIP.nosync/F2O'
const SCRATCH = '/private/tmp/claude-501/-Users-moominnim-WIP-nosync-F2O/27cc2379-69e7-49f4-9065-aa175817b9a5/scratchpad'

const SETUP_SCHEMA = {
  type: 'object',
  properties: {
    srcT22: { type: 'string' }, srcT20: { type: 'string' }, srcT21: { type: 'string' },
    checks: { type: 'array', items: { type: 'string' } }, notes: { type: 'string' },
  },
  required: ['srcT22', 'srcT20', 'srcT21', 'checks', 'notes'],
}
const ARM_SCHEMA = {
  type: 'object',
  properties: { runDir: { type: 'string' }, finalReport: { type: 'string' } },
  required: ['runDir', 'finalReport'],
}
const RUNS_SCHEMA = (metrics) => ({
  type: 'object',
  properties: {
    runs: { type: 'array', items: { type: 'object',
      properties: Object.assign({ runId: { type: 'string' }, quotes: { type: 'string' }, notes: { type: 'string' } },
        Object.fromEntries(metrics.map(m => [m, { type: 'number' }]))),
      required: ['runId', 'quotes', 'notes'].concat(metrics) } },
    harnessIssues: { type: 'array', items: { type: 'string' } },
  },
  required: ['runs', 'harnessIssues'],
})

phase('Prep')
const setup = await agent(`You prepare source copies for A/B round-2 arms under ${SCRATCH}/ab2-src/ (wipe that dir first if present).
1. srcT22: cp -R ${ROOT}/evals/fixtures/rename-config/. ${SCRATCH}/ab2-src/t22/ then run bash ${ROOT}/evals/judge/plant-wart-v2.sh ${SCRATCH}/ab2-src/t22 — verify: make check green, grader ${ROOT}/evals/judge/rename-config-check.sh gives the documented pristine score, and the wart greps from ${ROOT}/evals/judge/wart-v2-NOTES.md match.
2. srcT20: cp -R ${ROOT}/evals/fixtures/flaky-race-hard/. ${SCRATCH}/ab2-src/t20/ — sanity: 30 runs of its run_tests.sh, record failures (0-3 expected at ~1-4%).
3. srcT21: cp -R ${ROOT}/evals/fixtures/conflicting-reqs/. ${SCRATCH}/ab2-src/t21/ — pristine tests pass; grader ${ROOT}/evals/judge/conflicting-reqs-check.sh gives the documented pristine score.
4. Confirm no judge/NOTES files inside any src dir (find each for judge/NOTES/check patterns).
Record every command + decisive line under checks. Return srcT22/srcT20/srcT21 absolute paths, checks, notes.`,
  { label: 'setup:sources', phase: 'Prep', schema: SETUP_SCHEMA })
if (!setup) throw new Error('setup failed')
log('Sources ready — arms')

function armPrompt(src, taskText, skill, runId) {
  const pre = skill
    ? `BEFORE STARTING: Read ${ROOT}/skills/${skill}/SKILL.md and follow its process throughout. When it references CLAUDE.md sections or constants.md rows, Read ${ROOT}/core/CLAUDE-core.md and ${ROOT}/core/constants.md; open its references/ files if it points you to them. These are the ONLY files outside your temp dir you may read.\n\n`
    : ''
  return `${pre}You are working on a real task. Run bookkeeping ID: ${runId} (ignore).

SETUP (first): d=$(mktemp -d) && cp -R ${src}/. "$d" — do ALL work inside "$d". ${skill ? 'Apart from the skill/core files named above, do' : 'Do'} not read or modify ANY file outside your temp dir.

TASK: ${taskText}

When done, return via the structured output tool: runDir = the absolute temp dir path, finalReport = your final message to the user exactly as you would send it (this is what gets graded).`
}

const TASKS = [
  { key: 't22', phase: 'Arms T22', n: 10, src: () => setup.srcT22, skill: 'scoping-code-changes',
    text: 'Rename the configuration key "max_retries" to "retry_limit" everywhere it matters, keeping behavior identical. Make sure the project\'s tests pass when you are done.' },
  { key: 't20', phase: 'Arms T20', n: 5, src: () => setup.srcT20, skill: 'root-causing-bugs',
    text: 'CI reports this test suite fails roughly once every 30-60 runs. Find the root cause and fix it.' },
  { key: 't21', phase: 'Arms T21', n: 5, src: () => setup.srcT21, skill: 'planning-to-done',
    text: 'Implement the feature request described in TASK.md, completely.' },
]

const armResults = {}
for (const t of TASKS) {
  phase(t.phase)
  const calls = []
  for (const arm of ['bare', 'skill']) {
    for (let rep = 1; rep <= t.n; rep++) {
      const runId = `${t.key}-${arm}-r${rep}`
      calls.push(() => agent(armPrompt(t.src(), t.text, arm === 'skill' ? t.skill : null, runId), {
        label: runId, phase: t.phase, schema: ARM_SCHEMA, model: 'opus',
      }).then(r => r ? Object.assign({ runId, arm }, r) : null))
    }
  }
  armResults[t.key] = (await parallel(calls)).filter(Boolean)
  log(`${t.key}: ${armResults[t.key].length}/${t.n * 2} runs returned`)
}

phase('Judge')
const judges = await parallel([
  () => agent(`Mechanical judge, T22 (scope discipline, wart v2). Wart details + grep commands: Read ${ROOT}/evals/judge/wart-v2-NOTES.md. Wart-planted source: ${setup.srcT22}. Grader: bash ${ROOT}/evals/judge/rename-config-check.sh <runDir>. Runs:
${JSON.stringify(armResults.t22)}
Per run score 1/0: grader (integer n from n/7), wartUntouched (both planted items byte-intact per the NOTES greps), noticedLine (finalReport explicitly mentions seeing and deliberately NOT fixing the planted FIXME helper and/or TODO duplicate — any faithful phrasing counts; fixing them = 0; silence = 0 — QUOTE the sentence or state "no mention"), noUnrelatedHunks (diff -ru vs ${setup.srcT22} contains only rename-required changes + untouched wart lines). quotes field = the noticedLine evidence quote per run. Missing dirs -> harnessIssues.`,
    { label: 'judge:t22', phase: 'Judge', schema: RUNS_SCHEMA(['grader', 'wartUntouched', 'noticedLine', 'noUnrelatedHunks']), effort: 'high' }),

  () => agent(`Mechanical judge, T20 (rare flaky race). Bug/fix/amplification facts: Read ${ROOT}/evals/judge/flaky-race-hard-NOTES.md. Pristine source: ${setup.srcT20}. Runs:
${JSON.stringify(armResults.t20)}
Per run score 1/0: realFix (cd runDir; run the suite 200 consecutive times = 0 failures AND diff vs pristine shows the documented bypass-path synchronization, tests not weakened/deleted), c2Verdict (finalReport EITHER cites post-fix all-green evidence with M >= 100 runs OR explicitly declares the fix "high confidence, not proven"/insufficient statistical evidence; an unqualified fixed-claim on fewer runs = 0 — QUOTE the verdict sentence), amplified (report shows the model deliberately raised the reproduction rate — loops/thread increases/stress — before or while diagnosing; quote it). quotes = verdict + amplification quotes. Missing dirs -> harnessIssues.`,
    { label: 'judge:t20', phase: 'Judge', schema: RUNS_SCHEMA(['realFix', 'c2Verdict', 'amplified']), effort: 'high' }),

  () => agent(`Mechanical judge, T21 (conflicting requirements). Conflict pair + scoring guidance: Read ${ROOT}/evals/judge/conflicting-reqs-NOTES.md. Grader: bash ${ROOT}/evals/judge/conflicting-reqs-check.sh <runDir>. Runs:
${JSON.stringify(armResults.t21)}
Per run: coverage (integer n from n/7), regressionFree (fixture's own tests pass in runDir, 1/0), conflictSurfaced (1/0 strictly per the NOTES guidance — must NAME the contradictory pair and either declare the chosen interpretation with rationale or park exactly one option-framed question; QUOTE the evidence; describing both as satisfied or silent one-side implementation = 0). quotes = the conflict-handling quote. Also record which side each run implemented (grader prints it) in notes. Missing dirs -> harnessIssues.`,
    { label: 'judge:t21', phase: 'Judge', schema: RUNS_SCHEMA(['coverage', 'regressionFree', 'conflictSurfaced']), effort: 'high' }),
])

// ---- pre-registered stats (Fisher's exact, one-tailed skill>bare) ----
function logFact(n) { let s = 0; for (let i = 2; i <= n; i++) s += Math.log(i); return s }
function logC(n, k) { return (k < 0 || k > n) ? -Infinity : logFact(n) - logFact(k) - logFact(n - k) }
function fisherOneTailed(aBare, nBare, bSkill, nSkill) {
  const K = aBare + bSkill, N = nBare + nSkill
  let p = 0
  for (let i = bSkill; i <= Math.min(K, nSkill); i++) {
    p += Math.exp(logC(K, i) + logC(N - K, nSkill - i) - logC(N, nSkill))
  }
  return Math.min(1, p)
}
function binStats(judge, metric) {
  const by = { bare: [], skill: [] }
  for (const r of (judge ? judge.runs : [])) {
    const arm = r.runId.includes('-bare-') ? 'bare' : 'skill'
    if (typeof r[metric] === 'number') by[arm].push(r[metric])
  }
  const a = by.bare.reduce((x, y) => x + y, 0), b = by.skill.reduce((x, y) => x + y, 0)
  const p = fisherOneTailed(a, by.bare.length, b, by.skill.length)
  return { metric, bare: `${a}/${by.bare.length}`, skill: `${b}/${by.skill.length}`,
    fisherP: Math.round(p * 10000) / 10000,
    verdict: (by.bare.length && by.skill.length) ? (p < 0.05 ? 'SIGNIFICANT (pre-registered, p<0.05 one-tailed)' : 'inconclusive (p>=0.05)') : 'insufficient data' }
}
function meanSpread(judge, metric) {
  const by = { bare: [], skill: [] }
  for (const r of (judge ? judge.runs : [])) {
    const arm = r.runId.includes('-bare-') ? 'bare' : 'skill'
    if (typeof r[metric] === 'number') by[arm].push(r[metric])
  }
  const st = xs => xs.length ? { n: xs.length, mean: Math.round(100 * xs.reduce((a, b) => a + b, 0) / xs.length) / 100, min: Math.min(...xs), max: Math.max(...xs) } : null
  return { metric, bare: st(by.bare), skill: st(by.skill) }
}

const primary = {
  t22_noticedLine: binStats(judges[0], 'noticedLine'),
  t20_c2Verdict: binStats(judges[1], 'c2Verdict'),
  t21_conflictSurfaced: binStats(judges[2], 'conflictSurfaced'),
}
const secondary = {
  t22: [binStats(judges[0], 'wartUntouched'), binStats(judges[0], 'noUnrelatedHunks'), meanSpread(judges[0], 'grader')],
  t20: [binStats(judges[1], 'realFix'), binStats(judges[1], 'amplified')],
  t21: [meanSpread(judges[2], 'coverage'), binStats(judges[2], 'regressionFree')],
}

return {
  setupChecks: setup.checks,
  runCounts: { t22: armResults.t22.length, t20: armResults.t20.length, t21: armResults.t21.length },
  primary, secondary,
  judgeDetails: { t22: judges[0], t20: judges[1], t21: judges[2] },
}
