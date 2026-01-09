# Setup Guide for Fantasy Football App

## New Features Added

1. **Password Authentication** - Users must login with username and password
2. **Time-Based Editing** - Lineups can only be edited until 5 minutes before game time
3. **Dynamic Player List** - Players are loaded from the "Players" worksheet in Google Sheets

## Google Sheet Setup

### 1. Create "Users" Worksheet

Create a new worksheet named **"Users"** with these columns:
- `User Name` (column A)
- `Password` (column B)

Example:
```
User Name    | Password
-------------|----------
John Doe     | 1234
Jane Smith   | 5678
```

### 2. Create "Players" Worksheet

Create a new worksheet named **"Players"** with player data. You can organize it in two ways:

**Option A: Position Column Format**
- `Player Name` (column A)
- `Position` (column B) - Values: QB, RB, WR, or TE

Example:
```
Player Name          | Position
---------------------|----------
Patrick Mahomes      | QB
Josh Allen           | QB
Christian McCaffrey  | RB
...
```

**Option B: Column-Based Format**
- Column headers: `QB`, `RB`, `WR`, `TE`
- List players under each column

Example:
```
QB                  | RB                    | WR              | TE
--------------------|-----------------------|-----------------|------------------
Patrick Mahomes     | Christian McCaffrey   | Tyreek Hill     | Travis Kelce
Josh Allen          | Derrick Henry         | CeeDee Lamb     | Mark Andrews
...
```

### 3. Update Game Times

In `app.py`, update the `GAME_CUTOFF_TIMES` dictionary with the actual game start times (5 minutes before kickoff):

```python
GAME_CUTOFF_TIMES = {
    "Wildcard": datetime(2024, 1, 13, 16, 25, tzinfo=pytz.timezone('US/Eastern')),  # 4:25 PM EST
    "Divisional": datetime(2024, 1, 20, 16, 25, tzinfo=pytz.timezone('US/Eastern')),  # Update date/time
    "Conference": datetime(2024, 1, 27, 16, 25, tzinfo=pytz.timezone('US/Eastern')),  # Update date/time
    "Super Bowl": datetime(2024, 2, 11, 16, 25, tzinfo=pytz.timezone('US/Eastern')),  # Update date/time
}
```

**Format:** `datetime(year, month, day, hour, minute, tzinfo=pytz.timezone('US/Eastern'))`

The time should be **5 minutes before** the actual game start time.

## Installation

1. Install the new dependency:
   ```bash
   pip install pytz
   ```

   Or reinstall all requirements:
   ```bash
   pip install -r requirements.txt
   ```

## How It Works

### Authentication
- Users must login with their username and password
- Passwords are stored in the "Users" worksheet
- If no "Users" worksheet exists, the app allows any login (backward compatibility)

### Editing Restrictions
- Users can edit their lineups until 5 minutes before the first game of that week
- After the cutoff time, the submit/update button is disabled
- The app shows a warning message when editing is closed

### Player Loading
- Players are automatically loaded from the "Players" worksheet
- If the worksheet is empty or missing, the app falls back to sample players
- The app supports both position column format and column-based format

## Troubleshooting

### "No players found"
- Make sure the "Players" worksheet exists
- Check that column names match: "Player Name" and "Position" OR "QB", "RB", "WR", "TE"
- Ensure players are listed under the correct columns

### "Invalid username or password"
- Verify the "Users" worksheet exists with "User Name" and "Password" columns
- Check that usernames and passwords match exactly (case-sensitive)

### Editing not working
- Check that the game time is correctly set in `GAME_CUTOFF_TIMES`
- Verify the timezone is correct (US/Eastern)
- Make sure the date/time is in the future
