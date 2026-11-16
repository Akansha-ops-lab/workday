import sqlite3
from datetime import date, datetime
from pathlib import Path
import streamlit as st

DB = Path(__file__).with_name('attendance.db')
AREAS = [
    'HR Operations',
    'Recruitment & Placements',
    'Employee Experience',
]
AREA_DETAILS = {
    'HR Operations': 'Attendance & payroll coordination',
    'Recruitment & Placements': 'Candidate screening and hiring support',
    'Employee Experience': 'Employee queries and internal coordination',
}


def get_conn():
    db = sqlite3.connect(DB, check_same_thread=False)
    db.execute('''CREATE TABLE IF NOT EXISTS entries (
        id INTEGER PRIMARY KEY,
        employee TEXT NOT NULL,
        work_date TEXT NOT NULL,
        mode TEXT NOT NULL,
        check_in TEXT,
        check_out TEXT,
        report TEXT,
        status TEXT NOT NULL DEFAULT 'open',
        submitted_at TEXT,
        UNIQUE(employee, work_date)
    )''')
    db.execute('''CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY,
        entry_id INTEGER NOT NULL,
        start_time TEXT,
        end_time TEXT,
        area TEXT,
        task TEXT,
        outcome TEXT
    )''')
    db.commit()
    return db


def today_entry(db, employee):
    return db.execute('SELECT * FROM entries WHERE employee=? AND work_date=?',
                      (employee, date.today().isoformat())).fetchone()


def pretty_time(iso_value):
    if not iso_value:
        return '—'
    try:
        return datetime.fromisoformat(iso_value).strftime('%I:%M %p')
    except ValueError:
        return iso_value


def minutes_between(start, end):
    try:
        a = datetime.strptime(start, '%H:%M')
        b = datetime.strptime(end, '%H:%M')
        delta = int((b - a).total_seconds() // 60)
        return max(delta, 0)
    except (ValueError, TypeError):
        return 0


def display_duration(total):
    return f'{total // 60}h {total % 60:02d}m'


st.set_page_config(page_title='WsCube Workday', page_icon='🕒', layout='wide')
st.markdown('''
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
:root { --navy:#10223e; --teal:#078b8d; --teal-dark:#057477; --muted:#64748b; }
html, body, [class*="css"] { font-family: Inter, sans-serif; }
.stApp { background: #f4f7fb; }
.block-container { max-width: 1500px; padding-top: 1.15rem; padding-bottom: 2rem; }
[data-testid="stSidebar"] { background: var(--navy); }
[data-testid="stSidebar"] * { color: #f8fafc; }
[data-testid="stSidebar"] [data-testid="stRadio"] label { padding: .65rem .7rem; border-radius: 10px; }
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover { background: rgba(255,255,255,.1); }
.hero-title { font-size: 2rem; font-weight: 800; color:#10223e; margin:0; }
.subtle { color:var(--muted); }
.card { background:white; border:1px solid #dbe4ef; border-radius:16px; padding:18px 20px; box-shadow:0 4px 14px rgba(20,45,80,.045); min-height:96px; }
.clock-card { background:linear-gradient(110deg,#e5f7f6,#fff 55%,#d8f4f1); border:1px solid #c7e8e7; border-radius:18px; padding:22px 28px; min-height:132px; }
.clock-time { font-size:3rem; font-weight:800; color:#11233d; line-height:1.1; }
.card-title { font-size:1.12rem; font-weight:700; color:#142541; }
.area-card { background:#fff; border:1px solid #dbe4ef; border-radius:15px; padding:16px; min-height:155px; box-shadow:0 3px 10px rgba(20,45,80,.035); }
.badge { display:inline-block; background:#e8f7f5; color:#17666a; padding:6px 9px; border-radius:8px; font-size:.78rem; margin-top:13px; }
.notice { background:#fff8e8; border:1px solid #f5d99b; border-radius:12px; padding:13px 16px; color:#8d4b0d; }
.green { color:#087443; font-weight:700; }
</style>
''', unsafe_allow_html=True)

db = get_conn()
with st.sidebar:
    st.markdown('## 🟦 WsCube Workday')
    st.caption('Employee HRMS Portal')
    st.divider()
    employee = st.text_input('Employee name', value=st.session_state.get('employee', 'Akansha Khatri'), key='employee').strip()
    page = st.radio('Navigation', ['Dashboard', 'Attendance', 'Daily Reporting', 'Calendar', 'My Work Areas', 'Profile'], label_visibility='collapsed')
    st.divider()
    st.caption('Employee self-service')

if not employee:
    st.info('Enter your employee name in the sidebar to continue.')
    st.stop()

entry = today_entry(db, employee)
now = datetime.now()
current_time = now.strftime('%I:%M %p')
work_mode = entry[3] if entry else st.session_state.get('work_mode', 'Office')


def clock_in():
    db.execute('INSERT OR IGNORE INTO entries(employee,work_date,mode,check_in) VALUES(?,?,?,?)',
               (employee, date.today().isoformat(), st.session_state.work_mode,
                datetime.now().isoformat(timespec='minutes')))
    db.commit()
    st.rerun()


def render_dashboard():
    st.markdown(f'<p class="hero-title">☀️ Good morning, {employee}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="subtle">{date.today().strftime("%A, %d %B %Y")} &nbsp; · &nbsp; Employee Portal</p>', unsafe_allow_html=True)
    st.write('')
    a, b, c, d = st.columns(4)
    is_in = bool(entry and not entry[5] and entry[7] == 'open')
    values = [
        ('Today', 'Working' if is_in else ('Completed' if entry and entry[7] == 'locked' else 'Not clocked in')),
        ('Scheduled', '9:00 AM – 6:00 PM'),
        ('Work mode', work_mode),
        ('Report', 'Submitted' if entry and entry[7] == 'locked' else 'Pending'),
    ]
    for col, (label, value) in zip([a,b,c,d], values):
        with col:
            st.markdown(f'<div class="card"><div class="subtle">{label}</div><div class="card-title">{value}</div></div>', unsafe_allow_html=True)
    st.write('')
    left, right = st.columns([1.65, 1])
    with left:
        st.markdown('<div class="clock-card">', unsafe_allow_html=True)
        clock_col, action_col = st.columns([1.15, .85], vertical_alignment='center')
        with clock_col:
            st.markdown(f'<div class="clock-time">{current_time}</div><div class="subtle">{("Clocked in at " + pretty_time(entry[4])) if is_in else "Start your workday"}</div>', unsafe_allow_html=True)
        with action_col:
            if not entry:
                st.selectbox('Work mode', ['Office', 'Work from home'], key='work_mode', label_visibility='collapsed')
                st.button('↪  Clock In', type='primary', use_container_width=True, on_click=clock_in)
            elif entry[7] == 'locked':
                st.button('✓  Day Complete', disabled=True, use_container_width=True)
            elif entry[5]:
                st.button('✓  Clocked Out', disabled=True, use_container_width=True)
            else:
                st.info('Submit your daily report to clock out.')
        st.markdown('</div>', unsafe_allow_html=True)
        st.write('')
        st.subheader('My Core Work Areas')
        area_cols = st.columns(3)
        for col, area in zip(area_cols, AREAS):
            with col:
                st.markdown(f'<div class="area-card"><div class="card-title">{area}</div><p>{AREA_DETAILS[area]}</p><span class="badge">Assigned by: Reporting Manager</span></div>', unsafe_allow_html=True)
    with right:
        st.markdown('<div class="card"><div class="card-title">▣ Today’s Plan</div><br>09:30 AM &nbsp; Attendance review<br><br>11:00 AM &nbsp; Candidate follow-ups<br><br>02:00 PM &nbsp; Payroll coordination</div>', unsafe_allow_html=True)
    st.write('')
    st.markdown('<div class="notice"><b>Daily report is required before clock-out.</b> Submit your work log and summary from Daily Reporting before ending your workday.</div>', unsafe_allow_html=True)
    st.write('')
    with st.container(border=True):
        st.subheader(date.today().strftime('%B %Y'))
        st.caption('Calendar view · select Calendar in the sidebar to review attendance history.')
        st.write('Today:', date.today().strftime('%a, %d %b %Y'))


def render_reporting():
    st.markdown('<p class="hero-title">▤ End of Day Report</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtle">Add the work completed today before clocking out.</p>', unsafe_allow_html=True)
    st.caption(f'📅 {date.today().strftime("%A, %d %b %Y")}　 |　 👤 {employee}　 |　 🧭 {work_mode}')
    if not entry:
        st.warning('Clock in from the Dashboard before starting your daily report.')
        return
    if entry[7] == 'locked':
        st.success(f'🔒 Report submitted at {pretty_time(entry[8])}. Your report is read-only.')
        st.caption(f'Clock in: {pretty_time(entry[4])}　 |　 Clock out: {pretty_time(entry[5])}')
        st.subheader('Submitted work log')
        tasks = db.execute('SELECT start_time,end_time,area,task,outcome FROM tasks WHERE entry_id=? ORDER BY start_time',(entry[0],)).fetchall()
        st.dataframe(tasks, use_container_width=True, hide_index=True, column_config={
            0: 'From', 1: 'To', 2: 'Core work area', 3: 'Task / activity', 4: 'Outcome / progress'
        })
        st.subheader('Daily summary and handover')
        st.text_area('Submitted summary', value=entry[6] or '', disabled=True, label_visibility='collapsed')
        st.info('Need a correction? Contact your manager and request an audited adjustment.')
        return
    m1,m2,m3 = st.columns(3)
    m1.metric('Clock in', pretty_time(entry[4]))
    m2.metric('Current status', 'Working')
    m3.metric('Work mode', work_mode)
    st.subheader('Work log')
    st.caption('Add a row for each work block. Include the result or progress made.')
    previous = st.session_state.get('draft_tasks', [
        {'From':'09:15','To':'10:30','Core work area':'HR Operations','Task / activity':'','Outcome / progress':''}
    ])
    edited = st.data_editor(previous, num_rows='dynamic', use_container_width=True, hide_index=True, key='draft_task_editor', column_config={
        'From': st.column_config.TextColumn('From (HH:MM)'),
        'To': st.column_config.TextColumn('To (HH:MM)'),
        'Core work area': st.column_config.SelectboxColumn('Core work area', options=AREAS, required=True),
        'Task / activity': st.column_config.TextColumn('Task / activity', required=True),
        'Outcome / progress': st.column_config.TextColumn('Outcome / progress'),
    })
    st.session_state.draft_tasks = edited
    total_mins = sum(minutes_between(str(r.get('From','')), str(r.get('To',''))) for r in edited if r.get('Task / activity'))
    covered = len({r.get('Core work area') for r in edited if r.get('Task / activity')})
    logged = sum(1 for r in edited if r.get('Task / activity'))
    summary_col, totals_col = st.columns([1.65, .8])
    with summary_col:
        summary = st.text_area('Daily summary and handover', placeholder='Summarize key work completed, blockers, and handover notes…', height=140, key='daily_summary')
    with totals_col:
        st.markdown(f'<div class="card"><div class="card-title">Today’s totals</div><br><b>Total logged</b><h2>{display_duration(total_mins)}</h2><b>Work areas covered</b><h3>{covered}</h3><b>Tasks logged</b><h3>{logged}</h3></div>', unsafe_allow_html=True)
    st.warning('You must submit this report before clocking out. Submitted reports are locked for employee edits.')
    if st.button('⇥  Submit Report & Clock Out', type='primary', use_container_width=True):
        clean = [r for r in edited if str(r.get('Task / activity','')).strip()]
        if not clean or not summary.strip():
            st.error('Add at least one task and complete the daily summary before clocking out.')
        else:
            stamp = datetime.now().isoformat(timespec='minutes')
            db.execute('UPDATE entries SET check_out=?,report=?,status="locked",submitted_at=? WHERE id=?',
                       (stamp, summary.strip(), stamp, entry[0]))
            db.execute('DELETE FROM tasks WHERE entry_id=?', (entry[0],))
            db.executemany('INSERT INTO tasks(entry_id,start_time,end_time,area,task,outcome) VALUES(?,?,?,?,?,?)', [
                (entry[0], str(r.get('From','')), str(r.get('To','')), str(r.get('Core work area','')),
                 str(r.get('Task / activity','')).strip(), str(r.get('Outcome / progress','')).strip()) for r in clean
            ])
            db.commit()
            st.session_state.draft_tasks = [{'From':'09:00','To':'10:00','Core work area':AREAS[0],'Task / activity':'','Outcome / progress':''}]
            st.rerun()


def render_attendance():
    st.markdown('<p class="hero-title">Attendance</p>', unsafe_allow_html=True)
    st.caption('Your check-in and check-out history.')
    rows = db.execute('SELECT work_date,mode,check_in,check_out,status FROM entries WHERE employee=? ORDER BY work_date DESC',(employee,)).fetchall()
    if rows:
        st.dataframe(rows, use_container_width=True, hide_index=True, column_config={0:'Date',1:'Work mode',2:'Clock in',3:'Clock out',4:'Report status'})
    else:
        st.info('No attendance records yet. Clock in from your Dashboard to begin.')


def render_calendar():
    st.markdown('<p class="hero-title">Calendar</p>', unsafe_allow_html=True)
    st.caption(date.today().strftime('%B %Y'))
    rows = db.execute('SELECT work_date,mode,check_in,check_out,status FROM entries WHERE employee=? ORDER BY work_date DESC',(employee,)).fetchall()
    if rows:
        st.dataframe(rows, use_container_width=True, hide_index=True, column_config={0:'Date',1:'Work mode',2:'Clock in',3:'Clock out',4:'Report status'})
    else:
        st.info('Your attendance days and submitted reports will appear here.')


def render_work_areas():
    st.markdown('<p class="hero-title">My Core Work Areas</p>', unsafe_allow_html=True)
    st.caption('Areas assigned to you by your reporting manager.')
    cols = st.columns(3)
    for col, area in zip(cols, AREAS):
        with col:
            st.markdown(f'<div class="area-card"><div class="card-title">{area}</div><p>{AREA_DETAILS[area]}</p><span class="badge">Assigned by: Reporting Manager</span></div>', unsafe_allow_html=True)


def render_profile():
    st.markdown('<p class="hero-title">My Profile</p>', unsafe_allow_html=True)
    st.write({'Employee name':employee,'Workday portal':'WsCube Workday','Work schedule':'9:00 AM – 6:00 PM'})

if page == 'Dashboard':
    render_dashboard()
elif page == 'Attendance':
    render_attendance()
elif page == 'Daily Reporting':
    render_reporting()
elif page == 'Calendar':
    render_calendar()
elif page == 'My Work Areas':
    render_work_areas()
else:
    render_profile()
