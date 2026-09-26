import PipelineStep from '../components/PipelineStep.jsx'

const TEAM = [
  { name: 'Kovvuri Venkata Reddy', roll: '25B21A4502' },
  { name: 'Pantadi H. Durga Prasad', roll: '25B21A4503' },
  { name: 'Battula Sravan Kumar', roll: '25B21A4501' },
  { name: 'Bodireddy Kanaka Mani', roll: '25B21A4504' },
  { name: 'Kapa Kumar', roll: '25B21A4506' },
]

const PIPELINE = [
  {
    label: 'DBMS',
    title: 'Relational ingestion',
    copy: '3NF SQLite schema records subscribers, titles, and watch events.',
    color: '#0071e3',
  },
  {
    label: 'DMGT',
    title: 'Quotient partitioning',
    copy: 'Equivalence classes protect language–genre diversity in discovery.',
    color: '#248a3d',
  },
  {
    label: 'ADSA',
    title: 'Co-watch topology',
    copy: 'Weighted adjacency lists surface bridge titles and neighbor paths.',
    color: '#b25000',
  },
  {
    label: 'OOPJ + ML',
    title: 'Hybrid scoring',
    copy: 'Cosine similarity and graph centrality shape personal relevance.',
    color: '#5c5ce2',
  },
]

export default function Overview() {
  return (
    <div className="overview-page">
      <div className="brandline">
        <span className="brand-mark">SG</span>
        <span>StreamGlass</span>
        <span className="brand-divider"></span>
        <span>OTT intelligence platform</span>
      </div>

      <header className="page-header">
        <div className="eyebrow">Personalized discovery, made legible</div>
        <h1 className="page-title">A calmer way to understand an OTT recommendation engine.</h1>
        <p className="page-desc">
          StreamGlass brings the subscriber, catalog, and recommendation model into one focused
          academic product—without hiding the mathematics behind the interface.
        </p>
      </header>

      <div className="grid-overview">
        <section className="surface card">
          <h3 className="section-title">Why StreamGlass exists</h3>
          <blockquote className="quote">
            A regional streaming platform should not present the same popular list to every viewer.
          </blockquote>
          <p className="body-copy">
            The system counters catalog starvation by accounting for language, genre, historic
            interactions, and the relationships that form in co-watch behavior.
          </p>
          <ul className="bullet-list">
            <li>
              <strong>Regional relevance</strong> supports primary and secondary language affinity.
            </li>
            <li>
              <strong>Catalog diversity</strong> is preserved through equivalence-class partitioning.
            </li>
            <li>
              <strong>Transparent ranking</strong> exposes the signals behind every recommendation.
            </li>
          </ul>
        </section>

        <section className="surface card">
          <h3 className="section-title">Project dossier</h3>
          <div className="people-list">
            {TEAM.map((person) => (
              <div key={person.roll} className="person-row">
                <span>{person.name}</span>
                <code className="roll-badge">{person.roll}</code>
              </div>
            ))}
          </div>
        </section>
      </div>

      <div className="section-heading">
        <div>
          <h2>The intelligence pipeline</h2>
          <p>Four academic perspectives, connected in a single recommendation flow.</p>
        </div>
      </div>

      <div className="grid-4">
        {PIPELINE.map((step) => (
          <PipelineStep
            key={step.label}
            label={step.label}
            title={step.title}
            copy={step.copy}
            color={step.color}
          />
        ))}
      </div>
    </div>
  )
}
