# Gabay frontend (React)

React + Vite + React Router + Bootstrap. Built from the approved wireframes.

## Run
```
cd frontend
npm install
npm run dev
```
Open the address shown in the terminal (usually http://localhost:5173).

The backend is not needed yet: the screens use dummy data and a front-end-only login.

## Demo login (dummy account)
| Username | Password | Role |
|---|---|---|
| `nanay` | `gabay123` | Parent |

Dummy accounts live in `src/auth.js`. They are replaced by the real login API later.

## Routes
| Path | Page | Status |
|---|---|---|
| `/` | redirects to `/login` | done |
| `/login` | Login (desktop and mobile layouts) | done, uses the demo login |
| `/dashboard` | Parent dashboard | done, uses dummy data; requires login |
| `/attendance` | Attendance encoding (teacher) | not built yet |
| `/grades` | Grade encoding (teacher) | not built yet |
| `/notices` | Notice list | not built yet |

Any unknown address goes to `/login`. A person who is not logged in and opens `/dashboard` is sent to `/login`.

## Folder guide
```
src/
├── main.jsx                  app entry (Bootstrap CSS first, then index.css)
├── App.jsx                   routes and the login guard
├── auth.js                   demo login, session storage, logout
├── index.css                 colors, fonts, and layout styles
├── pages/
│   ├── Login.jsx
│   └── ParentDashboard.jsx
├── components/
│   ├── ParentNavbar.jsx      top bar, hamburger menu, child selector, bell
│   ├── TrendChart.jsx        grade trend line chart (plain SVG, no library)
│   ├── AttendanceCalendar.jsx
│   └── ConferenceModal.jsx   "Book a slot" form
└── data/
    └── mockParentData.js     dummy children, grades, attendance, summaries
```

## What works on each screen

### Login
- A correct username and password goes to the dashboard for the user's role.
- A wrong password shows an error and stays on the page.
- An empty username or password shows a "required" message.
- "Remember me" keeps the session after the browser closes. Without it, the session ends when the tab closes.

### Parent dashboard
- The child selector switches all records to the chosen child (the demo parent has two).
- The absence banner appears for absences with no reason. Choosing a reason saves it and updates "Reasons given".
- "Acknowledge report card" saves the date and time and changes to "Acknowledged".
- The language box rewrites the summary in English, Filipino, or Bisaya.
- "Book a slot" (desktop only) opens the conference booking form.
- General average, change from last quarter, and trend arrows are calculated from the grades.

## Dummy data to replace with the API
| Dummy source | Replace with |
|---|---|
| `src/auth.js` `login()` | POST to the Django JWT login endpoint |
| `src/data/mockParentData.js` | The parent's linked students, grades, attendance, and summaries |
| Absence reasons, acknowledgment, booked slot (saved in page state) | Save endpoints on the backend |

The Filipino and Bisaya summaries in the dummy data are placeholders. Have a native speaker check them before use.

## Build check
```
npm run build
```
