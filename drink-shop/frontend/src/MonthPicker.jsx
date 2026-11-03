export default function MonthPicker({ value, onChange }) {
  const shift = (d) => {
    let { year, month } = value
    month += d
    if (month < 1) { month = 12; year-- }
    if (month > 12) { month = 1; year++ }
    onChange({ year, month })
  }
  return (
    <span className="month-picker">
      <button onClick={() => shift(-1)}>‹</button>
      <b>{value.year} 年 {value.month} 月</b>
      <button onClick={() => shift(1)}>›</button>
    </span>
  )
}

export const thisMonth = () => {
  const d = new Date()
  return { year: d.getFullYear(), month: d.getMonth() + 1 }
}
