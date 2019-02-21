from flask import Flask, render_template, g, request
from launchpadlib.launchpad import Launchpad
import time
import sqlite3
import subprocess

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
        'SELECT notes, of_interest, `commit` FROM bug WHERE id=?',
        (bug_id,)
    ).fetchone()

    if row is not None:
        bug['notes'], bug['of_interest'], bug['commit'] = row

    if bug['commit'] is None:
        bug['commit'] = ''

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
    filters = ('of interest', 'unclassified', 'all')
    filter = request.args.get('filter', filters[0])
    if bug_id is not None:
        bug = get_bug(bug_id)
    else:
        bug = None

    analysed = set([
        a[0] for a in get_db().execute(
            'SELECT id FROM bug'
        ).fetchall()
    ])

    of_interest = set([
        oi[0] for oi in get_db().execute(
            'SELECT id FROM bug WHERE of_interest=1'
        ).fetchall()
    ])

    if filter == 'all':
        tasks = get_tasks()
    elif filter == 'unclassified':
        tasks = [t for t in get_tasks() if t['id'] not in analysed]
    elif filter == 'classified':
        tasks = [t for t in get_tasks() if t['id'] in analysed]
    elif filter == 'of interest':
        tasks = [t for t in get_tasks() if t['id'] in of_interest]

    git_grep = subprocess.Popen([
        '/usr/bin/git', '-C', '/home/bmartins/workspace/epics-base', 'log', '--oneline', '--grep='+str(bug['id'])
    ], stdout=subprocess.PIPE)

    stdout, _ = git_grep.communicate()
    print(stdout)

    if stdout:
        commit_suggestion = stdout.split()[0].decode()
    else:
        commit_suggestion = ''

    return render_template('bugs.html',
        tasks=tasks, bug=bug, filters=filters, selected_filter=filter, 
        notes=get_notes(), commit_suggestion=commit_suggestion
    )

@app.route('/')
def index():
    return render()

@app.route('/bug/<int:bug_id>', methods=['GET', 'POST'])
def bug(bug_id):
    if request.method == 'POST':
        notes = request.form.get('notes', '')
        of_interest = request.form.get('of_interest', 'no').lower() == 'yes'
        commit = request.form.get('commit')

        bug = get_bug(bug_id)

        db = get_db()
        print("INSERTING", notes, of_interest)
        print(db.execute('DELETE FROM bug WHERE id=?', (bug_id,)))
        print(db.execute("""INSERT INTO bug
                        (id, web_link, date_created, date_last_updated, notes, of_interest, 'commit')
                      VALUES (?, ?, ?, ?, ?, ?, ?) """,
                      (bug_id, bug['web_link'], bug['date_created'], bug['date_last_updated'],
                      notes, of_interest, commit)))
        db.commit()

    return render(bug_id)
