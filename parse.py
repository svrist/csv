# -*- coding: cp1252 -*-
import csv
import sys
from status import dir_to_accounts
from data_setup import file_dir, AMOUNT_COL, SKIP_ROWS


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


def main(idnumber, files):
    with open('%s.csv' % idnumber, 'wb') as output:
        w = csv.writer(output, dialect='excel', delimiter=';')
        for f in files:
            input_filename = f.filename
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
                            'L{}: Failed to parse \'{}\' as '
                            'floating number. {}\n'
                            .format(line_num, amount, row)
                        )
        print "Output in %s" % (output.name)


if __name__ == '__main__':
    for a, files in dir_to_accounts(file_dir).items():
        main(a, files)
