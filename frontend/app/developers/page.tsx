export default function DevelopersPage() {
  return (
    <main style={{maxWidth:980,margin:"0 auto",padding:"64px 24px",fontFamily:"Arial,sans-serif",lineHeight:1.55}}>
      <p style={{fontWeight:800,letterSpacing:1.4}}>PROOFJUDGE INTEGRATION KIT</p>
      <h1 style={{fontSize:52,lineHeight:1.05}}>Composable milestone settlement for dApps and agents.</h1>
      <p style={{fontSize:20}}>V5 adds ordered milestone dependencies, machine-readable project progress, neutral participant settlement stats, and a reusable TypeScript SDK.</p>
      <h2>Ordered project chains</h2><p>Each stage escrows its own GEN. A later stage cannot submit evidence until the prior stage is actually PAID.</p>
      <h2>Machine-readable state</h2><p><code>get_project_progress</code>, <code>get_project_job_id</code>, and <code>get_participant_stats</code> let other products compose ProofJudge without scraping the UI.</p>
      <h2>SDK</h2><pre style={{whiteSpace:"pre-wrap",padding:20,background:"#111",color:"#fff",borderRadius:12}}>{`const pj = new ProofJudgeClient({ address: V5_ADDRESS });\nconst progress = await pj.getProjectProgress("website-redesign");\nconst jobs = await pj.listProject("website-redesign");`}</pre>
      <h2>Promotion gate</h2><p>V5 is not made canonical until regression tests, GenVM lint, SDK tests, frontend build, live two-stage Studionet settlement, and deployed-source equality all pass.</p>
      <p><a href="https://github.com/maho0638/proofjudge-genlayer/tree/main/sdk">SDK source ↗</a> · <a href="https://github.com/maho0638/proofjudge-genlayer/blob/main/docs/MILESTONE_V5.md">Milestone plan ↗</a> · <a href="/">Back ↗</a></p>
    </main>
  );
}
