import os
import re
from datetime import timedelta
from dateutil import parser
from operator import attrgetter
from collections import namedtuple

import data_setup

name_re = re.compile(
    '^transactions (?P<account>[^ ]+) '
    '(?P<fromts>..-..-....)-(?P<tots>..-..-....) .*.csv$'
)


def dir_to_accounts(file_dir):
    files = os.listdir(file_dir)
    accounts = set([name_re.match(f).group('account')
                    for f in files if name_re.match(f)])
    data = {a: [] for a in accounts}
    for f in files:
        m = name_re.match(f)
        if not m:
            continue
        fdata = m.groupdict()
        data[fdata['account']].append(to_data(file_dir, f, fdata))

    return data


TsAnalysis = namedtuple('TsAnalysis', ['diagram', 'holes', 'mints', 'maxts'])
File = namedtuple('File', ['fromts', 'tots',  'filename'])


def analyze_ts(tss):
    s = sorted(tss, key=attrgetter('fromts'))
    holes = []

    overall_min = s[0].fromts
    overall_max = max([e.tots for e in s])

    cur_max = s[0].fromts
    cur = []

    diagram = ['*' for i in range((overall_max - overall_min).days + 1)]

    def set_d(from_ts, to_ts, c):
        i_start = (from_ts - overall_min).days
        i_end = (to_ts - overall_min).days
        for i in range(i_start, i_end):
            diagram[i] = c

    for e in s:
        #print '\t%s %s (%s %s)' % (e.fromts, e.tots, cur_min, cur_max)
        cur.append(e)
        if cur_max > e.fromts:
            set_d(e.fromts, cur_max, '#')
            continue

        if cur_max < e.fromts:
            hole = (cur_max + timedelta(days=1), e.fromts,
                    [cur[-2].filename, e.filename])
            set_d(hole[0], hole[1], '_')
            holes.append(hole)
        cur_max = e.tots
    return TsAnalysis(diagram, holes, overall_min, overall_max)


def to_data(file_dir, f, fdata):
    return File(parser.parse(fdata['fromts'], dayfirst=True),
                parser.parse(fdata['tots'], dayfirst=True),
                os.path.join(file_dir, f))


def main():
    data = dir_to_accounts(data_setup.file_dir)

    df = '%A %Y%m%d'
    for k, d in data.items():
        print 'Account %s' % k
        tsa = analyze_ts(d)
        print '\t%s -> %s' % (tsa.mints, tsa.maxts)
        if tsa.holes:
            print '\tHoles:'
        for f, t, fil in tsa.holes:
            print '\t\t[{} {}[ ({})'.format(f.strftime(df), t.strftime(df),
                                            fil)
        print tsa.diagram
        print ''


if __name__ == '__main__':
    main()
