import { useEffect, useState } from 'react'
import { api, fmtMoney } from '../api'
import MonthPicker, { thisMonth } from '../MonthPicker'
import { AttendanceReport } from './Staff'

const iso = (d) => d.toISOString().slice(0, 10)
const daysAgo = (n) => { const d = new Date(); d.setDate(d.getDate() - n); return iso(d) }

function Bars({ data, label, value, fmt = (v) => v }) {
  const max = Math.max(1, ...data.map(value))
  const step = Math.ceil(data.length / 12)
  return (
    <div className="bars">
      {data.map((d, i) => (
        <div key={i} className="bar-col" title={`${label(d)}：${fmt(value(d))}`}>
          <div className="bar" style={{ height: `${(value(d) / max) * 100}%` }} />
          <div className="bar-label">{i % step === 0 ? label(d) : '\u00a0'}</div>
        </div>
      ))}
    </div>
  )
}

export default function Manager() {
  const [tab, setTab] = useState('ops')
  return (
    <div>
      <h2>店長營運資料</h2>
      <div className="tabs">
        <button className={tab === 'ops' ? 'active' : ''} onClick={() => setTab('ops')}>營運報表</button>
        <button className={tab === 'staff' ? 'active' : ''} onClick={() => setTab('staff')}>員工工時</button>
      </div>
      {tab === 'ops' ? <Ops /> : <StaffHours />}
    </div>
  )
}

function Ops() {
  const [range, setRange] = useState({ start: daysAgo(29), end: daysAgo(0) })
  const [s, setS] = useState(null)
  const [monthly, setMonthly] = useState([])
  const [err, setErr] = useState('')

  useEffect(() => {
    setErr('')
    api(`/manager/summary?start=${range.start}&end=${range.end}`).then(setS).catch((e) => setErr(e.message))
  }, [range])
  useEffect(() => { api('/manager/monthly-revenue?months=12').then(setMonthly) }, [])

  const preset = (n) => setRange({ start: daysAgo(n - 1), end: daysAgo(0) })

  return (
    <>
      <div className="toolbar">
        <input type="date" value={range.start} onChange={(e) => setRange({ ...range, start: e.target.value })} />
        ~
        <input type="date" value={range.end} onChange={(e) => setRange({ ...range, end: e.target.value })} />
        <button onClick={() => preset(1)}>今日</button>
        <button onClick={() => preset(7)}>近 7 天</button>
        <button onClick={() => preset(30)}>近 30 天</button>
      </div>
      {err && <div className="error">{err}</div>}
      {s && (
        <>
          <div className="stats">
            <div className="stat card"><span>營業額</span><b>{fmtMoney(s.revenue)}</b></div>
            <div className="stat card"><span>訂單數</span><b>{s.order_count}</b></div>
            <div className="stat card"><span>客單價</span><b>{fmtMoney(s.avg_order_value)}</b></div>
            <div className="stat card"><span>售出杯數</span><b>{s.cups_sold}</b></div>
            <div className="stat card"><span>會員訂單比例</span>
              <b>{s.order_count ? Math.round((s.member_orders / s.order_count) * 100) : 0}%</b></div>
          </div>
          <div className="two-col">
            <div className="card">
              <h3>每日營收</h3>
              <Bars data={s.daily} label={(d) => d.date.slice(5)} value={(d) => d.revenue} fmt={fmtMoney} />
            </div>
            <div className="card">
              <h3>熱銷商品 Top 10</h3>
              <table>
                <thead><tr><th>#</th><th>商品</th><th>杯數</th><th>營收</th></tr></thead>
                <tbody>
                  {s.top_products.map((p, i) => (
                    <tr key={p.product_name}><td>{i + 1}</td><td>{p.product_name}</td><td>{p.quantity}</td><td>{fmtMoney(p.revenue)}</td></tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
          <div className="card">
            <h3>時段訂單分佈</h3>
            <Bars data={s.hourly.filter((h) => h.hour >= 8 && h.hour <= 22)} label={(d) => `${d.hour}時`} value={(d) => d.orders} />
          </div>
        </>
      )}
      <div className="card">
        <h3>近 12 個月營收</h3>
        <Bars data={monthly} label={(d) => d.month.slice(2)} value={(d) => d.revenue} fmt={fmtMoney} />
      </div>
    </>
  )
}

function StaffHours() {
  const [ym, setYm] = useState(thisMonth())
  const [rows, setRows] = useState([])
  const [detail, setDetail] = useState(null)
  const [form, setForm] = useState({ username: '', password: '', name: '' })
  const [msg, setMsg] = useState('')

  const load = () => api(`/manager/staff-hours?year=${ym.year}&month=${ym.month}`).then(setRows)
  useEffect(() => { load(); setDetail(null) }, [ym])

  const showDetail = async (r) => {
    const rep = await api(`/manager/staff/${r.staff_id}/monthly?year=${ym.year}&month=${ym.month}`)
    setDetail({ name: r.name, rep })
  }
  const addStaff = async (e) => {
    e.preventDefault()
    try {
      await api('/manager/staff', { method: 'POST', body: form })
      setMsg(`已新增店員 ${form.name}`)
      setForm({ username: '', password: '', name: '' })
      load()
    } catch (ex) {
      setMsg(ex.message)
    }
  }

  return (
    <>
      <div className="toolbar"><MonthPicker value={ym} onChange={setYm} /></div>
      <table>
        <thead><tr><th>姓名</th><th>帳號</th><th>目前狀態</th><th>總工時</th><th>班次</th><th>出勤天數</th><th></th></tr></thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.staff_id}>
              <td>{r.name}</td><td>{r.username}</td>
              <td>{r.on_duty ? <span className="tag warn">上班中</span> : <span className="tag">未上班</span>}</td>
              <td>{r.total_hours} 小時</td><td>{r.shifts}</td><td>{r.days_worked}</td>
              <td><button className="link" onClick={() => showDetail(r)}>打卡明細</button></td>
            </tr>
          ))}
        </tbody>
      </table>
      {detail && (
        <div className="card">
          <h3>{detail.name} — {ym.year}/{ym.month} 打卡明細</h3>
          <AttendanceReport report={detail.rep} />
        </div>
      )}
      <form className="card inline-form" onSubmit={addStaff}>
        <h3>新增店員帳號</h3>
        <input placeholder="帳號" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} required />
        <input placeholder="密碼 (至少 6 碼)" type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required />
        <input placeholder="姓名" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
        <button className="primary">新增</button>
        {msg && <span className="muted">{msg}</span>}
      </form>
    </>
  )
}
