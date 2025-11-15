# GitHub Commits Fetcher

A Python script to fetch and export all your commits across all GitHub repositories (public and private) within a specified date range.

## Features

- 🔍 Fetches commits from **all your repositories** (public, private, and collaborative)
- 📅 Filter commits by custom date range
- 📊 Detailed summary with commit counts per repository
- 📤 Export options:
  - CSV format for data analysis
  - Markdown format for documentation
- 🔒 Supports private repositories with proper authentication
- 💻 Clean, colorful terminal output

## Prerequisites

- Python 3.6 or higher
- A GitHub Personal Access Token

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd github-commits-fetcher
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

1. Generate a GitHub Personal Access Token:
   - Go to [GitHub Settings → Tokens](https://github.com/settings/tokens)
   - Click **"Generate new token (classic)"**
   - Give it a name (e.g., "Commits Fetcher")
   - Select scope: **`repo`** (Full control of private repositories)
   - Click **"Generate token"** and copy it

2. Create your environment configuration:
```bash
cp .env.example .env
```

3. Edit `.env` file and add your credentials:
```env
GITHUB_TOKEN=your_github_personal_access_token_here
GITHUB_USERNAME=your_github_username
```

⚠️ **Important**: Never commit your `.env` file! Make sure it's in your `.gitignore`.

## Usage

Run the script with a date range:

```bash
python3 fetch_commits.py START_DATE END_DATE
```

### Example

Fetch commits from January 2024:
```bash
python3 fetch_commits.py 2024-01-01 2024-01-31
```

Fetch commits from the last week:
```bash
python3 fetch_commits.py 2025-11-08 2025-11-15
```

## Output

The script provides:

1. **Repository Discovery**: Lists all repositories being scanned
2. **Progress Indicator**: Shows real-time progress as it fetches commits
3. **Summary**: Total commits and breakdown by repository
4. **Detailed List**: All commits with:
   - Repository name and privacy status
   - Commit SHA
   - Date and time
   - Commit message
   - Direct link to commit

### Export Formats

After fetching, you can export the results:

- **CSV**: Spreadsheet-friendly format for analysis
- **Markdown**: Beautiful formatted document with links
- **Both**: Get both formats at once

## Example Output

```
================================================================================
GitHub All Repositories Commits Fetcher
================================================================================

Validating GitHub token... ✓
Authenticated as: username

Fetching your repositories (including private)...
Found 45 repositories

Fetching commits from 2024-01-01 to 2024-01-31...
--------------------------------------------------------------------------------
[1/45] [PUBLIC] username/project-1... ✓ 12 commits
[2/45] [PRIVATE] username/secret-project... ✓ 8 commits
...

================================================================================
SUMMARY
================================================================================
Total commits: 156
Repositories with commits: 12

Commits by repository:
  username/main-project: 45 commits
  username/side-project: 32 commits
  ...
```

## Security Notes

⚠️ **Important**: Protect your credentials!

- Never commit your `.env` file to version control
- Keep your GitHub token private
- Add `.env` to your `.gitignore` file
- Regenerate your token if accidentally exposed
- The token only needs `repo` scope
- Use `.env.example` as a template (safe to commit)

## License

MIT License - Feel free to use and modify as needed.

## Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests

## Author

Built by [dr5hn](https://github.com/dr5hn)

---

**Note**: This tool respects GitHub's API rate limits. For users with many repositories or commits, the script may take a few minutes to complete.
