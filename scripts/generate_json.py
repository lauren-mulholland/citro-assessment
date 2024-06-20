# script to read a csv and convert to json
if __name__ == '__main__':
    import csv
    import json
    start_row = 1
    end_row = start_row + 10
    # Open the CSV
    f = open('scripts/txns.csv', 'r', encoding='utf-8-sig')
    reader = csv.DictReader(f)
    # Parse the CSV into JSON for 10 rows
    out = json.dumps([row for idx, row in enumerate(reader) if start_row <= idx < end_row])
    print(out)