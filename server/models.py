"""
models.py
Defines SQLAlchemy models and relationships for the Workout Application.

Models:
    - Exercise: A reusable exercise (e.g., Push-up, Squat).
    - Workout: A training session with a date, duration, and optional notes.
    - WorkoutExercise: Join table linking Workouts to Exercises with reps/sets/duration.
"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from datetime import date

db = SQLAlchemy()


class Exercise(db.Model):
    """
    Represents a reusable exercise that can be added to many workouts.

    Table Constraints:
        - name must be unique and not null
        - category must not be null

    Model Validations:
        - name must be a non-empty string
        - category must be one of the allowed values
    """

    __tablename__ = "exercises"

    # ── Table-level constraints ────────────────────────────────────────
    __table_args__ = (
        db.UniqueConstraint("name", name="uq_exercise_name"),  # Constraint 1
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)            # Constraint 2: NOT NULL
    category = db.Column(db.String(50), nullable=False)         # Constraint 3: NOT NULL
    equipment_needed = db.Column(db.Boolean, nullable=False, default=False)

    # ── Relationships ──────────────────────────────────────────────────
    workout_exercises = db.relationship(
        "WorkoutExercise",
        back_populates="exercise",
        cascade="all, delete-orphan",   # Stretch goal: cascade delete
    )
    workouts = db.relationship(
        "Workout",
        secondary="workout_exercises",
        back_populates="exercises",
        overlaps="workout_exercises,exercise",
    )

    # ── Model Validations ──────────────────────────────────────────────
    ALLOWED_CATEGORIES = [
        "strength", "cardio", "flexibility",
        "balance", "endurance", "hiit", "yoga", "other"
    ]

    @validates("name")
    def validate_name(self, key, value):
        """Ensure the exercise name is a non-empty string."""
        if not value or not value.strip():
            raise ValueError("Exercise name must not be empty.")
        return value.strip()

    @validates("category")
    def validate_category(self, key, value):
        """Ensure the category is one of the allowed values."""
        if value.lower() not in self.ALLOWED_CATEGORIES:
            raise ValueError(
                f"Category must be one of: {', '.join(self.ALLOWED_CATEGORIES)}"
            )
        return value.lower()

    def __repr__(self):
        return f"<Exercise id={self.id} name='{self.name}' category='{self.category}'>"


class Workout(db.Model):
    """
    Represents a single training session.

    Table Constraints:
        - date must not be null
        - duration_minutes must not be null

    Model Validations:
        - duration_minutes must be a positive integer
        - date must not be in the future
    """

    __tablename__ = "workouts"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)                   # Constraint 4: NOT NULL
    duration_minutes = db.Column(db.Integer, nullable=False)    # Constraint 5: NOT NULL
    notes = db.Column(db.Text, nullable=True)

    # ── Relationships ──────────────────────────────────────────────────
    workout_exercises = db.relationship(
        "WorkoutExercise",
        back_populates="workout",
        cascade="all, delete-orphan",   # Stretch goal: cascade delete
    )
    exercises = db.relationship(
        "Exercise",
        secondary="workout_exercises",
        back_populates="workouts",
        overlaps="workout_exercises,workout",
    )

    # ── Model Validations ──────────────────────────────────────────────
    @validates("duration_minutes")
    def validate_duration(self, key, value):
        """Ensure duration is a positive integer."""
        if not isinstance(value, int) or value <= 0:
            raise ValueError("duration_minutes must be a positive integer.")
        return value

    @validates("date")
    def validate_date(self, key, value):
        """Ensure the workout date is not in the future."""
        if isinstance(value, date) and value > date.today():
            raise ValueError("Workout date cannot be in the future.")
        return value

    def __repr__(self):
        return f"<Workout id={self.id} date={self.date} duration={self.duration_minutes}min>"


class WorkoutExercise(db.Model):
    """
    Join table linking Workout and Exercise.
    Stores per-exercise specifics: reps, sets, and/or duration in seconds.

    Table Constraints:
        - workout_id and exercise_id are foreign keys (not null)
        - unique together: (workout_id, exercise_id) — an exercise cannot be
          added to the same workout twice

    Model Validations:
        - reps, sets, and duration_seconds must be positive if provided
    """

    __tablename__ = "workout_exercises"

    # ── Table-level constraints ────────────────────────────────────────
    __table_args__ = (
        db.UniqueConstraint(
            "workout_id", "exercise_id",
            name="uq_workout_exercise"          # Constraint 6: no duplicate entries
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(
        db.Integer,
        db.ForeignKey("workouts.id", ondelete="CASCADE"),
        nullable=False,                         # Constraint 7: NOT NULL FK
    )
    exercise_id = db.Column(
        db.Integer,
        db.ForeignKey("exercises.id", ondelete="CASCADE"),
        nullable=False,                         # Constraint 8: NOT NULL FK
    )
    reps = db.Column(db.Integer, nullable=True)
    sets = db.Column(db.Integer, nullable=True)
    duration_seconds = db.Column(db.Integer, nullable=True)

    # ── Relationships ──────────────────────────────────────────────────
    workout = db.relationship(
        "Workout",
        back_populates="workout_exercises",
        overlaps="exercises,workouts",
    )
    exercise = db.relationship(
        "Exercise",
        back_populates="workout_exercises",
        overlaps="exercises,workouts",
    )

    # ── Model Validations ──────────────────────────────────────────────
    @validates("reps")
    def validate_reps(self, key, value):
        """Ensure reps is positive if provided."""
        if value is not None and (not isinstance(value, int) or value <= 0):
            raise ValueError("reps must be a positive integer.")
        return value

    @validates("sets")
    def validate_sets(self, key, value):
        """Ensure sets is positive if provided."""
        if value is not None and (not isinstance(value, int) or value <= 0):
            raise ValueError("sets must be a positive integer.")
        return value

    @validates("duration_seconds")
    def validate_duration_seconds(self, key, value):
        """Ensure duration_seconds is positive if provided."""
        if value is not None and (not isinstance(value, int) or value <= 0):
            raise ValueError("duration_seconds must be a positive integer.")
        return value

    def __repr__(self):
        return (
            f"<WorkoutExercise workout_id={self.workout_id} "
            f"exercise_id={self.exercise_id}>"
        )
