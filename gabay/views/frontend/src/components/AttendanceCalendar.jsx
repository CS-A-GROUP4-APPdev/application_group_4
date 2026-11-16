const DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
const MARK = { present: 'P', absent: 'A', late: 'L', excused: 'E' }

function statusOf(att, day, weekday) {
  if (weekday === 0 || weekday === 6 || day > att.lastDay) return null
  if (att.absent.includes(day)) return 'absent'
  if (att.late.includes(day)) return 'late'
  if (att.excused.includes(day)) return 'excused'
  return 'present'
}

export default function AttendanceCalendar({ attendance }) {
  const { year, month } = attendance
  const first = new Date(year, month, 1).getDay()
  const total = new Date(year, month + 1, 0).getDate()
  const title = new Date(year, month, 1).toLocaleDateString('en-PH', { month: 'long', year: 'numeric' })

  const cells = []
  for (let i = 0; i < first; i++) cells.push(<div key={`b${i}`} className="cal-cell blank" />)
  for (let d = 1; d <= total; d++) {
    const s = statusOf(attendance, d, new Date(year, month, d).getDay())
    cells.push(
      <div key={d} className={`cal-cell ${s || ''}`} title={s ? `${d}: ${s}` : undefined}>
        {d}
        {s && <b aria-label={s}>{MARK[s]}</b>}
      </div>
    )
  }

  return (
    <div>
      <p className="fw-bold mb-2">{title}</p>
      <div className="cal">
        {DAYS.map((d) => <div key={d} className="cal-head">{d}</div>)}
        {cells}
      </div>
      <ul className="legend mt-2">
        <li><b>P</b> Present</li><li><b>A</b> Absent</li><li><b>L</b> Late</li><li><b>E</b> Excused</li>
      </ul>
    </div>
  )
}
