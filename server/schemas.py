"""
schemas.py
Marshmallow schemas for serialization, deserialization, and schema-level validation.

Schema Validations (meets requirement of 2+):
    - ExerciseSchema: name length and category enum check
    - WorkoutSchema: duration_minutes range check
    - WorkoutExerciseSchema: at least one of reps, sets, or duration_seconds required
"""

from marshmallow import (
    Schema,
    fields,
    validate,
    validates,
    validates_schema,
    ValidationError,
    post_load,
)

# ── Allowed categories (mirrors model) ────────────────────────────────────────
ALLOWED_CATEGORIES = [
    "strength", "cardio", "flexibility",
    "balance", "endurance", "hiit", "yoga", "other"
]


# ── WorkoutExercise Schema ─────────────────────────────────────────────────────
class WorkoutExerciseSchema(Schema):
    """
    Schema for the WorkoutExercise join table.

    Schema Validations:
        - reps/sets/duration_seconds must be positive if provided
        - at least one of reps, sets, or duration_seconds must be supplied
    """

    id = fields.Int(dump_only=True)
    workout_id = fields.Int(dump_only=True)
    exercise_id = fields.Int(dump_only=True)

    reps = fields.Int(
        load_default=None,
        validate=validate.Range(min=1, error="reps must be at least 1."),  # Schema Validation 1
    )
    sets = fields.Int(
        load_default=None,
        validate=validate.Range(min=1, error="sets must be at least 1."),  # Schema Validation 2
    )
    duration_seconds = fields.Int(
        load_default=None,
        validate=validate.Range(min=1, error="duration_seconds must be at least 1."),  # Schema Validation 3
    )

    @validates_schema
    def validate_at_least_one_metric(self, data, **kwargs):
        """Ensure at least one of reps, sets, or duration_seconds is provided."""  # Schema Validation 4
        if not any([data.get("reps"), data.get("sets"), data.get("duration_seconds")]):
            raise ValidationError(
                "At least one of 'reps', 'sets', or 'duration_seconds' must be provided."
            )

    # Nested exercise details for output (avoid circular import by using lambda)
    exercise = fields.Nested(lambda: ExerciseSchema(only=("id", "name", "category")), dump_only=True)


# ── Exercise Schema ────────────────────────────────────────────────────────────
class ExerciseSchema(Schema):
    """
    Schema for Exercise model.

    Schema Validations:
        - name: 1–100 characters, required
        - category: must be in ALLOWED_CATEGORIES
        - equipment_needed: boolean, required on create
    """

    id = fields.Int(dump_only=True)

    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100, error="name must be between 1 and 100 characters."),  # Schema Validation 5
    )
    category = fields.Str(
        required=True,
        validate=validate.OneOf(ALLOWED_CATEGORIES, error=f"category must be one of: {', '.join(ALLOWED_CATEGORIES)}."),  # Schema Validation 6
    )
    equipment_needed = fields.Bool(required=True)

    # Show associated workouts (summary only) when viewing a single exercise
    workouts = fields.List(
        fields.Nested(lambda: WorkoutSchema(only=("id", "date", "duration_minutes"))),
        dump_only=True,
    )


# ── Workout Schema ─────────────────────────────────────────────────────────────
class WorkoutSchema(Schema):
    """
    Schema for Workout model.

    Schema Validations:
        - date: required, must be a valid date string (YYYY-MM-DD)
        - duration_minutes: required, must be between 1 and 600
        - notes: optional string
    """

    id = fields.Int(dump_only=True)

    date = fields.Date(
        required=True,
        format="%Y-%m-%d",
        error_messages={"invalid": "date must be in YYYY-MM-DD format."},
    )
    duration_minutes = fields.Int(
        required=True,
        validate=validate.Range(min=1, max=600, error="duration_minutes must be between 1 and 600."),  # Schema Validation 7
    )
    notes = fields.Str(
        load_default=None,
        validate=validate.Length(max=500, error="notes must be 500 characters or fewer."),  # Schema Validation 8
    )

    # Show associated exercises + their per-workout metrics
    workout_exercises = fields.List(
        fields.Nested(WorkoutExerciseSchema),
        dump_only=True,
    )


# ── Instantiated schema objects used by routes ─────────────────────────────────
exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True)

workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)

workout_exercise_schema = WorkoutExerciseSchema()
