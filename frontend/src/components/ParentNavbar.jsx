import { useState } from 'react'

const LINKS = [
  ['Dashboard', '/dashboard'],
  ['Grades', '#grades'],
  ['Attendance', '#attendance'],
  ['Notices', '#notices'],
]

export default function ParentNavbar({ kids, childId, onChildChange, parentName, noticeCount }) {
  const [open, setOpen] = useState(false)

  return (
    <header className="gabay-nav">
      <div className="container-xl d-flex align-items-center gap-3 py-2">
        <button
          type="button"
          className="btn btn-link d-lg-none p-0 nav-toggle"
          aria-label="Menu"
          aria-expanded={open}
          aria-controls="main-menu"
          onClick={() => setOpen(!open)}
        >
          ☰
        </button>
        <span className="logo-box d-none d-lg-flex">LOGO</span>
        <span className="brand">Gabay</span>

        <nav id="main-menu" className={`nav-links ${open ? 'open' : ''}`} aria-label="Main">
          {LINKS.map(([label, href]) => (
            <a key={label} href={href} aria-current={label === 'Dashboard' ? 'page' : undefined}>
              {label}
            </a>
          ))}
        </nav>

        <div className="ms-auto d-flex align-items-center gap-3">
          <select
            className="form-select form-select-sm d-none d-lg-block"
            aria-label="Choose child"
            value={childId}
            onChange={(e) => onChildChange(Number(e.target.value))}
          >
            {kids.map((k) => (
              <option key={k.id} value={k.id}>{k.name}, Grade {k.grade}</option>
            ))}
          </select>
          <a href="#notices" className="bell" aria-label={`Notices, ${noticeCount} new`}>
            🔔<span className="badge rounded-pill">{noticeCount}</span>
          </a>
          <span className="d-none d-lg-inline small text-nowrap">Parent: {parentName}</span>
        </div>
      </div>
    </header>
  )
}
