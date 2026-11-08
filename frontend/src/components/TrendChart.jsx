// Dependency-free SVG line chart: one line per subject across the quarters.
const COLORS = ['#0f766e', '#b45309', '#4338ca', '#be123c', '#4d7c0f']
const W = 520, H = 240, L = 36, R = 16, T = 16, B = 32
const MIN = 60, MAX = 100

const x = (q) => L + ((q - 1) * (W - L - R)) / 3
const y = (v) => T + ((MAX - Math.max(v, MIN)) / (MAX - MIN)) * (H - T - B)

export default function TrendChart({ subjects }) {
  const label = subjects.map((s) => `${s.name}: Q1 ${s.q1}, Q2 ${s.q2}`).join('. ')
  return (
    <>
      <svg className="trend-chart" viewBox={`0 0 ${W} ${H}`} role="img" aria-label={`Grade trend by subject. ${label}`}>
        {[60, 70, 80, 90, 100].map((v) => (
          <g key={v}>
            <line x1={L} x2={W - R} y1={y(v)} y2={y(v)} stroke="#d9dfd9" />
            <text x={L - 6} y={y(v) + 4} textAnchor="end" fontSize="11" fill="#5b6673">{v}</text>
          </g>
        ))}
        {[1, 2, 3, 4].map((q) => (
          <text key={q} x={x(q)} y={H - 10} textAnchor="middle" fontSize="12" fill="#5b6673">Q{q}</text>
        ))}
        {subjects.map((s, i) => (
          <g key={s.name}>
            <polyline
              points={`${x(1)},${y(s.q1)} ${x(2)},${y(s.q2)}`}
              fill="none" stroke={COLORS[i % COLORS.length]} strokeWidth="2.5" strokeLinecap="round"
            />
            <circle cx={x(1)} cy={y(s.q1)} r="4" fill={COLORS[i % COLORS.length]} />
            <circle cx={x(2)} cy={y(s.q2)} r="4" fill={COLORS[i % COLORS.length]} />
          </g>
        ))}
      </svg>
      <ul className="legend">
        {subjects.map((s, i) => (
          <li key={s.name}>
            <span className="swatch" style={{ background: COLORS[i % COLORS.length] }} />
            {s.name}
          </li>
        ))}
      </ul>
    </>
  )
}
