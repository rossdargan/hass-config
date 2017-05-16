#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import time, datetime

def mk_occasion(name, start, end, days=None):
    s = start.split(':')
    e = end.split(':')
    return {'name' : name,
            'start': time(int(s[0]), int(s[1]), int(s[2])),
            'end'  : time(int(e[0]), int(e[1]), int(e[2])),
            'days' : days}

# Matching is done from top to bottom
OCCASIONS = [
    # More specific occasions
    mk_occasion('work_morning', '06:00:00', '07:10:00', range(5)),

    # General matching
    mk_occasion('weekday', '00:00:00', '23:59:59', range(5)),
    mk_occasion('weekend', '00:00:00', '23:59:59', [5, 6])
]

def get_current_occasion(occasion_list, default_occasion='normal'):
    now = datetime.now()
    for occasion in OCCASIONS:
        if occasion['start'] <= now.time() <= occasion['end'] and \
           (occasion['days'] is None or now.weekday() in occasion['days']):
            return occasion['name']
    return default_occasion

if __name__ == '__main__':
    print(get_current_occasion(OCCASIONS))