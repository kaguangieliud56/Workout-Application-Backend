#!/usr/bin/env python3
"""
seed.py
Populates the database with sample data for development and testing.

Run with:
    python seed.py
from the server/ directory (with the virtual env active).

This script:
    1. Clears all existing data (WorkoutExercise → Exercise → Workout order to respect FK).
    2. Creates sample exercises.
    3. Creates sample workouts.
    4. Links exercises to workouts via WorkoutExercise records.
"""

from datetime import date
from app import app
from models import db, Exercise, Workout, WorkoutExercise

with app.app_context():

    # ── 1. Clear existing data ─────────────────────────────────────────────────
    print("Clearing existing data...")
    WorkoutExercise.query.delete()
    Exercise.query.delete()
    Workout.query.delete()
    db.session.commit()

    # ── 2. Seed Exercises ──────────────────────────────────────────────────────
    print("Seeding exercises...")
    push_up = Exercise(name="Push-Up", category="strength", equipment_needed=False)
    squat = Exercise(name="Barbell Squat", category="strength", equipment_needed=True)
    plank = Exercise(name="Plank", category="balance", equipment_needed=False)
    jump_rope = Exercise(name="Jump Rope", category="cardio", equipment_needed=True)
    deadlift = Exercise(name="Deadlift", category="strength", equipment_needed=True)
    yoga_flow = Exercise(name="Sun Salutation", category="yoga", equipment_needed=False)
    box_jump = Exercise(name="Box Jump", category="hiit", equipment_needed=True)
    hip_flex = Exercise(name="Hip Flexor Stretch", category="flexibility", equipment_needed=False)

    db.session.add_all([push_up, squat, plank, jump_rope, deadlift, yoga_flow, box_jump, hip_flex])
    db.session.commit()
    print(f"   * {Exercise.query.count()} exercises created.")

    # ── 3. Seed Workouts ───────────────────────────────────────────────────────
    print("Seeding workouts...")
    w1 = Workout(
        date=date(2024, 4, 1),
        duration_minutes=45,
        notes="Morning strength session focus on upper body.",
    )
    w2 = Workout(
        date=date(2024, 4, 3),
        duration_minutes=30,
        notes="HIIT and cardio circuit.",
    )
    w3 = Workout(
        date=date(2024, 4, 5),
        duration_minutes=60,
        notes="Full-body day with flexibility cool-down.",
    )
    w4 = Workout(
        date=date(2024, 4, 8),
        duration_minutes=50,
        notes=None,   # notes are optional
    )

    db.session.add_all([w1, w2, w3, w4])
    db.session.commit()
    print(f"   * {Workout.query.count()} workouts created.")

    # ── 4. Seed WorkoutExercises ───────────────────────────────────────────────
    print("Linking exercises to workouts...")

    we_records = [
        # Workout 1 upper body strength
        WorkoutExercise(workout_id=w1.id, exercise_id=push_up.id, sets=4, reps=15),
        WorkoutExercise(workout_id=w1.id, exercise_id=squat.id, sets=4, reps=10),
        WorkoutExercise(workout_id=w1.id, exercise_id=plank.id, sets=3, duration_seconds=60),
        # Workout 2 HIIT
        WorkoutExercise(workout_id=w2.id, exercise_id=jump_rope.id, duration_seconds=300),
        WorkoutExercise(workout_id=w2.id, exercise_id=box_jump.id, sets=3, reps=12),
        # Workout 3 full body
        WorkoutExercise(workout_id=w3.id, exercise_id=deadlift.id, sets=5, reps=5),
        WorkoutExercise(workout_id=w3.id, exercise_id=push_up.id, sets=3, reps=20),
        WorkoutExercise(workout_id=w3.id, exercise_id=hip_flex.id, duration_seconds=120),
        WorkoutExercise(workout_id=w3.id, exercise_id=yoga_flow.id, duration_seconds=300),
        # Workout 4 no notes
        WorkoutExercise(workout_id=w4.id, exercise_id=squat.id, sets=3, reps=12),
        WorkoutExercise(workout_id=w4.id, exercise_id=deadlift.id, sets=3, reps=8),
    ]

    db.session.add_all(we_records)
    db.session.commit()
    print(f"   * {WorkoutExercise.query.count()} workout-exercise links created.")

    # ── 5. Quick verification ──────────────────────────────────────────────────
    print("\nSeed complete! Quick check:")
    for w in Workout.query.all():
        ex_names = [we.exercise.name for we in w.workout_exercises]
        print(f"   Workout #{w.id} ({w.date}) -> {ex_names}")
