class DoubtStore:
    def __init__(self):
        # In-memory shared doubts store
        self.doubts = []
        self._next_id = 1

        # Pre-configured user accounts
        self.users = {
            "student1": {"password": "s123", "role": "student"},
            "teacher1": {"password": "t123", "role": "teacher"},
        }

    def authenticate(self, username, password):
        """Returns role string ('student' or 'teacher') if valid, else None."""
        if username in self.users and self.users[username]["password"] == password:
            return self.users[username]["role"]
        return None

    def add_doubt(self, student, subject, teacher, severity, urgent, explain, desc):
        """Adds a new doubt dictionary to the store."""
        doubt = {
            "id": self._next_id,
            "student": student,
            "subject": subject,
            "teacher": teacher,
            "severity": severity,
            "urgent": urgent,
            "explain": explain,
            "desc": desc,
            "reply": ""
        }
        self.doubts.append(doubt)
        self._next_id += 1
        return doubt

    def submit_reply(self, doubt_id, reply_text):
        """Finds doubt by ID and sets the reply text."""
        for d in self.doubts:
            if d["id"] == doubt_id:
                d["reply"] = reply_text
                return True
        return False

    def get_doubts_for_student(self, student_username):
        """Returns list of doubts submitted by a specific student."""
        return [d for d in self.doubts if d["student"] == student_username]

    def get_all_doubts(self):
        """Returns all doubts (for teachers)."""
        return self.doubts
