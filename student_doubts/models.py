import os
import json
import openpyxl

class DoubtStore:
    def __init__(self):
        # Resolve database paths relative to this file's directory
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.users_path = os.path.join(self.base_dir, "users.xlsx")
        self.doubts_path = os.path.join(self.base_dir, "doubts.xlsx")
        self.subjects_path = os.path.join(self.base_dir, "subjects.xlsx")
        self.config_path = os.path.join(self.base_dir, "config.json")

        self.users = {}
        self.subjects = []
        self.doubts = []
        self.default_users = []
        self.default_subjects = []
        self._next_id = 1

        # Load dynamic configurations
        self._load_config()

        # Initialize and load Excel databases
        self._init_users_file()
        self._init_subjects_file()
        self._init_doubts_file()
        self._load_data()

    def _load_config(self):
        default_config = {
            "default_users": [
                {"username": "student1", "password": "s123", "role": "student"},
                {"username": "teacher1", "password": "t123", "role": "teacher"},
                {"username": "Mr. Sharma", "password": "t123", "role": "teacher"},
                {"username": "Ms. Roy", "password": "t123", "role": "teacher"},
                {"username": "Dr. Sen", "password": "t123", "role": "teacher"}
            ],
            "default_subjects": [
                "Math",
                "Science",
                "English"
            ]
        }
        if not os.path.exists(self.config_path):
            try:
                with open(self.config_path, "w") as f:
                    json.dump(default_config, f, indent=2)
            except Exception:
                pass
            config = default_config
        else:
            try:
                with open(self.config_path, "r") as f:
                    config = json.load(f)
            except Exception:
                config = default_config

        self.default_users = config.get("default_users", default_config["default_users"])
        self.default_subjects = config.get("default_subjects", default_config["default_subjects"])

    def _init_users_file(self):
        if not os.path.exists(self.users_path):
            wb = openpyxl.Workbook()
            sheet = wb.active
            sheet.title = "Sheet"
            sheet.append(["username", "password", "role"])
            for uinfo in self.default_users:
                sheet.append([
                    uinfo.get("username", ""), 
                    uinfo.get("password", ""), 
                    uinfo.get("role", "")
                ])
            wb.save(self.users_path)
        else:
            wb = openpyxl.load_workbook(self.users_path)
            sheet = wb.active
            existing_usernames = set()
            for row in sheet.iter_rows(min_row=2, values_only=True):
                if row and row[0]:
                    existing_usernames.add(str(row[0]).strip().lower())
            
            modified = False
            for uinfo in self.default_users:
                u = uinfo.get("username", "")
                p = uinfo.get("password", "")
                r = uinfo.get("role", "")
                if u.strip().lower() not in existing_usernames:
                    sheet.append([u, p, r])
                    existing_usernames.add(u.strip().lower())
                    modified = True
            
            if modified:
                wb.save(self.users_path)

    def _init_subjects_file(self):
        if not os.path.exists(self.subjects_path):
            wb = openpyxl.Workbook()
            sheet = wb.active
            sheet.title = "Sheet"
            sheet.append(["subject"])
            for s in self.default_subjects:
                sheet.append([s])
            wb.save(self.subjects_path)

    def _init_doubts_file(self):
        expected_headers = ["id", "student", "subject", "teacher", "severity", "urgent", "explain", "desc", "reply"]
        if not os.path.exists(self.doubts_path):
            wb = openpyxl.Workbook()
            sheet = wb.active
            sheet.title = "Sheet"
            sheet.append(expected_headers)
            wb.save(self.doubts_path)
        else:
            # Check for header migration
            wb = openpyxl.load_workbook(self.doubts_path)
            sheet = wb.active
            headers = [cell.value for cell in sheet[1]]
            if headers != expected_headers:
                # Migrate database mapping old columns to the new layout
                col_map = {name: idx for idx, name in enumerate(headers) if name is not None}
                migrated_doubts = []
                for row in sheet.iter_rows(min_row=2, values_only=True):
                    def get_val(col_name, default=""):
                        if col_name in col_map and col_map[col_name] < len(row):
                            val = row[col_map[col_name]]
                            return val if val is not None else default
                        return default

                    try:
                        d_id_raw = get_val("id", None)
                        if d_id_raw is None:
                            continue
                        d_id = int(d_id_raw)
                    except (ValueError, TypeError):
                        continue

                    migrated_doubts.append({
                        "id": d_id,
                        "student": get_val("student"),
                        "subject": get_val("subject"),
                        "teacher": get_val("teacher"),
                        "severity": get_val("severity", "Low"),
                        "urgent": get_val("urgent", "No"),
                        "explain": get_val("explain", "No"),
                        "desc": get_val("desc"),
                        "reply": get_val("reply")
                    })
                
                # Overwrite/save the migrated sheet
                wb_new = openpyxl.Workbook()
                sheet_new = wb_new.active
                sheet_new.title = "Sheet"
                sheet_new.append(expected_headers)
                for d in migrated_doubts:
                    sheet_new.append([
                        d["id"],
                        d["student"],
                        d["subject"],
                        d["teacher"],
                        d["severity"],
                        d["urgent"],
                        d["explain"],
                        d["desc"],
                        d["reply"]
                    ])
                wb_new.save(self.doubts_path)

    def _load_data(self):
        # Load users
        wb_users = openpyxl.load_workbook(self.users_path)
        sheet_users = wb_users.active
        for row in sheet_users.iter_rows(min_row=2, values_only=True):
            if len(row) >= 3:
                username, password, role = row[0], row[1], row[2]
                if username:
                    self.users[str(username).strip()] = {
                        "password": str(password).strip() if password is not None else "",
                        "role": str(role).strip() if role is not None else ""
                    }

        # Load subjects
        wb_subjects = openpyxl.load_workbook(self.subjects_path)
        sheet_subjects = wb_subjects.active
        for row in sheet_subjects.iter_rows(min_row=2, values_only=True):
            if row and row[0]:
                self.subjects.append(str(row[0]).strip())

        # Load doubts
        wb_doubts = openpyxl.load_workbook(self.doubts_path)
        sheet_doubts = wb_doubts.active
        for row in sheet_doubts.iter_rows(min_row=2, values_only=True):
            if len(row) >= 9:
                try:
                    d_id = int(row[0])
                except (ValueError, TypeError):
                    continue
                self.doubts.append({
                    "id": d_id,
                    "student": str(row[1]) if row[1] is not None else "",
                    "subject": str(row[2]) if row[2] is not None else "",
                    "teacher": str(row[3]) if row[3] is not None else "",
                    "severity": str(row[4]) if row[4] is not None else "Low",
                    "urgent": str(row[5]) if row[5] is not None else "No",
                    "explain": str(row[6]) if row[6] is not None else "No",
                    "desc": str(row[7]) if row[7] is not None else "",
                    "reply": str(row[8]) if row[8] is not None else ""
                })
        
        if self.doubts:
            self._next_id = max(d["id"] for d in self.doubts) + 1
        else:
            self._next_id = 1

    def _save_doubts(self):
        wb = openpyxl.Workbook()
        sheet = wb.active
        sheet.title = "Sheet"
        sheet.append(["id", "student", "subject", "teacher", "severity", "urgent", "explain", "desc", "reply"])
        for d in self.doubts:
            sheet.append([
                d["id"],
                d["student"],
                d["subject"],
                d["teacher"],
                d["severity"],
                d["urgent"],
                d["explain"],
                d["desc"],
                d["reply"]
            ])
        wb.save(self.doubts_path)

    def authenticate(self, username, password):
        """Returns role string ('student' or 'teacher') if valid, else None."""
        u_clean = str(username).strip()
        p_clean = str(password).strip()
        if u_clean in self.users and self.users[u_clean]["password"] == p_clean:
            return self.users[u_clean]["role"]
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
        self._save_doubts()
        return doubt

    def submit_reply(self, doubt_id, reply_text):
        """Finds doubt by ID and sets the reply text."""
        for d in self.doubts:
            if d["id"] == doubt_id:
                d["reply"] = reply_text
                self._save_doubts()
                return True
        return False

    def get_doubts_for_student(self, student_username):
        """Returns list of doubts submitted by a specific student."""
        return [d for d in self.doubts if d["student"] == student_username]

    def get_all_doubts(self):
        """Returns all doubts (for teachers)."""
        return self.doubts

    def get_subjects(self):
        """Returns list of dynamic subjects."""
        return self.subjects

    def get_teachers(self):
        """Returns list of dynamic teachers."""
        return [uname for uname, uinfo in self.users.items() if uinfo["role"] == "teacher"]
