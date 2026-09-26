import { useTheme } from '../App.jsx'

const THEMES = ['Light', 'Dark', 'System']

export default function TopNav({ tabs, active, onTab }) {
  const { theme, setTheme } = useTheme()

  return (
    <nav className="liquid-nav" role="navigation" aria-label="Main navigation">
      <div className="nav-tabs">
        {tabs.map((t) => (
          <button
            key={t}
            className={`nav-tab${active === t ? ' active' : ''}`}
            onClick={() => onTab(t)}
            aria-current={active === t ? 'page' : undefined}
          >
            {t}
          </button>
        ))}
      </div>

      <div className="nav-divider" aria-hidden="true" />

      <div className="nav-tabs" role="group" aria-label="Appearance">
        {THEMES.map((t) => (
          <button
            key={t}
            className={`nav-tab theme-tab${theme === t ? ' active' : ''}`}
            onClick={() => setTheme(t)}
            aria-pressed={theme === t}
          >
            {t}
          </button>
        ))}
      </div>
    </nav>
  )
}
