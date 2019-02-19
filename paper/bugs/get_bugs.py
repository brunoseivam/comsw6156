#!/usr/bin/env python3

from launchpadlib.launchpad import Launchpad

# Login to Launchpad
lp = Launchpad.login_anonymously('test', 'production')

# Access EPICS project
epics = lp.projects['epics-base']

# Get bugs
bugs = epics.searchTasks(status=[
    'Fix Committed', 'Fix Released'
])

print('Found %d bugs' % len(bugs))

attrs = ['title', 'status', 'is_complete', 'self_link', 'web_link']
categories = ['logic', 'leak', 'null-deref', 'build', '']

# Iterate over bugs for manual classification
for bug in bugs:
    pass

