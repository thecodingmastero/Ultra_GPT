import { NavLink } from 'react-router-dom'

const primaryLinks = [
  ['/', 'Landing'],
  ['/dashboard', 'Dashboard'],
  ['/ask-ai', 'Ask AI'],
  ['/portfolio-lab', 'Portfolio Lab'],
  ['/learn', 'Learn'],
  ['/profile', 'Profile'],
]

export function TopNav() {
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
        <NavLink to="/login" className="nav-link">
          Login
        </NavLink>
      </nav>
    </header>
  )
}
