# Fantasy Football Playoffs - One and Done App

A Streamlit application for managing a fantasy football playoff league where users can only pick each player once throughout the playoffs.

## Features

- ✅ User-friendly interface with name selection
- ✅ Position-based player filtering (QB, RB, WR, TE)
- ✅ Automatic validation to prevent duplicate player picks
- ✅ Google Sheets integration for data persistence
- ✅ Playoff week tracking (Wildcard, Divisional, Conference, Super Bowl)
- ✅ View previous picks and used players

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note:** The package name is `st-gsheets-connection` (with hyphens), but it's imported as `streamlit_gsheets` (with underscores) in Python. This is normal - the package name and module name can differ.

### 2. Set Up Google Sheets

1. Create a new Google Sheet
2. Create a worksheet named **"Picks"** (case-sensitive)
3. Add the following headers in row 1:
   - `User Name`
   - `Week`
   - `QB`
   - `RB1`
   - `RB2`
   - `WR1`
   - `WR2`
   - `TE`
   - `Timestamp`

4. Share the sheet with the service account email (see step 3 below)
5. Copy the Google Sheet URL (it should look like: `https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit`)

### 3. Configure Google Sheets API Access

You have two options for authentication:

#### Option A: Using Service Account (Recommended)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Sheets API:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google Sheets API"
   - Click "Enable"
4. Create a Service Account:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Give it a name (e.g., "fantasy-football-app")
   - Click "Create and Continue"
   - Skip role assignment (click "Continue")
   - Click "Done"
5. Create a Key:
   - Click on the service account you just created
   - Go to the "Keys" tab
   - Click "Add Key" > "Create new key"
   - Choose "JSON" format
   - Download the JSON file
6. Share your Google Sheet with the service account email (found in the JSON file, looks like `your-service-account@project-id.iam.gserviceaccount.com`)
7. Copy the contents of the JSON file

#### Option B: Using OAuth 2.0 (Alternative)

If you prefer OAuth 2.0, you'll need to set up OAuth credentials and use a different authentication method. The service account method is simpler for this use case.

### 4. Configure Streamlit Secrets

Create a `.streamlit` directory in your project folder (if it doesn't exist):

```bash
mkdir -p .streamlit
```

Create a file named `secrets.toml` inside the `.streamlit` directory with the following content:

```toml
[connections.gsheets]
spreadsheet = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit#gid=0"
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = """-----BEGIN PRIVATE KEY-----
YOUR_PRIVATE_KEY_HERE
-----END PRIVATE KEY-----"""
client_email = "your-service-account@project-id.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40project-id.iam.gserviceaccount.com"
```

**Important Notes:**
- Replace `YOUR_SHEET_ID` with your actual Google Sheet ID from the URL
- The section name is `[connections.gsheets]` (not `[gsheets]`)
- The spreadsheet URL key is `spreadsheet` (not `spreadsheet_url`)
- Copy all the values from the JSON file you downloaded into the `secrets.toml` file
- The `private_key` should be on multiple lines with the `"""` triple quotes
- Make sure the service account email has been shared with your Google Sheet

### 5. Run the Application

```bash
streamlit run app.py
```

The app will open in your default web browser at `http://localhost:8501`

## Google Sheet Structure

Your Google Sheet should have a worksheet named **"Picks"** with these columns:

| User Name | Week | QB | RB1 | RB2 | WR1 | WR2 | TE | Timestamp |
|-----------|------|----|----|----|----|----|----|-----------|
| John Doe | Wildcard | Patrick Mahomes | ... | ... | ... | ... | ... | 2024-01-15 10:30:00 |

## How It Works

1. **User Selection**: Users enter their name or select from existing users
2. **Week Selection**: Choose the current playoff week
3. **Player Selection**: 
   - Players are filtered by position
   - Already-used players are automatically excluded
   - Duplicate picks within the same lineup are prevented
4. **Validation**: 
   - Checks for empty selections
   - Prevents duplicate players in the same lineup
   - Prevents reusing players from previous weeks
5. **Submission**: Writes to Google Sheet with timestamp

## Customization

### Adding More Players

Edit the `SAMPLE_PLAYERS` dictionary in `app.py` to add or modify players:

```python
SAMPLE_PLAYERS = {
    "QB": ["Player 1", "Player 2", ...],
    "RB": [...],
    "WR": [...],
    "TE": [...]
}
```

### Loading Players from Google Sheet

To load players from a Google Sheet instead of hardcoding them:

1. Create a "Players" worksheet in your Google Sheet
2. Modify the `get_all_players()` function in `app.py` to read from the sheet

### Modifying Playoff Weeks

Edit the `PLAYOFF_WEEKS` list in `app.py`:

```python
PLAYOFF_WEEKS = ["Wildcard", "Divisional", "Conference", "Super Bowl"]
```

## Troubleshooting

### "Failed to connect to Google Sheets"
- Check that your `secrets.toml` file is correctly formatted
- Verify the service account email has access to the Google Sheet
- Ensure the Google Sheets API is enabled in your Google Cloud project

### "Could not load picks from sheet"
- Verify the worksheet is named exactly "Picks" (case-sensitive)
- Check that the column headers match exactly
- Ensure the service account has edit permissions on the sheet

### Players not showing as used
- Clear the Streamlit cache: Click the hamburger menu > "Clear cache" > "Clear all caches"
- Verify the picks are being saved correctly in the Google Sheet

## Security Notes

- Never commit your `secrets.toml` file to version control
- Add `.streamlit/secrets.toml` to your `.gitignore` file
- Keep your service account JSON key secure

## License

This project is for personal/friends use. Feel free to modify as needed!

