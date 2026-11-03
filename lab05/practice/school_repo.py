import sqlite3


def students_in_program(con: sqlite3.Connection, program: str) -> list[str]:
    """Example function provided by lab."""
    cur = con.execute("SELECT name FROM students WHERE program = ?", (program,))
    return [row[0] for row in cur.fetchall()]


def add_student(con: sqlite3.Connection, name: str, year: int, program: str) -> int:
    """D1: Add a student and return the new student's id."""
    cur = con.execute(
        "INSERT INTO students (name, year, program) VALUES (?, ?, ?)",
        (name, year, program),
    )
    con.commit()
    return cur.lastrowid


def average_grade(con: sqlite3.Connection, course_code: str) -> float | None:
    """D2: Calculate average grade for a course code rounded to 2 decimals, or None."""
    cur = con.execute(
        "SELECT AVG(grade) FROM enrollments WHERE course_code = ?",
        (course_code,),
    )
    row = cur.fetchone()
    if row and row[0] is not None:
        return round(row[0], 2)
    return None


def transcript(con: sqlite3.Connection, student_id: int) -> list[tuple[str, int, float | None]]:
    """D3: Return student transcript (title, credits, grade) sorted by title."""
    cur = con.execute(
        """
        SELECT c.title, c.credits, e.grade
        FROM enrollments e
        JOIN courses c ON c.code = e.course_code
        WHERE e.student_id = ?
        ORDER BY c.title
        """,
        (student_id,),
    )
    return cur.fetchall()
