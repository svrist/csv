# -*- coding: cp1252 -*-
import csv
import sys
from math import fabs
from status import dir_to_accounts
from collections import Counter
from data_setup import file_dir, AMOUNT_COL, SKIP_ROWS, BOOK_COL, VAL_COL, DESCR_COL, BENEF_COL


def skip_rows(reader, rows):
    for i in range(rows):
        reader.next()


def less_than_zero(col):
    return float(col.replace(',', '.')) < 0


def invalid_row(line_num, row):
    invalid = len(row) < AMOUNT_COL
    if invalid:
        sys.stderr.write('Line {}. wrong number of cols: {} (< {}): |{}|\n'
                         .format(line_num, len(row), AMOUNT_COL, row))
    return invalid

def negatives(row):
    amount = row[AMOUNT_COL - 1]
    return less_than_zero(amount)

def holding(row):
    holding_benef = 'HOLDINGSELSKABET 4-7' in row[BENEF_COL - 1]
    return negatives(row) or holding_benef

def benef_descr(row, benef, descr):
    return benef in row[BENEF_COL - 1] and descr.lower() in row[DESCR_COL - 1].lower()
    
def main_acct(row):
    negative = negatives(row)
    treasury = benef_descr(row, 'COOP DANMARK', 'TREASURY VALUTA')
    ejd = benef_descr(row, 'COOP DANMARK A/S', 'Påfyldning EJD')
    bas = benef_descr(row, 'COOP DANMARK A/S', 'Påfyldning BAS')
    fakta = benef_descr(row, 'FAKTA A/S', 'yldning Fakta')
    ansv = benef_descr(row, 'HOLDINGSELSKABET AF', 'Bgs ansv. lånekapi')
    
    return (negative and not (treasury or ejd or bas or fakta or ansv))
    


filters = {
    '5005838105': negatives,
    '5005838092': negatives,
    '5005852704': negatives,
    '5368909124': negatives,
    '716190676': negatives,
    '630302307': negatives,
    '6885769878': negatives,
    '3486915462': holding,
    '277450550': main_acct,
}



def amount(row):
    return float(row[AMOUNT_COL - 1].replace(',', '.'))

def skip_value_moves(csv_file, val_mov, c=None):
    s = sorted(csv_file, key=lambda row: '%s|%s'%(row[BOOK_COL - 1], fabs(amount(row))))

    last_row = None
    for row in s:
        if last_row is None:
            last_row = row
            continue
        
        zeroes = amount(row) + amount(last_row) == 0
        same_book = row[BOOK_COL - 1] == last_row[BOOK_COL - 1]

        diff_val = row[VAL_COL - 1] != last_row[VAL_COL - 1]
        
        if zeroes and same_book:
            with open(val_mov,'ab') as valm:
                w = csv.writer(valm,dialect='excel', delimiter=';')
                w.writerow(last_row)
                w.writerow(row)
            last_row = None
            if c:
                c['valuemoves'] += 2
            continue
        else:
            yield last_row
            last_row = row


def ortre(row):
    return 'otrte' in row[DESCR_COL - 1].lower()



def main(idnumber, files):
    out = []
    c = Counter()
    for f in files:
        input_filename = f.filename
        print "Reading %s" % input_filename
        with open(input_filename, 'rb') as f:
            csv_file = csv.reader(f, dialect='excel', delimiter=';')
            skip_rows(csv_file, SKIP_ROWS)
            for ln, row in enumerate(skip_value_moves(csv_file,'%s-valmove.csv'%idnumber, c)):
                line_num = ln + SKIP_ROWS + 1
                if invalid_row(line_num, row):
                    c['invalid'] += 1
                    continue

                if ortre(row):
                    c['otre'] += 1
                    continue

                filt = filters[idnumber]
                
                try:
                    if filt(row):
                        c['hit'] += 1
                        out.append(row)
                    else:
                        c['miss'] += 1
                except ValueError:
                    sys.stderr.write(
                        'L{}: Failed to parse \'{}\' as '
                        'floating number. {}\n'
                        .format(line_num, amount, row)
                    )
    with open('%s.csv' % idnumber, 'wb') as output:
        w = csv.writer(output, dialect='excel', delimiter=';')
        w.writerows(sorted(out, key=lambda row: row[VAL_COL - 1]))
    print "Output in %s" % (output.name)
    print repr(c)
    print


if __name__ == '__main__':
    for a, files in dir_to_accounts(file_dir).items():
        main(a, files)
