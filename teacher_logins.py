"""Makes teacher logins for boardgameBuilder's teacher page.

usage: python teacher_logins.py <file> <name> [<name> ...]
Gives each name a new password, writes the names and passwords to <file> (keep it private: it is the only copy of the
passwords), and prints the TEACHER_LOGINS value to set on the server, which holds only salted hashes.
"""
import hashlib, os, secrets, sys

lines, logins = [], []
for name in (n.lower() for n in sys.argv[2:]):
    password = "-".join(secrets.token_urlsafe(4) for _ in range(3))
    salt = secrets.token_bytes(16)
    logins.append(f"{name}:{salt.hex()}.{hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 200_000).hex()}")
    lines.append(f"{name}\t{password}")
with open(sys.argv[1], "w") as f:
    f.write("Teacher logins for boardgameBuilder's /teacher page. Name, then password. Private: never commit or post this file.\n\n" + "\n".join(lines) + "\n")
os.chmod(sys.argv[1], 0o600)
print(",".join(logins))
