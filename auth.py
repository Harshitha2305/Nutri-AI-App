# =============================================================================
# auth.py — NutriAI v4
# Authentication layer: password hashing, registration, login, session helpers.
#
# Security choices
# ────────────────
#   • bcrypt via hashlib.pbkdf2_hmac (stdlib, no extra dep)  for password storage
#   • Token stored only in st.session_state (never in a cookie)
#   • Email normalised to lowercase before storage & lookup
#
# Public API (used by app.py)
#   AuthManager.register(name, email, password)  → (ok: bool, msg: str)
#   AuthManager.login(email, password)            → (ok: bool, msg: str, user_row)
#   is_logged_in()                                → bool
#   current_user()                                → dict | None
#   logout()
# =============================================================================

import hashlib
import hmac
import os
import re
import streamlit as st
from database import Database

# ── Constant-time compare for timing-safe password check ─────────────────────
_ITERATIONS = 260_000   # OWASP 2023 recommendation for PBKDF2-HMAC-SHA256


def _hash_password(password: str, salt: bytes = None) -> str:
    """
    Returns  'pbkdf2$<hex-salt>$<hex-dk>'  ready for DB storage.
    A fresh random 16-byte salt is generated if none supplied.
    """
    if salt is None:
        salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt, _ITERATIONS, dklen=32
    )
    return f"pbkdf2${salt.hex()}${dk.hex()}"


def _verify_password(password: str, stored_hash: str) -> bool:
    """Constant-time verification against a stored hash string."""
    try:
        _, salt_hex, dk_hex = stored_hash.split("$")
        salt = bytes.fromhex(salt_hex)
        new_hash = _hash_password(password, salt)
        return hmac.compare_digest(new_hash, stored_hash)
    except Exception:
        return False


# ── Validators ────────────────────────────────────────────────────────────────

def _valid_email(email: str) -> bool:
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email.strip()))


def _valid_password(pw: str) -> tuple[bool, str]:
    if len(pw) < 8:
        return False, "Password must be at least 8 characters."
    if not re.search(r"[A-Za-z]", pw):
        return False, "Password must contain at least one letter."
    if not re.search(r"\d", pw):
        return False, "Password must contain at least one digit."
    return True, ""


# ═════════════════════════════════════════════════════════════════════════════
# AuthManager
# ═════════════════════════════════════════════════════════════════════════════

class AuthManager:
    """Stateless auth helper — all state lives in the DB or session_state."""

    def __init__(self):
        self.db = Database()

    # ── Registration ──────────────────────────────────────────────────────────

    def register(self, name: str, email: str,
                 password: str, confirm: str) -> tuple[bool, str]:
        """
        Validate inputs, hash password, insert user row.

        Returns (success: bool, message: str).
        On success the message is empty; on failure it describes the problem.
        """
        name    = name.strip()
        email   = email.strip().lower()
        password = password.strip()
        confirm  = confirm.strip()

        if not name:
            return False, "Please enter your full name."
        if not _valid_email(email):
            return False, "Please enter a valid email address."
        ok, err = _valid_password(password)
        if not ok:
            return False, err
        if password != confirm:
            return False, "Passwords do not match."

        pw_hash = _hash_password(password)
        uid = self.db.create_user(name, email, pw_hash)
        if uid is None:
            return False, "An account with that email already exists. Please log in."
        return True, ""

    # ── Login ─────────────────────────────────────────────────────────────────

    def login(self, email: str, password: str) -> tuple[bool, str, dict | None]:
        """
        Verify credentials.

        Returns (success, message, user_dict | None).
        user_dict keys: id, name, email, created_at, last_login
        """
        email = email.strip().lower()
        if not email or not password:
            return False, "Email and password are required.", None

        row = self.db.get_user_by_email(email)
        if row is None:
            return False, "No account found with that email address.", None

        if not _verify_password(password, row["password_hash"]):
            return False, "Incorrect password. Please try again.", None

        self.db.update_last_login(row["id"])
        return True, "", dict(row)

    # ── Password change ───────────────────────────────────────────────────────

    def change_password(self, user_id: int, old_pw: str,
                        new_pw: str, confirm_pw: str) -> tuple[bool, str]:
        row = self.db.get_user_by_id(user_id)
        if not row or not _verify_password(old_pw, row["password_hash"]):
            return False, "Current password is incorrect."
        ok, err = _valid_password(new_pw)
        if not ok:
            return False, err
        if new_pw != confirm_pw:
            return False, "New passwords do not match."
        self.db.update_password(user_id, _hash_password(new_pw))
        return True, "Password updated successfully."


# ═════════════════════════════════════════════════════════════════════════════
# Session helpers  (used everywhere in app.py)
# ═════════════════════════════════════════════════════════════════════════════

def init_auth_state():
    """Call once at app startup to ensure auth keys exist in session_state."""
    keys = {
        "auth_user":      None,   # dict with id, name, email  (or None)
        "auth_page":      "landing",  # landing | login | register | app
        "auth_error":     "",
        "auth_success":   "",
        "profile_setup":  False,  # True once profile form submitted this session
    }
    for k, v in keys.items():
        if k not in st.session_state:
            st.session_state[k] = v


def is_logged_in() -> bool:
    return st.session_state.get("auth_user") is not None


def current_user() -> dict | None:
    return st.session_state.get("auth_user")


def login_user(user_dict: dict):
    """Persist user dict to session and flip to app page."""
    st.session_state.auth_user    = user_dict
    st.session_state.auth_page    = "app"
    st.session_state.auth_error   = ""
    st.session_state.auth_success = ""
    # Reset dashboard state on fresh login
    for k in ["ready","profile","daily_plan","weekly_plan",
              "grocery_list","chat_messages","hydration_ml",
              "swap_result","swap_slot"]:
        st.session_state[k] = None if k not in ("chat_messages",) else []
    st.session_state["ready"] = False
    st.session_state["hydration_ml"] = 0


def logout():
    """Clear all session state and return to landing."""
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.session_state.auth_page  = "landing"
    st.session_state.auth_user  = None
