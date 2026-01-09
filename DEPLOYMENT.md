# Deploying Your Fantasy Football App to Streamlit Community Cloud

## Prerequisites

1. A GitHub account (free)
2. Your code pushed to a GitHub repository
3. A Streamlit Community Cloud account (free)

## Step-by-Step Deployment

### 1. Create a GitHub Repository

1. Go to [GitHub](https://github.com) and sign in
2. Click the "+" icon in the top right → "New repository"
3. Name it something like `fantasy-football-playoffs`
4. Make it **Public** (required for free Streamlit Cloud)
5. Click "Create repository"

### 2. Push Your Code to GitHub

**Option A: Using GitHub Desktop (Easiest)**
1. Download [GitHub Desktop](https://desktop.github.com/)
2. Clone your repository
3. Copy your `app.py`, `requirements.txt`, and `.gitignore` files to the repository folder
4. Commit and push

**Option B: Using Command Line**

```bash
cd /Users/timrob/Documents/fantasy-football

# Initialize git (if not already done)
git init

# Add files
git add app.py requirements.txt .gitignore README.md

# Commit
git commit -m "Initial commit - Fantasy Football Playoffs app"

# Add your GitHub repository as remote (replace with your repo URL)
git remote add origin https://github.com/YOUR_USERNAME/fantasy-football-playoffs.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Important:** Make sure `.streamlit/secrets.toml` is in `.gitignore` (it should be) - **NEVER commit your secrets!**

### 3. Deploy to Streamlit Community Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click "New app"
4. Fill in the details:
   - **Repository:** Select your `fantasy-football-playoffs` repository
   - **Branch:** `main` (or `master`)
   - **Main file path:** `app.py`
   - **App URL:** Choose a custom URL (e.g., `fantasy-football-playoffs`)
5. Click "Deploy!"

### 4. Configure Secrets

After deployment, you need to add your Google Sheets credentials:

1. In your Streamlit Cloud app dashboard, click "⚙️ Settings" (or "Manage app" → "Settings")
2. Click "Secrets" in the left sidebar
3. Paste your entire `.streamlit/secrets.toml` contents into the secrets editor
4. Click "Save"

**Important:** The secrets format should be exactly as in your `secrets.toml` file:

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
universe_domain = "googleapis.com"
```

### 5. Share the Link

Once deployed, your app will be available at:
```
https://YOUR_APP_NAME.streamlit.app
```

Share this link with your friends!

## Troubleshooting

### App won't deploy
- Make sure `requirements.txt` includes all dependencies
- Check that `app.py` is in the root of your repository
- Verify your repository is public (for free tier)

### "Failed to connect to Google Sheets"
- Double-check your secrets are correctly pasted in Streamlit Cloud
- Verify the service account email has access to your Google Sheet
- Make sure the spreadsheet URL is correct

### App is slow
- This is normal for free tier - it may take a few seconds to start
- The app "sleeps" after 1 hour of inactivity and takes ~30 seconds to wake up

## Security Notes

- ✅ Your secrets are encrypted and secure in Streamlit Cloud
- ✅ Never commit `secrets.toml` to GitHub
- ✅ The app URL is public, but users still need to login with passwords
- ✅ Consider making your Google Sheet "View only" for the service account if you want extra security

## Alternative: Private Deployment

If you want a private deployment (not public on GitHub), you can:
- Use Streamlit Cloud Teams (paid)
- Deploy to your own server (AWS, Google Cloud, etc.)
- Use other platforms like Heroku, Railway, or Render

For a friends-only app, the free public Streamlit Cloud option works great!
