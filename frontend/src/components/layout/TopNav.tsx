import { NavLink, useNavigate } from 'react-router-dom'
import { clearAuthToken, isAuthenticated } from '../../services/auth'
import { Button } from '../common/Button'

const primaryLinks = [
  ['/', 'Landing'],
  ['/dashboard', 'Dashboard'],
  ['/ask-ai', 'Ask AI'],
  ['/portfolio-lab', 'Portfolio Lab'],
  ['/learn', 'Learn'],
  ['/profile', 'Profile'],
]

export function TopNav() {
  const navigate = useNavigate()
  const loggedIn = isAuthenticated()

  const logout = () => {
    clearAuthToken()
    void fetch(`${import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:5000'}/api/auth/logout`, {
      method: 'POST',
    }).catch(() => undefined)
    navigate('/login')
  }

  return (
    <header className="top-nav">
      <div>
        <p className="top-nav__eyebrow">The Better Investor</p>
        <h1>Smarter Investing Starts Here.</h1>
      </div>
      <nav>
        {primaryLinks.map(([to, label]) => (
          <NavLink key={to} to={to} className={({ isActive }) => (isActive ? 'nav-link nav-link--active' : 'nav-link')} end={to === '/'}>
            {label}
          </NavLink>
        ))}
        {loggedIn ? (
          <Button variant="secondary" onClick={logout}>
            Logout
          </Button>
        ) : (
          <>
            <NavLink to="/login" className="nav-link">
              Login
            </NavLink>
            <NavLink to="/register" className="nav-link">
              Register
            </NavLink>
          </>
        )}
      </nav>
    </header>
  )
}
