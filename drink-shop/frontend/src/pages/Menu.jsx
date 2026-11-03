import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { api, fmtMoney } from '../api'
import { useAuth } from '../AuthContext'

export default function Menu() {
  const { user } = useAuth()
  const [products, setProducts] = useState([])
  const [opts, setOpts] = useState({ sugar: [], ice: [] })
  const [cart, setCart] = useState([])
  const [msg, setMsg] = useState('')
  const [err, setErr] = useState('')

  useEffect(() => {
    api('/products').then(setProducts).catch((e) => setErr(e.message))
    api('/options').then(setOpts)
  }, [])

  const grouped = useMemo(() => {
    const g = {}
    products.forEach((p) => (g[p.category] ||= []).push(p))
    return g
  }, [products])

  const add = (p) =>
    setCart([...cart, { key: crypto.randomUUID(), product: p, quantity: 1, sugar: '正常糖', ice: '正常冰' }])
  const update = (key, patch) => setCart(cart.map((c) => (c.key === key ? { ...c, ...patch } : c)))
  const remove = (key) => setCart(cart.filter((c) => c.key !== key))
  const total = cart.reduce((s, c) => s + c.product.price * c.quantity, 0)

  const checkout = async () => {
    setErr('')
    setMsg('')
    try {
      const o = await api('/orders', {
        method: 'POST',
        body: {
          items: cart.map((c) => ({
            product_id: c.product.id, quantity: c.quantity, sugar: c.sugar, ice: c.ice,
          })),
        },
      })
      setCart([])
      setMsg(`下單成功！訂單編號 #${o.id}，金額 ${fmtMoney(o.total)}`)
    } catch (e) {
      setErr(e.message)
    }
  }

  return (
    <div className="menu-layout">
      <section>
        <h2>飲品菜單</h2>
        {Object.entries(grouped).map(([cat, items]) => (
          <div key={cat}>
            <h3 className="cat">{cat}</h3>
            <div className="grid">
              {items.map((p) => (
                <div key={p.id} className="card product">
                  <div className="pname">{p.name}</div>
                  <div className="price">{fmtMoney(p.price)}</div>
                  {user?.role === 'customer' && <button onClick={() => add(p)}>加入</button>}
                </div>
              ))}
            </div>
          </div>
        ))}
      </section>
      <aside className="card cart">
        <h3>購物車</h3>
        {user?.role !== 'customer' ? (
          <p className="muted">
            {user ? '僅會員可線上點餐。' : <><Link to="/login">登入會員</Link> 後即可線上點餐。</>}
          </p>
        ) : cart.length === 0 ? (
          <p className="muted">尚未選擇飲品</p>
        ) : (
          <>
            {cart.map((c) => (
              <div key={c.key} className="cart-item">
                <div className="row">
                  <b>{c.product.name}</b>
                  <button className="link" onClick={() => remove(c.key)}>移除</button>
                </div>
                <div className="row">
                  <select value={c.sugar} onChange={(e) => update(c.key, { sugar: e.target.value })}>
                    {opts.sugar.map((s) => <option key={s}>{s}</option>)}
                  </select>
                  <select value={c.ice} onChange={(e) => update(c.key, { ice: e.target.value })}>
                    {opts.ice.map((s) => <option key={s}>{s}</option>)}
                  </select>
                  <input type="number" min="1" max="50" value={c.quantity}
                    onChange={(e) => update(c.key, { quantity: Math.max(1, +e.target.value || 1) })} />
                </div>
              </div>
            ))}
            <div className="row total"><span>合計</span><b>{fmtMoney(total)}</b></div>
            <button className="primary" onClick={checkout}>送出訂單</button>
          </>
        )}
        {msg && <div className="success">{msg}</div>}
        {err && <div className="error">{err}</div>}
      </aside>
    </div>
  )
}
