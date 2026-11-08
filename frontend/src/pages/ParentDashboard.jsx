import { useState } from 'react'
import ParentNavbar from '../components/ParentNavbar.jsx'
import TrendChart from '../components/TrendChart.jsx'
import AttendanceCalendar from '../components/AttendanceCalendar.jsx'
import ConferenceModal from '../components/ConferenceModal.jsx'
import { currentUser } from '../auth.js'
import { CHILDREN, NOTICE_COUNT, REASONS } from '../data/mockParentData.js'

const LANGS = [['en', 'English'], ['fil', 'Filipino'], ['ceb', 'Bisaya']]
const mean = (list) => Math.round(list.reduce((a, b) => a + b, 0) / list.length)

function Trend({ q1, q2 }) {
  if (q2 > q1) return <span className="trend-up">▲ Up</span>
  if (q2 < q1) return <span className="trend-down">▼ Down</span>
  return <span className="trend-flat">● Steady</span>
}

export default function ParentDashboard() {
  const parentName = currentUser()?.name ?? 'Parent'
  const [childId, setChildId] = useState(CHILDREN[0].id)
  const [lang, setLang] = useState('en')
  const [reasons, setReasons] = useState(() => Object.fromEntries(CHILDREN.map((c) => [c.id, { ...c.reasons }])))
  const [acks, setAcks] = useState({})
  const [booked, setBooked] = useState(() => Object.fromEntries(CHILDREN.map((c) => [c.id, c.conference])))
  const [booking, setBooking] = useState(false)

  const child = CHILDREN.find((c) => c.id === childId)
  const given = reasons[childId]
  const absences = child.attendance.absent
  const pendingDay = absences.find((d) => !given[d])
  const reasonsGiven = absences.filter((d) => given[d]).length

  const avg = mean(child.subjects.map((s) => s.q2))
  const delta = avg - mean(child.subjects.map((s) => s.q1))

  const dateLabel = (d) =>
    new Date(child.attendance.year, child.attendance.month, d).toLocaleDateString('en-PH', { month: 'long', day: 'numeric' })

  const saveReason = (reason) =>
    setReasons({ ...reasons, [childId]: { ...given, [pendingDay]: reason } })

  const acknowledge = () =>
    setAcks({ ...acks, [childId]: new Date().toLocaleString('en-PH', { dateStyle: 'medium', timeStyle: 'short' }) })

  return (
    <>
      <ParentNavbar
        kids={CHILDREN} childId={childId} onChildChange={setChildId}
        parentName={parentName} noticeCount={NOTICE_COUNT}
      />

      <main className="container-xl py-4 d-grid gap-3">
        {/* Mobile child selector (the desktop one lives in the navbar) */}
        <select
          className="form-select d-lg-none" aria-label="Choose child"
          value={childId} onChange={(e) => setChildId(Number(e.target.value))}
        >
          {CHILDREN.map((c) => <option key={c.id} value={c.id}>{c.name}, Grade {c.grade}</option>)}
        </select>

        {pendingDay && (
          <section className="absence-banner d-md-flex align-items-center justify-content-between gap-3" aria-live="polite">
            <p className="mb-2 mb-md-0">
              <b>{child.name} was absent on {dateLabel(pendingDay)}.</b> What was the reason?
            </p>
            <div className="d-flex flex-wrap gap-2">
              {REASONS.map((r) => (
                <button key={r} type="button" className="btn btn-outline-dark btn-sm" onClick={() => saveReason(r)}>{r}</button>
              ))}
            </div>
          </section>
        )}

        <section className="d-flex flex-column flex-md-row justify-content-between align-items-md-start gap-2">
          <div>
            <h1 className="h3 mb-0">{child.name}</h1>
            <p className="text-muted mb-0">Grade {child.grade} · Section {child.section} · Quarter {child.quarter}</p>
          </div>
          {acks[childId] ? (
            <div className="text-md-end">
              <button type="button" className="btn btn-success w-100" disabled>✓ Acknowledged</button>
              <div className="small text-muted mt-1">{acks[childId]}</div>
            </div>
          ) : (
            <button type="button" className="btn btn-primary" onClick={acknowledge}>Acknowledge report card</button>
          )}
        </section>

        <section className="row g-3" aria-label="Summary">
          <div className="col-6 col-lg-3"><div className="panel h-100">
            <div className="stat-label">General average</div>
            <div className="stat-value">{avg}</div>
            <div className="stat-label">Change from last quarter: {delta > 0 ? '+' : delta < 0 ? '−' : ''}{Math.abs(delta)}</div>
          </div></div>
          <div className="col-6 col-lg-3"><div className="panel h-100">
            <div className="stat-label"><span className="d-lg-none">Attendance</span><span className="d-none d-lg-inline">Attendance rate</span></div>
            <div className="stat-value">{child.attendanceRate}%</div>
            <div className="stat-label d-none d-lg-block">This quarter</div>
          </div></div>
          <div className="col-6 col-lg-3"><div className="panel h-100">
            <div className="stat-label">Absences this month</div>
            <div className="stat-value">{absences.length}</div>
            <div className="stat-label d-none d-lg-block">Reasons given: {reasonsGiven} of {absences.length}</div>
          </div></div>
          <div className="col-6 col-lg-3"><div className="panel h-100">
            <div className="stat-label"><span className="d-lg-none">Conference</span><span className="d-none d-lg-inline">Parent-teacher conference</span></div>
            <div className="fw-bold my-1">{booked[childId] || 'No slot booked'}</div>
            <button type="button" className="btn btn-outline-primary btn-sm d-none d-lg-inline-block" onClick={() => setBooking(true)}>
              Book a slot
            </button>
          </div></div>
        </section>

        <div className="row g-3">
          <div className="col-lg-8 d-grid gap-3 align-content-start">
            <section className="panel" id="grades">
              <h2>Grades by subject</h2>

              {/* Desktop table */}
              <table className="table grades-table align-middle mb-0 d-none d-md-table">
                <thead>
                  <tr>
                    <th scope="col">Subject</th><th scope="col">Q1</th><th scope="col">Q2</th>
                    <th scope="col">Trend</th><th scope="col">Needed to pass</th>
                  </tr>
                </thead>
                <tbody>
                  {child.subjects.map((s) => (
                    <tr key={s.name}>
                      <th scope="row" className="fw-normal text-body">{s.name}</th>
                      <td>{s.q1}</td><td className="fw-bold">{s.q2}</td>
                      <td><Trend q1={s.q1} q2={s.q2} /></td><td>{s.needed}</td>
                    </tr>
                  ))}
                </tbody>
              </table>

              {/* Mobile compact list */}
              <table className="table grades-table align-middle mb-0 d-md-none">
                <thead>
                  <tr><th scope="col">Subject</th><th scope="col" className="text-end">Q2 · Needed to pass</th></tr>
                </thead>
                <tbody>
                  {child.subjects.map((s) => (
                    <tr key={s.name}>
                      <th scope="row" className="fw-normal text-body">{s.name}</th>
                      <td className="text-end">{s.q2} · {s.needed}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </section>

            <section className="panel">
              <h2>Grade trend</h2>
              <TrendChart subjects={child.subjects} />
            </section>
          </div>

          <div className="col-lg-4 d-grid gap-3 align-content-start">
            <section className="panel">
              <h2>This week in plain words</h2>
              <p lang={lang}>{child.summary[lang]}</p>
              <select className="form-select form-select-sm w-auto mb-2" aria-label="Summary language" value={lang} onChange={(e) => setLang(e.target.value)}>
                {LANGS.map(([code, name]) => <option key={code} value={code}>{name}</option>)}
              </select>
              <p className="small text-muted mb-0">Reviewed by the teacher before release.</p>
            </section>

            <section className="panel" id="attendance">
              <h2>Attendance this month</h2>
              <AttendanceCalendar attendance={child.attendance} />
            </section>

            <section className="panel">
              <h2>Good news</h2>
              <p className="mb-0">{child.goodNews}</p>
            </section>
          </div>
        </div>
      </main>

      {booking && (
        <ConferenceModal
          childName={child.name}
          slots={child.conferenceSlots}
          current={booked[childId]}
          onClose={() => setBooking(false)}
          onConfirm={(slot) => { setBooked({ ...booked, [childId]: slot }); setBooking(false) }}
        />
      )}
    </>
  )
}
