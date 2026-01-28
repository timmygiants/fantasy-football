import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from typing import Dict, List
from datetime import datetime
import pytz

st.set_page_config(
    page_title="Scoreboard - Fantasy Football Playoffs", page_icon="📊", layout="wide"
)

PLAYOFF_WEEKS = ["Wildcard", "Divisional", "Conference", "Super Bowl"]

# Game start times (Eastern Time)
GAME_START_TIMES = {
    "Wildcard": datetime(
        2026, 1, 10, 16, 25, tzinfo=pytz.timezone("US/Eastern")
    ),  # 4:25 PM EST
    "Divisional": datetime(
        2026, 1, 17, 16, 25, tzinfo=pytz.timezone("US/Eastern")
    ),  # Update as needed
    "Conference": datetime(
        2026, 1, 25, 15, 00, tzinfo=pytz.timezone("US/Eastern")
    ),  # Update as needed
    "Super Bowl": datetime(
        2026, 2, 8, 5, 25, tzinfo=pytz.timezone("US/Eastern")
    ),  # Update as needed
}


def games_have_started(week: str) -> bool:
    """Check if games have started for a given week"""
    if week not in GAME_START_TIMES:
        return False  # Hide if no start time defined

    now = datetime.now(pytz.timezone("US/Eastern"))
    return now >= GAME_START_TIMES[week]


def get_most_recent_started_week() -> str:
    """Get the most recent week that has started, or first week if none have started"""
    now = datetime.now(pytz.timezone("US/Eastern"))
    
    started_weeks = []
    for week in PLAYOFF_WEEKS:
        if week in GAME_START_TIMES and now >= GAME_START_TIMES[week]:
            started_weeks.append(week)
    
    # Return the last started week (most recent), or first week if none have started
    return started_weeks[-1] if started_weeks else PLAYOFF_WEEKS[0]


@st.cache_resource
def init_gsheets():
    """Initialize Google Sheets connection"""
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        return conn
    except Exception as e:
        st.error(f"Failed to connect to Google Sheets: {e}")
        return None


@st.cache_data(ttl=30)
def load_picks_from_sheet(_conn) -> pd.DataFrame:
    """Load all picks from Google Sheet"""
    try:
        df = _conn.read(worksheet="Picks", usecols=list(range(10)), ttl=30)
        return df
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=30)
def load_scores_from_sheet(_conn) -> pd.DataFrame:
    """Load all scores from Google Sheet"""
    try:
        df = _conn.read(worksheet="scores", ttl=30)
        return df
    except Exception:
        return pd.DataFrame()


def normalize_player_name(name: str) -> str:
    """Normalize player name for matching by removing common suffixes and variations."""
    if not name:
        return ""
    # Remove common suffixes that might be added after scoring
    name = str(name).strip()
    # Remove " - Please pay ASAP" and similar suffixes
    if " - " in name:
        name = name.split(" - ")[0].strip()
    return name


def normalize_username(name: str) -> str:
    """Normalize username for matching by removing common suffixes and variations."""
    # Same normalization as player names - handles cases where user names change
    return normalize_player_name(name)


def get_player_score(scores_df: pd.DataFrame, player_name: str, week: str) -> float:
    """Get fantasy points for a specific player in a specific week"""
    if scores_df.empty or not player_name:
        return 0.0

    # Normalize the input player name
    normalized_input = normalize_player_name(player_name)
    
    # Try exact match first
    player_scores = scores_df[
        (scores_df["playerName"] == player_name) & (scores_df["gameWeek"] == week)
    ]
    
    # If no exact match, try normalized match
    if player_scores.empty and normalized_input != player_name:
        # Normalize all player names in scores_df for comparison
        scores_df_normalized = scores_df.copy()
        scores_df_normalized["playerName_normalized"] = scores_df_normalized["playerName"].apply(normalize_player_name)
        
        player_scores = scores_df_normalized[
            (scores_df_normalized["playerName_normalized"] == normalized_input) & 
            (scores_df_normalized["gameWeek"] == week)
        ]

    if player_scores.empty:
        return 0.0

    try:
        return float(player_scores.iloc[0].get("fantasyPoints", 0))
    except (ValueError, TypeError):
        return 0.0


def get_user_week_scores(
    picks_df: pd.DataFrame, scores_df: pd.DataFrame, username: str, week: str
) -> Dict[str, float]:
    """Get all player scores for a user's lineup in a specific week"""
    if picks_df.empty:
        return {}

    # Try exact match first
    user_picks = picks_df[
        (picks_df["User Name"] == username) & (picks_df["Week"] == week)
    ]

    # If no exact match, try normalized match (handles cases where user names changed)
    if user_picks.empty:
        normalized_username = normalize_username(username)
        if normalized_username != username:
            # Normalize all user names in picks_df for comparison
            picks_df_normalized = picks_df.copy()
            picks_df_normalized["User Name_normalized"] = picks_df_normalized["User Name"].apply(normalize_username)
            
            user_picks = picks_df_normalized[
                (picks_df_normalized["User Name_normalized"] == normalized_username) & 
                (picks_df_normalized["Week"] == week)
            ]

    if user_picks.empty:
        return {}

    # Sort by Timestamp (descending) to get the most recent submission
    # Handle both exact match and normalized match cases
    if "Timestamp" in user_picks.columns:
        try:
            # Convert Timestamp to datetime for proper sorting
            user_picks = user_picks.copy()
            user_picks["Timestamp"] = pd.to_datetime(user_picks["Timestamp"], errors="coerce")
            user_picks = user_picks.sort_values("Timestamp", ascending=False, na_position="last")
        except Exception:
            # If timestamp parsing fails, just use the order from the sheet
            pass
    
    # Get the most recent submission (first row after sorting)
    pick_row = user_picks.iloc[0]
    position_cols = ["QB", "RB1", "RB2", "WR1", "WR2", "TE"]

    scores = {}
    for col in position_cols:
        player = pick_row.get(col, "")
        if player and pd.notna(player):
            scores[col] = {
                "player": str(player),
                "points": get_player_score(scores_df, str(player), week),
            }
        else:
            scores[col] = {"player": "", "points": 0.0}

    return scores


def get_user_total_points(
    picks_df: pd.DataFrame, scores_df: pd.DataFrame, username: str, weeks: List[str]
) -> Dict[str, float]:
    """Get total points for a user across specified weeks"""
    week_totals = {}
    grand_total = 0.0

    for week in weeks:
        week_scores = get_user_week_scores(picks_df, scores_df, username, week)
        week_total = sum(p["points"] for p in week_scores.values())
        week_totals[week] = week_total
        grand_total += week_total

    return {"weeks": week_totals, "total": grand_total}


def render_lineup_details(week_scores: Dict, show_players: bool = True) -> None:
    """Render the lineup player rows"""
    for pos in ["QB", "RB1", "RB2", "WR1", "WR2", "TE"]:
        player_data = week_scores.get(pos, {"player": "", "points": 0.0})
        player_name = player_data.get("player", "") or "-"

        # Hide player names if games haven't started
        if not show_players and player_name != "-":
            player_name = "🔒 Hidden"

        points = player_data.get("points", 0.0)
        points_display = f"{points:.1f}" if points > 0 else "-"

        cols = st.columns([1, 3, 1])
        with cols[0]:
            st.caption(pos)
        with cols[1]:
            st.write(player_name)
        with cols[2]:
            st.write(f"**{points_display}**")


def render_baseball_card(
    username: str,
    week_scores: Dict,
    week_total: float,
    running_total: float,
    rank: int,
    selected_week: str,
    show_players: bool = True,
) -> None:
    """Render a baseball card style view for a user's lineup (expanded)"""

    with st.container(border=True):
        # Header row with name and season total
        header_cols = st.columns([2, 1.5, 1.5])
        with header_cols[0]:
            st.markdown(f"**#{rank} {username}**")
        with header_cols[1]:
            st.markdown(f"**{selected_week}**")
            st.markdown(f"**{week_total:.1f}**")
        with header_cols[2]:
            st.markdown(f"**Season**")
            st.markdown(f"**{running_total:.1f}**")

        st.divider()

        render_lineup_details(week_scores, show_players)


def render_collapsible_card(
    username: str,
    week_scores: Dict,
    week_total: float,
    running_total: float,
    rank: int,
    selected_week: str,
    show_players: bool = True,
) -> None:
    """Render a collapsible card showing summary, with lineup revealed on click"""

    with st.container(border=True):
        # Summary header always visible
        header_cols = st.columns([2, 1.5, 1.5])
        with header_cols[0]:
            st.markdown(f"**#{rank} {username}**")
        with header_cols[1]:
            st.markdown(f"**{selected_week}**")
            st.markdown(f"**{week_total:.1f}**")
        with header_cols[2]:
            st.markdown(f"**Season**")
            st.markdown(f"**{running_total:.1f}**")

        # Collapsible lineup details
        with st.expander("View Lineup"):
            render_lineup_details(week_scores, show_players)


def render_scoreboard(
    picks_df: pd.DataFrame, scores_df: pd.DataFrame, selected_week: str
) -> None:
    """Render the full scoreboard view"""
    if picks_df.empty:
        st.info("No picks have been submitted yet.")
        return

    # Check if player names should be shown
    show_players = games_have_started(selected_week)

    # Get all unique user names, but normalize them to group variations together
    # We'll use the most recent (longest) version of each normalized name for display
    all_raw_users = picks_df["User Name"].dropna().unique().tolist()
    
    # Group users by normalized name, keeping the longest version for display
    user_name_map = {}  # normalized -> display name (longest version)
    for user in all_raw_users:
        normalized = normalize_username(user)
        if normalized not in user_name_map or len(user) > len(user_name_map[normalized]):
            user_name_map[normalized] = user
    
    # Use the display names (most recent versions) for the list
    all_users = list(user_name_map.values())

    if not all_users:
        st.info("No users found with picks.")
        return

    # Calculate running totals for all users
    # Note: get_user_total_points and get_user_week_scores will handle name normalization
    user_totals = []
    for user in all_users:
        totals = get_user_total_points(picks_df, scores_df, user, PLAYOFF_WEEKS)
        user_totals.append(
            {
                "username": user,
                "running_total": totals["total"],
                "week_totals": totals["weeks"],
            }
        )

    # Sort by running total (descending)
    user_totals.sort(key=lambda x: x["running_total"], reverse=True)

    # Show lock notice if games haven't started
    if not show_players:
        st.info("🔒 Player lineups will be revealed when games start.")

    # Get current user if authenticated
    current_user = st.session_state.get("username", "")
    
    # Normalize current user for matching
    normalized_current_user = normalize_username(current_user) if current_user else ""

    # Find current user's data and rank (match by normalized name)
    current_user_data = None
    current_user_rank = None

    for i, user_data in enumerate(user_totals):
        # Match by normalized name to handle name variations
        if normalize_username(user_data["username"]) == normalized_current_user:
            current_user_data = user_data
            current_user_rank = i + 1
            break

    # Render current user's section if authenticated and has picks
    if current_user and current_user_data:
        st.markdown(f"### Your Lineup - {selected_week}")

        week_scores = get_user_week_scores(
            picks_df, scores_df, current_user, selected_week
        )
        week_total = sum(p["points"] for p in week_scores.values())

        # Always show current user's own lineup expanded
        render_baseball_card(
            username=current_user,
            week_scores=week_scores,
            week_total=week_total,
            running_total=current_user_data["running_total"],
            rank=current_user_rank,
            selected_week=selected_week,
            show_players=True,  # User can always see their own lineup
        )

        st.markdown("---")

    # Render all users in rankings section (including current user)
    st.markdown("### Rankings")

    cols_per_row = 3
    for i in range(0, len(user_totals), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, col in enumerate(cols):
            if i + j < len(user_totals):
                user_data = user_totals[i + j]
                username = user_data["username"]
                rank = i + j + 1

                week_scores = get_user_week_scores(
                    picks_df, scores_df, username, selected_week
                )
                week_total = sum(p["points"] for p in week_scores.values())

                # Current user can always see their own lineup (match by normalized name)
                user_show_players = True if normalize_username(username) == normalized_current_user else show_players

                with col:
                    render_collapsible_card(
                        username=username,
                        week_scores=week_scores,
                        week_total=week_total,
                        running_total=user_data["running_total"],
                        rank=rank,
                        selected_week=selected_week,
                        show_players=user_show_players,
                    )


def main():
    st.title("📊 Weekly Scoreboard")
    st.markdown("---")

    # Initialize session state for authentication (shared with main app)
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "username" not in st.session_state:
        st.session_state.username = ""

    # Show login status
    if st.session_state.authenticated and st.session_state.username:
        st.caption(f"Logged in as: **{st.session_state.username}**")
    else:
        st.caption("Not logged in - [Go to Home to login](./)")

    conn = init_gsheets()
    if conn is None:
        st.stop()

    # Load data
    picks_df = load_picks_from_sheet(conn)
    scores_df = load_scores_from_sheet(conn)

    # Get default week (most recent started week)
    default_week = get_most_recent_started_week()
    default_index = PLAYOFF_WEEKS.index(default_week)

    # Week selector
    selected_week = st.selectbox(
        "Select Week to View:", PLAYOFF_WEEKS, index=default_index, key="scoreboard_week_select"
    )

    st.markdown("---")

    render_scoreboard(picks_df, scores_df, selected_week)


if __name__ == "__main__":
    main()
