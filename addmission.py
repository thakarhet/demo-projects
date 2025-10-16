from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple

OPEN = "OPEN"
RESERVED_CATS = {"OBC", "SC", "ST", "EWS"}
ALL_CATS = [OPEN, "OBC", "SC", "ST", "EWS"]

@dataclass
class Student:
    sid: str
    rank: int
    category: str  # "GEN" or one of RESERVED_CATS; GEN uses only OPEN seats
    preferences: List[str]  # ordered list of branch codes
    total_marks: int = 0
    subject_marks: int = 0
    dob: str = "2000-01-01"  # ISO YYYY-MM-DD for easy comparison

    # runtime state
    assigned_branch: Optional[str] = None
    assigned_seat_type: Optional[str] = None  # OPEN or one of RESERVED_CATS
    assigned_pref_index: Optional[int] = None  # index in preferences

    def key(self) -> Tuple:
        # Sorting/tie-breaking key: lower is higher priority
        # Earlier DOB means older (preferred), ISO date sorts correctly
        return (self.rank, -self.total_marks, -self.subject_marks, self.dob, self.sid)

    def prefers(self, branch: str) -> bool:
        if branch not in self.preferences:
            return False
        if self.assigned_branch is None:
            return True
        return self.pref_index(branch) < self.assigned_pref_index

    def pref_index(self, branch: str) -> int:
        try:
            return self.preferences.index(branch)
        except ValueError:
            return 10**9

@dataclass
class AdmissionSystem:
    # seats[branch][seat_type] -> remaining seats
    seats: Dict[str, Dict[str, int]]
    students: List[Student] = field(default_factory=list)

    def _eligible_for(self, s: Student, seat_type: str) -> bool:
        if seat_type == OPEN:
            return True
        return s.category == seat_type  # only same reserved category can take reserved seat

    def _allocate(self, s: Student, branch: str, seat_type: str) -> None:
        assert self.seats[branch][seat_type] > 0, "No seat available to allocate"
        self.seats[branch][seat_type] -= 1
        s.assigned_branch = branch
        s.assigned_seat_type = seat_type
        s.assigned_pref_index = s.pref_index(branch)

    def initial_allocation(self) -> None:
        self.students.sort(key=lambda x: x.key())
        for s in self.students:
            for b in s.preferences:
                # Try OPEN first
                if self.seats.get(b, {}).get(OPEN, 0) > 0:
                    self._allocate(s, b, OPEN)
                    break
                # Then try reserved (if any)
                if s.category in RESERVED_CATS:
                    if self.seats.get(b, {}).get(s.category, 0) > 0:
                        self._allocate(s, b, s.category)
                        break

    def _best_candidate_for(self, branch: str, seat_type: str) -> Optional[Student]:
        best = None
        best_key = None
        for s in self.students:
            if branch not in s.preferences:
                continue
            if not self._eligible_for(s, seat_type):
                continue
            if not s.prefers(branch):
                continue
            k = s.key()
            if best is None or k < best_key:
                best = s
                best_key = k
        return best

    def upgrade_and_fill(self, branch: str, seat_type: str) -> None:
        vacancies = [(branch, seat_type)]
        while vacancies:
            b, t = vacancies.pop(0)
            while self.seats.get(b, {}).get(t, 0) > 0:
                cand = self._best_candidate_for(b, t)
                if cand is None:
                    break
                prev_b = cand.assigned_branch
                prev_t = cand.assigned_seat_type

                # Allocate new seat
                self.seats[b][t] -= 1
                cand.assigned_branch = b
                cand.assigned_seat_type = t
                cand.assigned_pref_index = cand.pref_index(b)

                # Free old seat and try to refill it
                if prev_b is not None:
                    self.seats[prev_b][prev_t] += 1
                    vacancies.append((prev_b, prev_t))

    # Real-time events
    def withdraw(self, sid: str) -> None:
        s = next((x for x in self.students if x.sid == sid), None)
        if not s or s.assigned_branch is None:
            return
        b, t = s.assigned_branch, s.assigned_seat_type
        # Free seat
        self.seats[b][t] += 1
        s.assigned_branch = None
        s.assigned_seat_type = None
        s.assigned_pref_index = None
        # Upgrade cascade
        self.upgrade_and_fill(b, t)

    def add_capacity(self, branch: str, seat_type: str, delta: int) -> None:
        self.seats.setdefault(branch, {}).setdefault(seat_type, 0)
        self.seats[branch][seat_type] += delta
        self.upgrade_and_fill(branch, seat_type)

    def snapshot(self):
        # Returns sorted list of assignments (sid, branch, seat_type)
        return [(s.sid, s.assigned_branch, s.assigned_seat_type)
                for s in sorted(self.students, key=lambda x: x.key())]

# Demo usage
if __name__ == "__main__":
    seats = {
        "CSE": {OPEN: 2, "OBC": 1, "SC": 1, "ST": 0, "EWS": 0},
        "ECE": {OPEN: 2, "OBC": 1, "SC": 1, "ST": 0, "EWS": 0},
        "ME":  {OPEN: 1, "OBC": 1, "SC": 0, "ST": 0, "EWS": 0},
    }
    students = [
        Student("S1", 1, "GEN", ["CSE", "ECE", "ME"], total_marks=480, subject_marks=95, dob="2004-02-01"),
        Student("S2", 2, "OBC", ["CSE", "ECE", "ME"], total_marks=475, subject_marks=94, dob="2004-05-10"),
        Student("S3", 3, "SC",  ["CSE", "ME"],        total_marks=470, subject_marks=90, dob="2004-03-20"),
        Student("S4", 4, "GEN", ["CSE", "ECE"],       total_marks=468, subject_marks=91, dob="2004-01-05"),
        Student("S5", 5, "OBC", ["ECE", "CSE", "ME"], total_marks=465, subject_marks=89, dob="2004-07-11"),
        Student("S6", 6, "GEN", ["ME", "CSE"],        total_marks=460, subject_marks=88, dob="2004-09-30"),
        Student("S7", 7, "SC",  ["CSE", "ECE"],       total_marks=455, subject_marks=85, dob="2004-04-01"),
        Student("S8", 8, "GEN", ["ECE"],              total_marks=450, subject_marks=84, dob="2004-12-12"),
    ]
    sys = AdmissionSystem(seats=seats, students=students)
    sys.initial_allocation()
    print("Initial allocation:", sys.snapshot())
    sys.withdraw("S1")
    print("After S1 withdraw:", sys.snapshot())
    sys.add_capacity("CSE", OPEN, 1)
    print("After adding 1 OPEN seat in CSE:", sys.snapshot())