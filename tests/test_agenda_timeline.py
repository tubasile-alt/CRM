import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AGENDA_JS = ROOT / 'static' / 'js' / 'agenda.js'


def run_day_layout_script(body):
    bootstrap = f"""
const fs = require('fs');
global.window = global;
global.document = {{
  addEventListener: () => {{}},
  querySelector: () => null,
  getElementById: () => null
}};
global.localStorage = {{ getItem: () => null, setItem: () => {{}}, removeItem: () => {{}} }};
global.setInterval = () => 0;
eval(fs.readFileSync({json.dumps(str(AGENDA_JS))}, 'utf8'));
const rowsSummary = rows => rows.map(row => row.type === 'free'
  ? 'livre ' + String(Math.floor(row.min / 60)).padStart(2, '0') + ':' + String(row.min % 60).padStart(2, '0')
  : 'consulta ' + row.app.id);
{body}
"""
    result = subprocess.run(
        ['node', '-e', bootstrap],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


class AgendaDayLayoutTest(unittest.TestCase):
    def test_simultaneous_appointments_are_all_listed_at_the_same_time(self):
        result = run_day_layout_script("""
const apps = [
  { id: 1, start: '2026-10-23T09:00:00', end: '2026-10-23T09:30:00' },
  { id: 2, start: '2026-10-23T09:00:00', end: '2026-10-23T09:15:00' },
  { id: 3, start: '2026-10-23T10:00:00', end: '2026-10-23T10:15:00' }
];
const rows = rowsSummary(__agendaDayLayout.buildDayRows(apps, true));
const from = rows.indexOf('livre 08:45');
console.log(JSON.stringify(rows.slice(from, from + 7)));
""")

        # As duas consultas das 09:00 aparecem juntas; 09:15 fica coberto pela consulta de 30 min.
        self.assertEqual(result, [
            'livre 08:45', 'consulta 1', 'consulta 2', 'livre 09:30', 'livre 09:45',
            'consulta 3', 'livre 10:15',
        ])

    def test_short_appointments_reserve_at_least_one_fifteen_minute_slot(self):
        result = run_day_layout_script("""
const apps = [
  { id: 1, start: '2026-10-23T09:00:00', end: '2026-10-23T09:05:00' },
  { id: 2, start: '2026-10-23T09:10:00', end: '2026-10-23T09:15:00' },
  { id: 3, start: '2026-10-23T09:15:00', end: '2026-10-23T09:20:00' }
];
const rows = rowsSummary(__agendaDayLayout.buildDayRows(apps, true));
const from = rows.indexOf('livre 08:45');
console.log(JSON.stringify(rows.slice(from, from + 5)));
""")

        self.assertEqual(result, [
            'livre 08:45', 'consulta 1', 'consulta 2', 'consulta 3', 'livre 09:30',
        ])

    def test_appointments_outside_default_hours_are_never_hidden(self):
        result = run_day_layout_script("""
const apps = [
  { id: 1, start: '2026-10-23T06:30:00', end: '2026-10-23T07:00:00' },
  { id: 2, start: '2026-10-23T21:10:00', end: '2026-10-23T21:25:00' }
];
const rows = rowsSummary(__agendaDayLayout.buildDayRows(apps, true));
console.log(JSON.stringify([rows[0], rows[1], rows[rows.length - 2], rows[rows.length - 1]]));
""")

        self.assertEqual(result, ['consulta 1', 'livre 07:00', 'livre 19:45', 'consulta 2'])

    def test_doctor_view_lists_only_booked_appointments_in_time_order(self):
        result = run_day_layout_script("""
const apps = [
  { id: 2, start: '2026-10-23T16:00:00', end: '2026-10-23T16:15:00' },
  { id: 1, start: '2026-10-23T09:00:00', end: '2026-10-23T09:15:00' }
];
console.log(JSON.stringify(rowsSummary(__agendaDayLayout.buildDayRows(apps, false))));
""")

        self.assertEqual(result, ['consulta 1', 'consulta 2'])


if __name__ == '__main__':
    unittest.main()
