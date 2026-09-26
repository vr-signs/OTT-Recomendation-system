/**
 * DataTable — renders API data (columns + rows) as a responsive HTML table.
 * Handles arrays, objects, and long strings gracefully.
 */

function renderCell(value) {
  if (value === null || value === undefined) return '—'
  if (Array.isArray(value)) return value.join(', ')
  if (typeof value === 'object') return JSON.stringify(value)
  return String(value)
}

export default function DataTable({ columns, rows, maxHeight = 360 }) {
  if (!columns || !rows) return <p style={{ color: 'var(--muted)', fontSize: '0.85rem' }}>No data.</p>

  return (
    <div className="data-surface" style={{ maxHeight, overflowY: 'auto' }}>
      <table className="data-table">
        <thead>
          <tr>
            {columns.map((col) => (
              <th key={col}>{col.replace(/_/g, ' ')}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i}>
              {columns.map((col) => (
                <td key={col} title={renderCell(row[col])}>
                  {renderCell(row[col])}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
