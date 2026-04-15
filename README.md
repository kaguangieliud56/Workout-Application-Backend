# Workout Application Backend

A RESTful API backend for a workout tracking application used by personal trainers. Built with **Flask**, **SQLAlchemy**, and **Marshmallow**.



## Tech Stack

| Tool | Version |
|---|---|
| Python | 3.8.13+ |
| Flask | 2.2.2 |
| Flask-SQLAlchemy | 3.0.3 |
| Flask-Migrate | 3.1.0 |
| Marshmallow | 3.20.1 |
| Werkzeug | 2.2.2 |
| SQLite | (bundled) |

---

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/Workout-Application-Backend.git
cd Workout-Application-Backend
```

### 2. Install dependencies
```bash
pipenv install
pipenv shell
```

### 3. Navigate to the server directory
```bash
cd server
```

### 4. Initialize and run migrations
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade head
```

### 5. Seed the database
```bash
python seed.py
```

---

## Running the App

```bash
# From the server/ directory, with the virtual env active:
python app.py
```

The API will be available at **http://localhost:5555**

---

## API Endpoints

### Workouts

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/workouts` | List all workouts |
| `GET` | `/workouts/<id>` | Get a single workout with its exercises, reps/sets/duration |
| `POST` | `/workouts` | Create a new workout |
| `DELETE` | `/workouts/<id>` | Delete a workout (cascade-deletes its workout_exercises) |

#### POST /workouts — Request Body
```json
{
  "date": "2024-05-01",
  "duration_minutes": 45,
  "notes": "Optional notes here"
}
```

---

### Exercises

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/exercises` | List all exercises |
| `GET` | `/exercises/<id>` | Get a single exercise with its associated workouts |
| `POST` | `/exercises` | Create a new exercise |
| `DELETE` | `/exercises/<id>` | Delete an exercise (cascade-deletes its workout_exercises) |

#### POST /exercises — Request Body
```json
{
  "name": "Push-Up",
  "category": "strength",
  "equipment_needed": false
}
```

Allowed categories: `strength`, `cardio`, `flexibility`, `balance`, `endurance`, `hiit`, `yoga`, `other`

---

### WorkoutExercises (Join)

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/workouts/<workout_id>/exercises/<exercise_id>/workout_exercises` | Add an exercise to a workout |

#### Request Body
```json
{
  "reps": 15,
  "sets": 3,
  "duration_seconds": null
}
```

> At least one of `reps`, `sets`, or `duration_seconds` is required.

---

## Validations

### Table Constraints
- `exercises.name` — `NOT NULL` + `UNIQUE`
- `exercises.category` — `NOT NULL`
- `workouts.date` — `NOT NULL`
- `workouts.duration_minutes` — `NOT NULL`
- `workout_exercises.workout_id` — `NOT NULL` FK
- `workout_exercises.exercise_id` — `NOT NULL` FK
- `workout_exercises(workout_id, exercise_id)` — `UNIQUE` (no duplicate joins)

### Model Validations (`@validates`)
- `Exercise.name` — must be a non-empty string
- `Exercise.category` — must be an allowed category value
- `Workout.duration_minutes` — must be a positive integer
- `Workout.date` — must not be in the future
- `WorkoutExercise.reps/sets/duration_seconds` — must be positive if provided

### Schema Validations (Marshmallow)
- `name` — 1–100 characters
- `category` — must be one of the allowed enum values
- `duration_minutes` — 1–600 range
- `notes` — max 500 characters
- `reps/sets/duration_seconds` — minimum value of 1
- At least one metric (`reps`, `sets`, or `duration_seconds`) required per `WorkoutExercise`

---

## Project Structure

```
Workout-Application-Backend/
├── Pipfile
├── README.md
└── server/
    ├── app.py          # Flask app + all route definitions
    ├── models.py       # SQLAlchemy models with constraints & validations
    ├── schemas.py      # Marshmallow schemas for serialization/validation
    ├── seed.py         # Database seed script
    └── instance/
        └── app.db      # SQLite database (auto-generated)
```
