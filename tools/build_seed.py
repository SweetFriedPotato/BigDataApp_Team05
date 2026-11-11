#!/usr/bin/env python3
"""Build plain INSERTs from validated inputs. Stable ordering; no runtime dependencies."""
from data_common import ROOT, LOCATIONS
from validate_data import validate

def literal(value):
    if value is None: return 'NULL'
    # Doubled quotes work regardless of NO_BACKSLASH_ESCAPES. Source data contains no backslashes.
    s = str(value)
    if '\\' in s or '\x00' in s: raise ValueError('Unsupported source control character')
    return "'" + s.replace("'", "''") + "'"

def insert(table, columns, rows):
    out = []
    for offset in range(0,len(rows),250):
        values = [ '(' + ','.join(literal(v) for v in row) + ')' for row in rows[offset:offset+250] ]
        out.append(f'INSERT INTO {table} ({columns}) VALUES\n' + ',\n'.join(values)+';\n')
    return ''.join(out)

weather, terms, foods = validate()
sql = '-- Deterministic seed; generated only after raw validation. Plans intentionally empty.\nUSE team05;\nSET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;\nSTART TRANSACTION;\n'
sql += insert('locations','location_id,location_code,name_en,name_ko,requested_latitude,requested_longitude',LOCATIONS)
sql += insert('daily_temperatures','location_id,weather_date,tmean,tmax,tmin',weather)
sql += insert('solar_terms','term_date,term_name,source_url',[[r[k] for k in ('term_date','term_name','source_url')] for r in sorted(terms,key=lambda r:r['term_date'])])
sql += insert('monthly_food_guides','month_no,food_name,source_url',[[r[k] for k in ('month_no','food_name','source_url')] for r in foods])
(ROOT/'sql/dbinsert.sql').write_text(sql+'COMMIT;\n')
print('Wrote sql/dbinsert.sql: 5 + 5480 + 72 + 12 = 5569 rows')
