# -*- coding: cp1252 -*-
import csv
import sys
import os
from data_setup import *

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
        


def main(idnumber):
    with open('%d.csv' % idnumber, 'wb') as output:
        w = csv.writer(output, dialect='excel', delimiter=';')
        wrote_header = False
        for input_fn in os.listdir(file_dir):
            input_filename = os.path.join(file_dir, input_fn)
            if not 'transactions %d'%idnumber in input_filename:
                continue
            print "Reading %s" % input_filename
            with open(input_filename, 'rb') as f:
                csv_file = csv.reader(f, dialect='excel', delimiter=';')
                skip_rows(csv_file, SKIP_ROWS)
                for ln, row in enumerate(csv_file):
                    line_num = ln + SKIP_ROWS + 1
                    if invalid_row(line_num, row):
                        continue
                    
                    amount = row[AMOUNT_COL - 1]
                    try:
                        if less_than_zero(amount):
                            w.writerow(row)
                    except ValueError:
                        sys.stderr.write(
                            'L{}: Failed to parse \'{}\' as floating number. {}\n'
                            .format(line_num, amount, row)
                        )
        print "Output in %s" % (output.name)


if __name__ == '__main__':
    for a in accounts:
        main(a)

