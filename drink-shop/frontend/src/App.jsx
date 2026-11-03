import { Navigate, NavLink, Route, Routes } from 'react-router-dom'
import { homeFor, useAuth } from './AuthContext'
import Login from './pages/Login'
import Menu from './pages/Menu'
import MyOrders from './pages/MyOrders'
import Staff from './pages/Staff'
import Manager from './pages/Manager'

const ROLE_LABEL = { customer: '會員', staff: '店員', manager: '店長' }

function Guard({ roles, children }) {
  const { user } = useAuth()
  if (!user) return <Navigate to="/login" replace />
  if (!roles.includes(user.role)) return <Navigate to={homeFor(user.role)} replace />
  return children
}

export default function App() {
  const { user, logout } = useAuth()
  return (
    <>
      <header className="topbar">
        <div className="brand">🧋 好茶飲料店</div>
        <nav>
          <NavLink to="/menu">菜單</NavLink>
          {user?.role === 'customer' && <NavLink to="/orders">我的訂單</NavLink>}
          {(user?.role === 'staff' || user?.role === 'manager') && (
            <NavLink to="/staff">打卡 / 工時</NavLink>
          )}
          {user?.role === 'manager' && <NavLink to="/manager">營運報表</NavLink>}
        </nav>
        <div className="userbox">
          {user ? (
            <>
              <span className={`badge ${user.role}`}>{ROLE_LABEL[user.role]}</span>
              <span>{user.name}</span>
              <button className="link" onClick={logout}>登出</button>
            </>
          ) : (
            <NavLink to="/login">登入 / 註冊</NavLink>
          )}
        </div>
      </header>
      <main className="container">
        <Routes>
          <Route path="/" element={<Navigate to={user ? homeFor(user.role) : '/menu'} replace />} />
          <Route path="/login" element={<Login />} />
          <Route path="/menu" element={<Menu />} />
          <Route path="/orders" element={<Guard roles={['customer']}><MyOrders /></Guard>} />
          <Route path="/staff" element={<Guard roles={['staff', 'manager']}><Staff /></Guard>} />
          <Route path="/manager" element={<Guard roles={['manager']}><Manager /></Guard>} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </>
  )
}
