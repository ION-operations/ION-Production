"""
AIM-OS Email Comms Tool
Send email between agents as a backup comms channel.

Usage:
    python3 email_comms.py send "Subject" "Body"
    python3 email_comms.py send "Subject" "Body" --to other@email.com
    python3 email_comms.py test   # Test connection
"""
import smtplib
import ssl
import sys
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from datetime import datetime

# Import vault
sys.path.insert(0, str(Path(__file__).parent))
from vault import CredentialVault


def get_creds(vault_key="backup_gmail"):
    """Retrieve email credentials from vault."""
    vault = CredentialVault()
    creds = vault.retrieve(vault_key)
    if not creds:
        print(f"ERROR: No credentials found for '{vault_key}' in vault")
        sys.exit(1)
    return creds


def test_connection(creds):
    """Test SMTP connection with multiple methods."""
    email = creds["email"]
    password = creds["password"]

    methods = [
        ("SSL (465)", 465, "ssl"),
        ("STARTTLS (587)", 587, "starttls"),
    ]

    for name, port, method in methods:
        print(f"Testing {name}...")
        try:
            if method == "ssl":
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL("smtp.gmail.com", port, timeout=10, context=context) as server:
                    server.login(email, password)
                    print(f"  ✅ {name}: Connected and authenticated!")
                    return port, method
            else:
                with smtplib.SMTP("smtp.gmail.com", port, timeout=10) as server:
                    server.starttls()
                    server.login(email, password)
                    print(f"  ✅ {name}: Connected and authenticated!")
                    return port, method
        except smtplib.SMTPAuthenticationError as e:
            print(f"  ❌ {name}: Auth failed — {e}")
        except Exception as e:
            print(f"  ❌ {name}: {type(e).__name__} — {e}")

    print("\nAll methods failed. Check:")
    print("  1. 'Less secure app access' in Google account settings")
    print("  2. Or generate an App Password at myaccount.google.com/apppasswords")
    return None, None


def send_email(subject, body, to_email=None, vault_key="backup_gmail"):
    """Send email using vault credentials."""
    creds = get_creds(vault_key)
    email = creds["email"]
    password = creds["password"]
    to = to_email or email  # Default: send to self

    msg = MIMEMultipart()
    msg["From"] = f"AIM-OS Opus <{email}>"
    msg["To"] = to
    msg["Subject"] = subject

    # Add timestamp to body
    full_body = f"{body}\n\n---\nSent by AIM-OS Opus at {datetime.now().isoformat()}\nMachine: pop-os (192.168.2.25)"
    msg.attach(MIMEText(full_body, "plain"))

    # Try SSL first (more reliable), then STARTTLS
    methods = [
        (465, "ssl"),
        (587, "starttls"),
    ]

    for port, method in methods:
        try:
            if method == "ssl":
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL("smtp.gmail.com", port, timeout=15, context=context) as server:
                    server.login(email, password)
                    server.sendmail(email, [to], msg.as_string())
            else:
                with smtplib.SMTP("smtp.gmail.com", port, timeout=15) as server:
                    server.starttls()
                    server.login(email, password)
                    server.sendmail(email, [to], msg.as_string())

            print(f"✅ Email sent via {method}:{port}")
            print(f"   To: {to}")
            print(f"   Subject: {subject}")
            return True
        except Exception as e:
            print(f"❌ {method}:{port} failed — {e}")
            continue

    print("All send methods failed.")
    return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 email_comms.py test")
        print("  python3 email_comms.py send 'Subject' 'Body'")
        print("  python3 email_comms.py send 'Subject' 'Body' --to email@example.com")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "test":
        creds = get_creds()
        test_connection(creds)
    elif cmd == "send":
        if len(sys.argv) < 4:
            print("Usage: python3 email_comms.py send 'Subject' 'Body' [--to email]")
            sys.exit(1)
        subject = sys.argv[2]
        body = sys.argv[3]
        to = None
        if "--to" in sys.argv:
            idx = sys.argv.index("--to")
            to = sys.argv[idx + 1]
        send_email(subject, body, to)
    else:
        print(f"Unknown command: {cmd}")
