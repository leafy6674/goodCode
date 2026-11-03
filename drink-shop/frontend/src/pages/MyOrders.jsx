import { Fragment, useEffect, useMemo, useState } from 'react'
import { api, fmtDateTime, fmtMoney } from '../api'

export default function MyOrders() {
  const [data, setData] = useState(null)
  const [err, setErr] = useState('')
  const [month, setMonth] = useState('all')
  const [open, setOpen] = useState(null)

  useEffect(() => {
    api('/orders/me').then(setData).catch((e) => setErr(e.message))
  }, [])

  const months = useMemo(
    () => [...new Set((data?.orders || []).map((o) => o.created_at.slice(0, 7)))],
    [data],
  )
  const shown = (data?.orders || []).filter((o) => month === 'all' || o.created_at.startsWith(month))

  if (err) return <div className="error">{err}</div>
  if (!data) return <p>載入中…</p>

  return (
    <div>
      <h2>我的訂單 <small className="muted">（近 12 個月：{data.since.slice(0, 10)} ~ {data.until.slice(0, 10)}）</small></h2>
      <div className="stats">
        <div className="stat card"><span>訂單數</span><b>{data.count}</b></div>
        <div className="stat card"><span>累計消費</span><b>{fmtMoney(data.total_spent)}</b></div>
      </div>
      <div className="toolbar">
        月份篩選：
        <select value={month} onChange={(e) => setMonth(e.target.value)}>
          <option value="all">全部</option>
          {months.map((m) => <option key={m}>{m}</option>)}
        </select>
        <span className="muted">顯示 {shown.length} 筆</span>
      </div>
      {shown.length === 0 ? (
        <p className="muted">沒有訂單</p>
      ) : (
        <table>
          <thead><tr><th>訂單編號</th><th>時間</th><th>品項</th><th>金額</th><th></th></tr></thead>
          <tbody>
            {shown.map((o) => (
              <Fragment key={o.id}>
                <tr>
                  <td>#{o.id}</td>
                  <td>{fmtDateTime(o.created_at)}</td>
                  <td>{o.items.map((i) => i.product_name).join('、')}</td>
                  <td>{fmtMoney(o.total)}</td>
                  <td><button className="link" onClick={() => setOpen(open === o.id ? null : o.id)}>
                    {open === o.id ? '收合' : '明細'}</button></td>
                </tr>
                {open === o.id && (
                  <tr className="detail">
                    <td colSpan="5">
                      {o.items.map((i, idx) => (
                        <div key={idx}>
                          {i.product_name}（{i.sugar} / {i.ice}）× {i.quantity} — {fmtMoney(i.unit_price * i.quantity)}
                        </div>
                      ))}
                    </td>
                  </tr>
                )}
              </Fragment>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
