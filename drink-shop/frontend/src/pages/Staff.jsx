import { useCallback, useEffect, useState } from 'react'
import { api, fmtDateTime } from '../api'
import MonthPicker, { thisMonth } from '../MonthPicker'

export default function Staff() {
  const [status, setStatus] = useState(null)
  const [ym, setYm] = useState(thisMonth())
  const [report, setReport] = useState(null)
  const [err, setErr] = useState('')
  const [clock, setClock] = useState(new Date())

  useEffect(() => {
    const t = setInterval(() => setClock(new Date()), 1000)
    return () => clearInterval(t)
  }, [])

  const loadStatus = useCallback(() => api('/attendance/status').then(setStatus).catch((e) => setErr(e.message)), [])
  const loadReport = useCallback(
    () => api(`/attendance/monthly?year=${ym.year}&month=${ym.month}`).then(setReport).catch((e) => setErr(e.message)),
    [ym],
  )
  useEffect(() => { loadStatus() }, [loadStatus])
  useEffect(() => { loadReport() }, [loadReport])

  const punch = async (kind) => {
    setErr('')
    try {
      await api(`/attendance/${kind}`, { method: 'POST' })
      await Promise.all([loadStatus(), loadReport()])
    } catch (e) {
      setErr(e.message)
    }
  }

  return (
    <div>
      <h2>打卡 / 工時查詢</h2>
      <div className="card punch">
        <div className="clock">{clock.toLocaleTimeString('zh-TW', { hour12: false })}</div>
        {status && (
          <>
            <div className={`state ${status.on_duty ? 'on' : 'off'}`}>
              {status.on_duty ? `● 上班中（${fmtDateTime(status.current.clock_in)} 打卡）` : '○ 未上班'}
            </div>
            <div className="muted">今日已工作 {status.today_hours} 小時</div>
            <div className="row center">
              <button className="primary" disabled={status.on_duty} onClick={() => punch('clock-in')}>上班打卡</button>
              <button className="danger" disabled={!status.on_duty} onClick={() => punch('clock-out')}>下班打卡</button>
            </div>
          </>
        )}
        {err && <div className="error">{err}</div>}
      </div>

      <div className="toolbar"><MonthPicker value={ym} onChange={setYm} /></div>
      {report && <AttendanceReport report={report} />}
    </div>
  )
}

export function AttendanceReport({ report }) {
  return (
    <>
      <div className="stats">
        <div className="stat card"><span>本月總工時</span><b>{report.total_hours} 小時</b></div>
        <div className="stat card"><span>班次</span><b>{report.shifts}</b></div>
        <div className="stat card"><span>出勤天數</span><b>{report.days_worked}</b></div>
      </div>
      {report.records.length === 0 ? (
        <p className="muted">本月沒有打卡紀錄</p>
      ) : (
        <table>
          <thead><tr><th>日期</th><th>上班打卡</th><th>下班打卡</th><th>時數</th><th>狀態</th></tr></thead>
          <tbody>
            {report.records.map((r) => (
              <tr key={r.id}>
                <td>{r.clock_in.slice(0, 10)}</td>
                <td>{r.clock_in.slice(11, 16)}</td>
                <td>{r.clock_out ? r.clock_out.slice(11, 16) : '—'}</td>
                <td>{r.hours ?? '—'}</td>
                <td>{r.clock_out ? <span className="tag ok">已完成</span> : <span className="tag warn">上班中</span>}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </>
  )
}
