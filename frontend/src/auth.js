// Temporary front-end-only login so the screens can be tested before the API exists.
// Replace login() with a POST to the Django JWT endpoint, and keep the rest as is.
const KEY = 'gabay_user'

// Demo account (dummy data only): username "nanay", password "gabay123"
const DEMO_USERS = [{ username: 'nanay', password: 'gabay123', role: 'parent', name: 'Elena Cruz' }]

export const HOME_BY_ROLE = {
  parent: '/dashboard',
  // teacher: '/attendance', adviser: '/attendance'  (added when those screens are built)
}

export function currentUser() {
  try {
    return JSON.parse(sessionStorage.getItem(KEY) || localStorage.getItem(KEY))
  } catch {
    return null
  }
}

export async function login(username, password, remember) {
  await new Promise((r) => setTimeout(r, 300)) // pretend network delay
  const found = DEMO_USERS.find((u) => u.username === username && u.password === password)
  if (!found) throw new Error('Wrong username or password. Check them and try again.')

  const user = { username: found.username, role: found.role, name: found.name }
  logout()
  // "Remember me" keeps the session after the browser closes; otherwise it ends with the tab.
  ;(remember ? localStorage : sessionStorage).setItem(KEY, JSON.stringify(user))
  return user
}

export function logout() {
  sessionStorage.removeItem(KEY)
  localStorage.removeItem(KEY)
}
