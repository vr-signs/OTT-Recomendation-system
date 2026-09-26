export default function PipelineStep({ label, title, copy, color }) {
  return (
    <section className="pipeline-step" style={{ '--step-color': color }}>
      <div className="step-label">{label}</div>
      <h3>{title}</h3>
      <p>{copy}</p>
    </section>
  )
}
