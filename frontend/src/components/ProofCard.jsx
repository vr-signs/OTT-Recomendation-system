export default function ProofCard({ proof }) {
  return (
    <div className="proof-card">
      <div className="proof-kicker">VERIFIED AXIOM</div>
      <h3>{proof.property}</h3>
      <code>{proof.formula}</code>
      <p>{proof.mathematical_proof}</p>
    </div>
  )
}
