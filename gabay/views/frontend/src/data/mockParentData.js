// Dummy data only. Replaced by API calls once the Django endpoints exist
// (children come from Student.objects.for_parent, which already enforces consent).
export const PARENT = { name: 'Elena Cruz' }

export const CHILDREN = [
  {
    id: 1,
    name: 'Maria Cruz',
    grade: 7,
    section: 'Rizal',
    quarter: 2,
    attendanceRate: 91,
    subjects: [
      { name: 'English', q1: 84, q2: 86, needed: 64 },
      { name: 'Mathematics', q1: 80, q2: 72, needed: 79 },
      { name: 'Science', q1: 78, q2: 79, needed: 71 },
      { name: 'Filipino', q1: 88, q2: 90, needed: 60 },
      { name: 'Araling Panlipunan', q1: 76, q2: 74, needed: 77 },
    ],
    // Days of the month; weekdays up to lastDay not listed here count as present.
    attendance: { year: 2026, month: 10, lastDay: 6, absent: [3, 5], late: [4], excused: [] },
    reasons: { 3: 'Sick' }, // day -> reason already given by the parent
    conference: '14 Nov 2026, 9:00 AM',
    conferenceSlots: ['14 Nov 2026, 9:00 AM', '14 Nov 2026, 10:30 AM', '15 Nov 2026, 8:30 AM'],
    summary: {
      en: 'Maria is doing well in Filipino and English this week. Mathematics dropped a little, so a short review of fractions at home could help.',
      fil: 'Maganda ang takbo ni Maria sa Filipino at English ngayong linggo. Bumaba nang kaunti ang Mathematics, kaya makakatulong ang maikling pag-review ng mga fraction sa bahay.',
      ceb: 'Maayo ang resulta ni Maria sa Filipino ug English karong semana. Mius-os gamay ang Mathematics, busa makatabang ang mubong review sa fractions sa balay.',
    },
    goodNews: 'English went up 2 points, the most improved subject this quarter.',
  },
  {
    id: 2,
    name: 'Jose Cruz',
    grade: 9,
    section: 'Luna',
    quarter: 2,
    attendanceRate: 100,
    subjects: [
      { name: 'English', q1: 79, q2: 82, needed: 68 },
      { name: 'Mathematics', q1: 85, q2: 87, needed: 61 },
      { name: 'Science', q1: 83, q2: 83, needed: 66 },
      { name: 'Filipino', q1: 80, q2: 84, needed: 63 },
      { name: 'Araling Panlipunan', q1: 81, q2: 85, needed: 62 },
    ],
    attendance: { year: 2026, month: 10, lastDay: 6, absent: [], late: [], excused: [] },
    reasons: {},
    conference: null,
    conferenceSlots: ['16 Nov 2026, 1:00 PM', '16 Nov 2026, 2:00 PM'],
    summary: {
      en: 'Jose improved in four of five subjects this week and has not missed a class this month.',
      fil: 'Bumuti ang marka ni Jose sa apat sa limang asignatura ngayong linggo at hindi pa siya lumiban ngayong buwan.',
      ceb: 'Miuswag si Jose sa upat sa lima ka subject karong semana ug wala pa siya mag-absent ning bulana.',
    },
    goodNews: 'Perfect attendance this month.',
  },
]

export const REASONS = ['Sick', 'No fare or allowance', 'Flood or bad weather', 'Family matter', 'Other']
export const NOTICE_COUNT = 2
