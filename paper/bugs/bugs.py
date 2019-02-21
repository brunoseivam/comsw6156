from flask import Flask, render_template, g, request
from launchpadlib.launchpad import Launchpad
import time
import sqlite3

DATABASE = 'bugs.db'
app = Flask(__name__)

gl = {'_bugs': {}}

def get_lp():
    if '_lp' not in gl:
        print('Launchpad login')
        # Login to Launchpad
        gl['_lp'] = Launchpad.login_anonymously('test', 'production')
    return gl['_lp']

def get_tasks():
    if '_tasks' not in gl:
        print('fetching tasks')

        # Access EPICS project
        epics = get_lp().projects['epics-base']

        # Get tasks
        gl['_tasks'] = []

        for t in epics.searchTasks(status=['Fix Committed', 'Fix Released']):
            web_link = t.lp_get_parameter('web_link')
            web_link.replace('https', 'http')
            title = t.lp_get_parameter('title')
            date_created = t.lp_get_parameter('date_created')
            id = int(title.split()[1][1:])

            gl['_tasks'].append({
                'task': t,
                'id': id,
                'web_link': web_link,
                #'title': title,
                'date_created': date_created,
            })

        gl['_tasks'] = sorted(gl['_tasks'], key=lambda t: t['date_created'], reverse=True)
    return gl['_tasks']

def get_bug(bug_id):
    if bug_id not in gl['_bugs']:
        gl['_bugs'][bug_id] = None
        for t in get_tasks():
            if t['id'] == bug_id:
                bug = t['task'].lp_get_parameter('bug')

                bug_dict = {
                    p: bug.lp_get_parameter(p)
                    for p in ['id', 'title', 'heat',
                        'web_link', 'description',
                        'date_created', 'date_last_updated']
                }

                bug_dict['messages'] = [
                    m.lp_get_parameter('content')
                    for m in bug.lp_get_parameter('messages')
                ]

                bug_dict['messages'] = bug_dict['messages'][1:]

                bug_dict['bug'] = bug

                gl['_bugs'][bug_id] = bug_dict


    bug = gl['_bugs'][bug_id]
    if bug is None:
        return None

    row = get_db().execute(
        'SELECT notes, of_interest FROM bug WHERE id=?',
        (bug_id,)
    ).fetchone()

    if row is not None:
        bug['notes'], bug['of_interest'] = row

    return bug

def get_notes():
    return get_db().execute("""
        SELECT COUNT(notes) as cnt, notes
        FROM bug
        GROUP BY notes
        ORDER BY cnt DESC
    """).fetchall()

def get_db():
    if '_database' not in g:
        g._database = sqlite3.connect(DATABASE)
    return g._database

@app.teardown_appcontext
def teardown_db(exception):
    db = g.pop('_database', None)
    if db is not None:
        db.close()

def render(bug_id=None):
    show_all = int(request.args.get('all', 0))
    if bug_id is not None:
        bug = get_bug(bug_id)
    else:
        bug = None

    analysed = get_db().execute('SELECT id FROM bug').fetchall()
    analysed = set([a[0] for a in analysed])
    if show_all:
        tasks = get_tasks()
    else:
        tasks = [t for t in get_tasks() if t['id'] not in analysed]

    return render_template('bugs.html',
        tasks=tasks, bug=bug, show_all=show_all, notes=get_notes()
    )

@app.route('/')
def index():
    return render()

@app.route('/bug/<int:bug_id>', methods=['GET', 'POST'])
def bug(bug_id):
    if request.method == 'POST':
        notes = request.form.get('notes', '')
        of_interest = request.form.get('of_interest', 'no').lower() == 'yes'

        bug = get_bug(bug_id)

        db = get_db()
        print("INSERTING", notes, of_interest)
        print(db.execute('DELETE FROM bug WHERE id=?', (bug_id,)))
        print(db.execute("""INSERT INTO bug
                        (id, web_link, date_created, date_last_updated, notes, of_interest)
                      VALUES (?, ?, ?, ?, ?, ?) """,
                      (bug_id, bug['web_link'], bug['date_created'], bug['date_last_updated'],
                      notes, of_interest)))
        db.commit()

    return render(bug_id)
