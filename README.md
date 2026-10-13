# Basketball Training System

A Python project for managing basketball player training data.

## Features

- Player information management
- Shooting statistics
- Training history recording
- Shooting evaluation system
- Recent 5 effective training days overall shooting percentage summary

## Recent Effective Training Days

The project can calculate the overall shooting percentage for the latest 5 effective training days from `Player.training_history`.

Rules:

- Training records are sorted by their actual ISO date values.
- Records from the same date are merged before deciding whether that date is effective.
- A training day is effective only when merged `shots >= 5`.
- The overall percentage is calculated as total made shots divided by total shots, then rounded to 1 decimal place.
- If fewer than 5 effective training days exist, available data is used and the result is marked as reference only.
- Missing dates, invalid dates, and illegal shooting data are skipped with user-facing messages.
- Existing `player.json` structure is reused; no new data fields are required.

Related methods:

- `Player.get_recent_effective_training_days(limit=5)`
- `Player.get_recent_effective_training_days_summary(limit=5)`
- `Player.show_recent_effective_training_days(limit=5)`

## Project Structure
```text
basketball_project
├── main.py
├── player.py
├── utils.py
├── report.py
├── player.json
└── README.md
```

##  How to Run
```bash
python main.py
```

## Technologies
- Python
- JSON
- Git
- GitHub

## Future Improvements

## Version History

## Author
Richard
