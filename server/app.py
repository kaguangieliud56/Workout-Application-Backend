"""
app.py
Flask application entry point.

Registers all API routes for the Workout Application backend.

Endpoints:
    Workouts
        GET    /workouts                                          - list all workouts
        GET    /workouts/<id>                                     - get a workout with exercises
        POST   /workouts                                          - create a workout
        DELETE /workouts/<id>                                     - delete a workout (cascade)

    Exercises
        GET    /exercises                                         - list all exercises
        GET    /exercises/<id>                                    - get an exercise with workouts
        POST   /exercises                                         - create an exercise
        DELETE /exercises/<id>                                    - delete an exercise (cascade)

    WorkoutExercises
        POST   /workouts/<workout_id>/exercises/<exercise_id>/workout_exercises
                                                                  - add exercise to a workout
"""

from flask import Flask, make_response, request, jsonify
from flask_migrate import Migrate
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from models import db, Workout, Exercise, WorkoutExercise
from schemas import (
    workout_schema,
    workouts_schema,
    exercise_schema,
    exercises_schema,
    workout_exercise_schema,
)

# ── App Configuration ──────────────────────────────────────────────────────────
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

migrate = Migrate(app, db)
db.init_app(app)


# ── Helper ─────────────────────────────────────────────────────────────────────
def error_response(message, status_code):
    """Return a JSON error response with the given message and status code."""
    return make_response(jsonify({"error": message}), status_code)


@app.route("/")
def home():
    """Welcome route to confirm the API is running."""
    return "<h1>Workout API is Running</h1><p>Try visiting <a href='/workouts'>/workouts</a> to see your data.</p>"


# ══════════════════════════════════════════════════════════════════════════════
#  WORKOUT ROUTES
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/workouts", methods=["GET"])
def get_workouts():
    """
    GET /workouts
    Returns a list of all workouts (without nested exercises for brevity).
    """
    workouts = Workout.query.all()
    return make_response(jsonify(workouts_schema.dump(workouts)), 200)


@app.route("/workouts/<int:workout_id>", methods=["GET"])
def get_workout(workout_id):
    """
    GET /workouts/<id>
    Returns a single workout with its associated exercises and
    per-exercise reps/sets/duration data (stretch goal).
    """
    workout = db.session.get(Workout, workout_id)
    if not workout:
        return error_response(f"Workout with id {workout_id} not found.", 404)
    return make_response(jsonify(workout_schema.dump(workout)), 200)


@app.route("/workouts", methods=["POST"])
def create_workout():
    """
    POST /workouts
    Create a new workout.
    Expected JSON body: { "date": "YYYY-MM-DD", "duration_minutes": int, "notes": str (optional) }
    """
    json_data = request.get_json()
    if not json_data:
        return error_response("No input data provided.", 400)

    # ── Schema validation (deserialization) ───────────────────────────
    try:
        data = workout_schema.load(json_data)
    except ValidationError as err:
        return make_response(jsonify({"errors": err.messages}), 422)

    # ── Model validation + DB persist ─────────────────────────────────
    try:
        workout = Workout(
            date=data["date"],
            duration_minutes=data["duration_minutes"],
            notes=data.get("notes"),
        )
        db.session.add(workout)
        db.session.commit()
    except ValueError as err:
        db.session.rollback()
        return error_response(str(err), 422)
    except IntegrityError as err:
        db.session.rollback()
        return error_response("Database integrity error: " + str(err.orig), 422)

    return make_response(jsonify(workout_schema.dump(workout)), 201)


@app.route("/workouts/<int:workout_id>", methods=["DELETE"])
def delete_workout(workout_id):
    """
    DELETE /workouts/<id>
    Deletes a workout. Associated WorkoutExercise records are cascade-deleted.
    """
    workout = db.session.get(Workout, workout_id)
    if not workout:
        return error_response(f"Workout with id {workout_id} not found.", 404)

    db.session.delete(workout)
    db.session.commit()
    return make_response(jsonify({"message": f"Workout {workout_id} deleted successfully."}), 200)


# ══════════════════════════════════════════════════════════════════════════════
#  EXERCISE ROUTES
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/exercises", methods=["GET"])
def get_exercises():
    """
    GET /exercises
    Returns a list of all exercises.
    """
    exercises = Exercise.query.all()
    return make_response(jsonify(exercises_schema.dump(exercises)), 200)


@app.route("/exercises/<int:exercise_id>", methods=["GET"])
def get_exercise(exercise_id):
    """
    GET /exercises/<id>
    Returns a single exercise with the workouts it has been added to.
    """
    exercise = db.session.get(Exercise, exercise_id)
    if not exercise:
        return error_response(f"Exercise with id {exercise_id} not found.", 404)
    return make_response(jsonify(exercise_schema.dump(exercise)), 200)


@app.route("/exercises", methods=["POST"])
def create_exercise():
    """
    POST /exercises
    Create a new exercise.
    Expected JSON body: { "name": str, "category": str, "equipment_needed": bool }
    """
    json_data = request.get_json()
    if not json_data:
        return error_response("No input data provided.", 400)

    # ── Schema validation ─────────────────────────────────────────────
    try:
        data = exercise_schema.load(json_data)
    except ValidationError as err:
        return make_response(jsonify({"errors": err.messages}), 422)

    # ── Model validation + DB persist ─────────────────────────────────
    try:
        exercise = Exercise(
            name=data["name"],
            category=data["category"],
            equipment_needed=data["equipment_needed"],
        )
        db.session.add(exercise)
        db.session.commit()
    except ValueError as err:
        db.session.rollback()
        return error_response(str(err), 422)
    except IntegrityError:
        db.session.rollback()
        return error_response(f"An exercise named '{data['name']}' already exists.", 422)

    return make_response(jsonify(exercise_schema.dump(exercise)), 201)


@app.route("/exercises/<int:exercise_id>", methods=["DELETE"])
def delete_exercise(exercise_id):
    """
    DELETE /exercises/<id>
    Deletes an exercise. Associated WorkoutExercise records are cascade-deleted.
    """
    exercise = db.session.get(Exercise, exercise_id)
    if not exercise:
        return error_response(f"Exercise with id {exercise_id} not found.", 404)

    db.session.delete(exercise)
    db.session.commit()
    return make_response(jsonify({"message": f"Exercise {exercise_id} deleted successfully."}), 200)


# ══════════════════════════════════════════════════════════════════════════════
#  WORKOUT-EXERCISE JOIN ROUTE
# ══════════════════════════════════════════════════════════════════════════════

@app.route(
    "/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises",
    methods=["POST"],
)
def add_exercise_to_workout(workout_id, exercise_id):
    """
    POST /workouts/<workout_id>/exercises/<exercise_id>/workout_exercises
    Adds an exercise to a workout with optional reps, sets, and/or duration_seconds.
    Expected JSON body: { "reps": int, "sets": int, "duration_seconds": int }
    At least one metric is required (enforced by schema).
    """
    # ── Verify parent resources exist ─────────────────────────────────
    workout = db.session.get(Workout, workout_id)
    if not workout:
        return error_response(f"Workout with id {workout_id} not found.", 404)

    exercise = db.session.get(Exercise, exercise_id)
    if not exercise:
        return error_response(f"Exercise with id {exercise_id} not found.", 404)

    json_data = request.get_json() or {}

    # ── Schema validation ─────────────────────────────────────────────
    try:
        data = workout_exercise_schema.load(json_data)
    except ValidationError as err:
        return make_response(jsonify({"errors": err.messages}), 422)

    # ── Model validation + DB persist ─────────────────────────────────
    try:
        we = WorkoutExercise(
            workout_id=workout_id,
            exercise_id=exercise_id,
            reps=data.get("reps"),
            sets=data.get("sets"),
            duration_seconds=data.get("duration_seconds"),
        )
        db.session.add(we)
        db.session.commit()
    except ValueError as err:
        db.session.rollback()
        return error_response(str(err), 422)
    except IntegrityError:
        db.session.rollback()
        return error_response(
            f"Exercise {exercise_id} has already been added to Workout {workout_id}.", 422
        )

    return make_response(jsonify(workout_exercise_schema.dump(we)), 201)


# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app.run(port=5555, debug=True)
