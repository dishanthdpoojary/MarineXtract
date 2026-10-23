"""Run once to create or reset this computer's MarineXtract login."""
from getpass import getpass

from backend.auth_config import LOGIN_SETTINGS_PATH, save_local_login


def configure_login():
    print("\nMarineXtract sign-in setup")
    print("Your login will be saved locally and reused after restarts.")
    print("Passwords are hidden while you type.\n")
    while True:
        username = input("Username [admin]: ").strip() or "admin"
        password = getpass("Choose a password (at least 12 characters): ")
        confirm = getpass("Confirm password: ")
        if password != confirm:
            print("Passwords do not match. Please try again.\n")
            continue
        try:
            save_local_login(username, password)
        except ValueError as exc:
            print(f"{exc}\n")
            continue
        print(f"\nSign-in configured for {username}. Settings saved to {LOGIN_SETTINGS_PATH}")
        print("Restart the server if it is already running, then refresh the login page.")
        return


if __name__ == "__main__":
    try:
        configure_login()
    except (EOFError, KeyboardInterrupt):
        raise SystemExit("\nSetup cancelled. Run python setup_login.py in an interactive terminal.")
