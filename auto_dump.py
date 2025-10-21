#!/usr/bin/env python3
import sys
import os
import re
import csv
import datetime as dt
from getpass import getpass
from typing import List, Optional, Iterable
import firebirdsql

def quote_ident(name: str) -> str:
    n = name.strip()
    return '"' + n.replace('"', '""') + '"'

def sanitize_filename(name: str) -> str:
    n = name.strip()
    return re.sub(r'[^0-9A-Za-z._-]+', '_', n) or "table"

def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)

def get_user_tables(cur) -> List[str]:
    cur.execute("""
        SELECT rdb$relation_name
        FROM rdb$relations
        WHERE rdb$view_blr IS NULL
          AND (rdb$system_flag IS NULL OR rdb$system_flag = 0);
    """)
    return [row[0].strip() for row in cur.fetchall()]

def fetch_in_batches(cur, batch_size: int) -> Iterable[list]:
    while True:
        rows = cur.fetchmany(batch_size)
        if not rows:
            break
        yield from rows

def export_table(cur, table: str, outdir: str, max_rows: Optional[int], batch_size: int) -> None:
    qname = quote_ident(table)
    sql = f"SELECT * FROM {qname};" if max_rows is None else f"SELECT FIRST {max_rows} * FROM {qname};"
    cur.execute(sql)
    cols = [d[0] for d in cur.description] if cur.description else []
    path = os.path.join(outdir, f"{sanitize_filename(table)}.csv")

    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(cols)
        count = 0
        for row in fetch_in_batches(cur, batch_size):
            writer.writerow(row)
            count += 1
            if max_rows and count >= max_rows:
                break

def extract_and_export(db_path: str, host: str) -> None:
    try:
        con = firebirdsql.connect(
            host=host, database=db_path,
            user="SYSDBA", password="masterkey", timeout=15
        )
    except Exception as e:
        print(f"[CONNECT] Błąd połączenia do '{db_path}': {e}")
        return

    try:
        cur = con.cursor()
        tables = get_user_tables(cur)
        if not tables:
            print(f"Brak tabel w bazie: {db_path}")
            return

        outdir = os.path.join("export", os.path.basename(db_path).split('.')[0])
        ensure_dir(outdir)

        print(f"\nEksport bazy: {db_path}")
        for t in tables:
            print(f" - tabela {t}")
            export_table(cur, t, outdir, max_rows=100, batch_size=1000)
            print(f"   -> {outdir}/{sanitize_filename(t)}.csv")
    finally:
        cur.close()
        con.close()

def main():
    if len(sys.argv) != 2:
        print("Użycie: python3 fb_enum_export.py <host>")
        sys.exit(1)
    host = sys.argv[1]

    print(f"Łączenie do serwera {host} jako SYSDBA/masterkey...")
    try:
        svc = firebirdsql.services.connect(host=host, user="SYSDBA", password="masterkey", timeout=5)
        attached = svc.getAttachedDatabaseNames()
        svc.close()
    except Exception as e:
        print(f"[SERVICE] Błąd usługi Firebird: {e}")
        sys.exit(1)

    if not attached:
        print("Brak podłączonych baz.")
        sys.exit(0)

    print("\nZnalezione bazy:")
    for db in attached:
        print(f" * {db}")
        extract_and_export(db, host)

if __name__ == "__main__":
    main()
