import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AGENDA_JS = ROOT / 'static' / 'js' / 'agenda.js'


def run_timeline_script(body):
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


class AgendaTimelineLayoutTest(unittest.TestCase):
    def test_simultaneous_appointments_share_the_same_time_in_separate_lanes(self):
        result = run_timeline_script("""
const apps = [
  { id: 1, start: '2026-10-23T09:00:00', end: '2026-10-23T09:30:00' },
  { id: 2, start: '2026-10-23T09:00:00', end: '2026-10-23T09:15:00' },
  { id: 3, start: '2026-10-23T10:00:00', end: '2026-10-23T10:15:00' }
];
const layout = __agendaTimeline.assignOverlapLanes(
  apps.map(__agendaTimeline.appointmentInterval)
);
console.log(JSON.stringify(layout.map(item => ({
  id: item.app.id,
  lane: item.lane,
  laneCount: item.laneCount
}))));
""")

        self.assertEqual(result, [
            {'id': 1, 'lane': 0, 'laneCount': 2},
            {'id': 2, 'lane': 1, 'laneCount': 2},
            {'id': 3, 'lane': 0, 'laneCount': 1},
        ])

    def test_short_appointments_reserve_at_least_one_fifteen_minute_slot(self):
        result = run_timeline_script("""
const apps = [
  { id: 1, start: '2026-10-23T09:00:00', end: '2026-10-23T09:05:00' },
  { id: 2, start: '2026-10-23T09:10:00', end: '2026-10-23T09:15:00' },
  { id: 3, start: '2026-10-23T09:15:00', end: '2026-10-23T09:20:00' }
];
const layout = __agendaTimeline.assignOverlapLanes(
  apps.map(__agendaTimeline.appointmentInterval)
);
console.log(JSON.stringify(layout.map(item => ({
  id: item.app.id,
  lane: item.lane,
  laneCount: item.laneCount
}))));
""")

        self.assertEqual(result, [
            {'id': 1, 'lane': 0, 'laneCount': 2},
            {'id': 2, 'lane': 1, 'laneCount': 2},
            {'id': 3, 'lane': 0, 'laneCount': 2},
        ])

    def test_timeline_expands_for_appointments_outside_default_hours(self):
        result = run_timeline_script("""
const apps = [
  { id: 1, start: '2026-10-23T06:30:00', end: '2026-10-23T07:00:00' },
  { id: 2, start: '2026-10-23T21:10:00', end: '2026-10-23T21:25:00' }
];
const intervals = apps.map(__agendaTimeline.appointmentInterval);
console.log(JSON.stringify(__agendaTimeline.timelineBounds(intervals)));
""")

        self.assertEqual(result, {'startMinutes': 360, 'endMinutes': 1320})


if __name__ == '__main__':
    unittest.main()
