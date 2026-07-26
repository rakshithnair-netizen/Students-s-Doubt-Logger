import os
import json
from supabase import create_client, Client


class DoubtStore:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.env_path = os.path.join(self.base_dir, ".env")
        self.config_path = os.path.join(self.base_dir, "config.json")

        self.default_subjects = []

        self._load_env()
        self._load_config()

        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        if not url or not key:
            raise KeyError(
                "SUPABASE_URL and SUPABASE_KEY must be set in the .env file."
            )

        self.client: Client = create_client(url, key)
        self._seed_defaults()

    def _load_env(self):
        if os.path.exists(self.env_path):
            try:
                with open(self.env_path, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, val = line.split("=", 1)
                            os.environ[key.strip()] = val.strip()
            except Exception:
                pass

    def _load_config(self):
        self.config = {}
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    self.config = json.load(f)
            except Exception:
                pass

        env_subjects = os.environ.get("DEFAULT_SUBJECTS")
        if env_subjects:
            try:
                self.default_subjects = json.loads(env_subjects)
            except Exception:
                self.default_subjects = []
        else:
            self.default_subjects = self.config.get("default_subjects", [])

    def _seed_defaults(self):
        """Inserts default subjects into Supabase if they don't already exist."""
        for subject in self.default_subjects:
            try:
                self.client.table("subjects").upsert(
                    {"subject": subject}, on_conflict="subject"
                ).execute()
            except Exception:
                pass

    # ──────────────────────────────────────────────────────
    # Auth
    # ──────────────────────────────────────────────────────

    def authenticate(self, username, password):
        """Returns role string ('student' or 'teacher') if credentials match, else None."""
        u = str(username).strip()
        p = str(password).strip()
        try:
            res = (
                self.client.table("users")
                .select("password, role")
                .eq("username", u)
                .execute()
            )
            if res.data and res.data[0]["password"] == p:
                return res.data[0]["role"]
        except Exception as e:
            print(f"authenticate error: {e}")
        return None

    def register_user(self, username, password, role):
        """Registers a new user. Returns True on success, False if username exists or invalid."""
        u = str(username).strip()
        p = str(password).strip()
        r = str(role).strip().lower()

        if not u or not p or r not in ["student", "teacher"]:
            return False

        # Check for existing user
        try:
            existing = (
                self.client.table("users")
                .select("username")
                .eq("username", u)
                .execute()
            )
            if existing.data:
                return False

            self.client.table("users").insert(
                {"username": u, "password": p, "role": r}
            ).execute()
            return True
        except Exception as e:
            print(f"register_user error: {e}")
            return False

    # ──────────────────────────────────────────────────────
    # Doubts
    # ──────────────────────────────────────────────────────

    def add_doubt(self, student, subject, teacher, severity, urgent, explain, desc):
        """Adds a new doubt to Supabase."""
        try:
            res = (
                self.client.table("doubts")
                .insert(
                    {
                        "student": student,
                        "subject": subject,
                        "teacher": teacher,
                        "severity": severity,
                        "urgent": urgent,
                        "explain": explain,
                        "desc": desc,
                        "reply": "",
                        "status": "Pending",
                    }
                )
                .execute()
            )
            return res.data[0] if res.data else None
        except Exception as e:
            print(f"add_doubt error: {e}")
            return None

    def submit_reply(self, doubt_id, reply_text):
        """Updates the reply on a doubt and sets status to Replied if currently Pending."""
        try:
            # Fetch current status first
            cur = (
                self.client.table("doubts")
                .select("status")
                .eq("id", doubt_id)
                .execute()
            )
            current_status = cur.data[0]["status"] if cur.data else "Pending"
            new_status = "Replied" if current_status == "Pending" else current_status

            self.client.table("doubts").update(
                {"reply": reply_text, "status": new_status}
            ).eq("id", doubt_id).execute()
            return True
        except Exception as e:
            print(f"submit_reply error: {e}")
            return False

    def get_doubts_for_student(self, student_username):
        """Returns list of doubts submitted by a specific student."""
        try:
            res = (
                self.client.table("doubts")
                .select("id, student, subject, teacher, severity, urgent, explain, desc, reply, status")
                .eq("student", student_username)
                .execute()
            )
            return res.data or []
        except Exception as e:
            print(f"get_doubts_for_student error: {e}")
            return []

    def get_all_doubts(self):
        """Returns all doubts (used by chat for looking up a doubt by id)."""
        try:
            res = (
                self.client.table("doubts")
                .select("id, student, subject, teacher, severity, urgent, explain, desc, reply, status")
                .execute()
            )
            return res.data or []
        except Exception as e:
            print(f"get_all_doubts error: {e}")
            return []

    def get_doubts_for_teacher(self, teacher_username):
        """Returns doubts received by a specific teacher."""
        try:
            res = (
                self.client.table("doubts")
                .select("id, student, subject, teacher, severity, urgent, explain, desc, reply, status")
                .eq("teacher", teacher_username)
                .execute()
            )
            return res.data or []
        except Exception as e:
            print(f"get_doubts_for_teacher error: {e}")
            return []

    def resolve_doubt(self, doubt_id):
        """Sets the doubt status to 'Resolved'."""
        try:
            self.client.table("doubts").update({"status": "Resolved"}).eq(
                "id", doubt_id
            ).execute()
            return True
        except Exception as e:
            print(f"resolve_doubt error: {e}")
            return False

    def unresolve_doubt(self, doubt_id):
        """Sets the doubt status back to 'Pending'."""
        try:
            self.client.table("doubts").update({"status": "Pending"}).eq(
                "id", doubt_id
            ).execute()
            return True
        except Exception as e:
            print(f"unresolve_doubt error: {e}")
            return False

    # ──────────────────────────────────────────────────────
    # Subjects & Teachers
    # ──────────────────────────────────────────────────────

    def get_subjects(self):
        """Returns list of subjects."""
        try:
            res = self.client.table("subjects").select("subject").execute()
            return [r["subject"] for r in (res.data or [])]
        except Exception as e:
            print(f"get_subjects error: {e}")
            return []

    def get_teachers(self):
        """Returns list of teacher usernames."""
        try:
            res = (
                self.client.table("users")
                .select("username")
                .eq("role", "teacher")
                .execute()
            )
            return [r["username"] for r in (res.data or [])]
        except Exception as e:
            print(f"get_teachers error: {e}")
            return []

    # ──────────────────────────────────────────────────────
    # Chat Messages
    # ──────────────────────────────────────────────────────

    def get_chat_messages(self, doubt_id):
        """Returns all chat messages for a given doubt ID, ordered by timestamp."""
        try:
            res = (
                self.client.table("chat_messages")
                .select("sender, message, timestamp")
                .eq("doubt_id", doubt_id)
                .order("timestamp", desc=False)
                .execute()
            )
            return res.data or []
        except Exception as e:
            print(f"get_chat_messages error: {e}")
            return []

    def add_chat_message(self, doubt_id, sender, message):
        """Adds a new chat message."""
        try:
            self.client.table("chat_messages").insert(
                {"doubt_id": doubt_id, "sender": sender, "message": message}
            ).execute()
        except Exception as e:
            print(f"add_chat_message error: {e}")
