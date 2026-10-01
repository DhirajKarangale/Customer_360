import { BrowserRouter as Router, Routes, Route, Navigate, useLocation, useNavigate } from 'react-router-dom'
import { useEffect } from 'react'
import Navbar from './components/Navbar'
import Footer from './components/layout/Footer'
import Login from './pages/Login'
import Home from './pages/Home'
import Profile from './pages/Profile'
import Policies from './pages/Policies'
import About from './pages/About'
import Chat from './pages/Chat'
import { useAppStore } from './store/useAppStore'
import { MessageSquare } from 'lucide-react'

function Layout() {
  const location = useLocation()
  const navigate = useNavigate()
  const showFooter = location.pathname !== '/login' && location.pathname !== '/'
  const showFloatingChat = location.pathname !== '/login' && location.pathname !== '/' && location.pathname !== '/chat'
  
  return (
    <div className="min-h-screen flex flex-col bg-background text-foreground transition-colors duration-300 relative">
      <Navbar />
      <main className="flex-1 flex flex-col w-full">
        <Routes>
          <Route path="/" element={<Navigate to="/home" replace />} />
          <Route path="/login" element={<Login />} />
          <Route path="/home" element={<Home />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/policies" element={<Policies />} />
          <Route path="/about" element={<About />} />
          <Route path="/chat" element={<Chat />} />
        </Routes>
      </main>
      {showFooter && <Footer />}
    </div>
  )
}

function App() {
  const theme = useAppStore(state => state.theme)

  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, [theme])

  return (
    <Router>
      <Layout />
    </Router>
  )
}

export default App
