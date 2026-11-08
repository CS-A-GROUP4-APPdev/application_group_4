import { useEffect, useState } from 'react'

export default function ConferenceModal({ childName, slots, current, onConfirm, onClose }) {
  const [slot, setSlot] = useState(current || slots[0])

  useEffect(() => {
    const onKey = (e) => e.key === 'Escape' && onClose()
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])

  return (
    <div className="modal-backdrop-g" onClick={onClose}>
      <div className="modal-card" role="dialog" aria-modal="true" aria-labelledby="conf-title" onClick={(e) => e.stopPropagation()}>
        <h2 id="conf-title" className="h5">Book a parent-teacher conference</h2>
        <p className="text-muted">Choose a time to meet about {childName}.</p>
        <fieldset className="mb-3">
          <legend className="visually-hidden">Available times</legend>
          {slots.map((s) => (
            <div className="form-check mb-1" key={s}>
              <input className="form-check-input" type="radio" name="slot" id={`slot-${s}`} checked={slot === s} onChange={() => setSlot(s)} />
              <label className="form-check-label" htmlFor={`slot-${s}`}>{s}</label>
            </div>
          ))}
        </fieldset>
        <div className="d-flex gap-2 justify-content-end">
          <button type="button" className="btn btn-outline-secondary" onClick={onClose}>Cancel</button>
          <button type="button" className="btn btn-primary" onClick={() => onConfirm(slot)}>Book this slot</button>
        </div>
      </div>
    </div>
  )
}
