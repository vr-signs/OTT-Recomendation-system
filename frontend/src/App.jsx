import { useState, useEffect, createContext, useContext } from 'react'
import TopNav from './components/TopNav.jsx'
import Overview from './pages/Overview.jsx'
import Coursework from './pages/Coursework.jsx'
import Data from './pages/Data.jsx'
import ModelLab from './pages/ModelLab.jsx'
import Studio from './pages/Studio.jsx'
import Analytics from './pages/Analytics.jsx'

// ── Theme Context ─────────────────────────────────────────────────────────────
const ThemeCtx = createContext(null)
export const useTheme = () => useContext(ThemeCtx)

const TABS = ['Overview', 'Coursework', 'Data', 'Model Lab', 'Studio', 'Analytics']

export default function App() {
  const [tab, setTab] = useState('Overview')
  const [theme, setTheme] = useState(() => localStorage.getItem('sg-theme') || 'System')

  // Apply theme to <html data-theme>
  useEffect(() => {
    const root = document.documentElement
    if (theme === 'Dark') {
      root.setAttribute('data-theme', 'dark')
    } else if (theme === 'Light') {
      root.removeAttribute('data-theme')
    } else {
      // System
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      prefersDark ? root.setAttribute('data-theme', 'dark') : root.removeAttribute('data-theme')
    }
    localStorage.setItem('sg-theme', theme)
  }, [theme])

  const page = {
    Overview: <Overview />,
    Coursework: <Coursework />,
    Data: <Data />,
    'Model Lab': <ModelLab />,
    Studio: <Studio />,
    Analytics: <Analytics />,
  }[tab] ?? <Overview />

  return (
    <ThemeCtx.Provider value={{ theme, setTheme }}>
      <div className="app-shell">
        <TopNav tabs={TABS} active={tab} onTab={setTab} />
        <main className="page-content">{page}</main>
        <footer className="app-footer">
          StreamGlass · OTT subscriber and personalized recommendation system · JNTUK R23 · TEAM-18
        </footer>
      </div>
    </ThemeCtx.Provider>
  )
}
