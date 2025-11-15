#!/usr/bin/env python3
"""
GitHub All Repositories Commits Fetcher
Fetches all commits made by you across all repositories (public and private) within a date range
"""

import requests
from datetime import datetime
import sys
import csv
from collections import defaultdict
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
USERNAME = os.getenv("GITHUB_USERNAME")


class GitHubCommitsFetcher:
    def __init__(self, username, token):
        self.username = username
        self.token = token
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.base_url = "https://api.github.com"

    def get_all_repositories(self):
        """Fetch all repositories (public and private) for the user"""
        repos = []
        page = 1

        print("Fetching your repositories (including private)...")

        while True:
            url = f"{self.base_url}/user/repos"
            params = {
                "per_page": 100,
                "page": page,
                "affiliation": "owner,collaborator,organization_member"
            }

            response = requests.get(url, headers=self.headers, params=params)

            if response.status_code != 200:
                print(f"Error fetching repositories: {response.status_code}")
                print(response.json())
                break

            batch = response.json()

            if not batch:
                break

            repos.extend(batch)

            if len(batch) < 100:
                break

            page += 1

        print(f"Found {len(repos)} repositories")
        return repos

    def get_commits_from_repo(self, repo_full_name, start_date, end_date):
        """Fetch commits from a specific repository"""
        owner, repo = repo_full_name.split('/')
        url = f"{self.base_url}/repos/{owner}/{repo}/commits"

        params = {
            "author": self.username,
            "since": f"{start_date}T00:00:00Z",
            "until": f"{end_date}T23:59:59Z",
            "per_page": 100
        }

        commits = []
        page = 1

        while True:
            params["page"] = page
            response = requests.get(url, headers=self.headers, params=params)

            if response.status_code != 200:
                # Skip repos where we don't have access or other errors
                break

            batch = response.json()

            if not batch:
                break

            commits.extend(batch)

            if len(batch) < 100:
                break

            page += 1

        return commits

    def fetch_all_commits(self, start_date, end_date):
        """Fetch all commits across all repositories"""
        repos = self.get_all_repositories()

        all_commits = []
        repo_commit_count = defaultdict(int)

        print(f"\nFetching commits from {start_date} to {end_date}...")
        print("-" * 80)

        for i, repo in enumerate(repos, 1):
            repo_name = repo['full_name']
            is_private = repo['private']
            privacy_label = "[PRIVATE]" if is_private else "[PUBLIC]"

            print(f"[{i}/{len(repos)}] {privacy_label} {repo_name}...", end=" ", flush=True)

            commits = self.get_commits_from_repo(repo_name, start_date, end_date)

            if commits:
                # Add repository info to each commit
                for commit in commits:
                    commit['repository'] = {
                        'full_name': repo_name,
                        'private': is_private,
                        'url': repo['html_url']
                    }

                all_commits.extend(commits)
                repo_commit_count[repo_name] = len(commits)
                print(f"✓ {len(commits)} commits")
            else:
                print("✓ 0 commits")

        # Sort commits by date (newest first)
        all_commits.sort(key=lambda x: x['commit']['committer']['date'], reverse=True)

        return all_commits, repo_commit_count


def display_commits(commits, repo_commit_count):
    """Display commits in a readable format"""
    if not commits:
        print("\n" + "=" * 80)
        print("No commits found in the specified date range.")
        print("=" * 80)
        return

    print("\n" + "=" * 80)
    print(f"SUMMARY")
    print("=" * 80)
    print(f"Total commits: {len(commits)}")
    print(f"Repositories with commits: {len(repo_commit_count)}")
    print()

    # Show breakdown by repository
    print("Commits by repository:")
    for repo, count in sorted(repo_commit_count.items(), key=lambda x: x[1], reverse=True):
        print(f"  {repo}: {count} commits")

    print("\n" + "=" * 80)
    print(f"DETAILED COMMIT LIST")
    print("=" * 80 + "\n")

    for i, commit in enumerate(commits, 1):
        repo_name = commit['repository']['full_name']
        is_private = commit['repository']['private']
        privacy_label = "[PRIVATE]" if is_private else "[PUBLIC]"

        commit_msg = commit['commit']['message'].split("\n")[0]  # First line only
        commit_date = commit['commit']['committer']['date']
        commit_url = commit['html_url']
        sha = commit['sha'][:7]

        # Format date nicely
        date_obj = datetime.strptime(commit_date, "%Y-%m-%dT%H:%M:%SZ")
        formatted_date = date_obj.strftime("%Y-%m-%d %H:%M")

        print(f"{i}. {privacy_label} [{repo_name}]")
        print(f"   SHA: {sha}")
        print(f"   Date: {formatted_date}")
        print(f"   Message: {commit_msg}")
        print(f"   URL: {commit_url}")
        print()


def export_to_csv(commits, filename):
    """Export commits to CSV file"""
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Date', 'Repository', 'Private', 'SHA', 'Message', 'URL']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for commit in commits:
            # Get full commit message (all lines)
            full_message = commit['commit']['message']

            writer.writerow({
                'Date': commit['commit']['committer']['date'],
                'Repository': commit['repository']['full_name'],
                'Private': 'Yes' if commit['repository']['private'] else 'No',
                'SHA': commit['sha'][:7],
                'Message': full_message.replace('\n', ' | '),  # Replace newlines with separator
                'URL': commit['html_url']
            })

    print(f"✓ Commits exported to {filename}")


def export_to_markdown(commits, repo_commit_count, start_date, end_date, filename):
    """Export commits to a formatted Markdown file"""
    with open(filename, 'w', encoding='utf-8') as mdfile:
        mdfile.write(f"# GitHub Commits Report\n\n")
        mdfile.write(f"**Period:** {start_date} to {end_date}\n\n")
        mdfile.write(f"**Total Commits:** {len(commits)}\n\n")
        mdfile.write(f"**Repositories:** {len(repo_commit_count)}\n\n")

        mdfile.write("## Summary by Repository\n\n")
        for repo, count in sorted(repo_commit_count.items(), key=lambda x: x[1], reverse=True):
            mdfile.write(f"- **{repo}**: {count} commits\n")

        mdfile.write("\n---\n\n## Detailed Commits\n\n")

        current_repo = None
        for commit in commits:
            repo_name = commit['repository']['full_name']
            is_private = commit['repository']['private']
            privacy_label = "🔒 Private" if is_private else "🌐 Public"

            # Add repo header if we're in a new repo
            if repo_name != current_repo:
                mdfile.write(f"\n### {privacy_label} {repo_name}\n\n")
                current_repo = repo_name

            commit_msg = commit['commit']['message'].split("\n")[0]
            commit_date = commit['commit']['committer']['date']
            commit_url = commit['html_url']
            sha = commit['sha'][:7]

            date_obj = datetime.strptime(commit_date, "%Y-%m-%dT%H:%M:%SZ")
            formatted_date = date_obj.strftime("%Y-%m-%d %H:%M")

            mdfile.write(f"- **{sha}** ({formatted_date}): {commit_msg} [→ View]({commit_url})\n")

    print(f"✓ Commits exported to {filename}")


def validate_token(token):
    """Validate GitHub token"""
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    response = requests.get("https://api.github.com/user", headers=headers)

    if response.status_code == 200:
        user_data = response.json()
        return True, user_data['login']
    elif response.status_code == 401:
        return False, "Invalid token"
    else:
        return False, f"Error: {response.status_code}"


def main():
    """Main function"""
    print("=" * 80)
    print("GitHub All Repositories Commits Fetcher")
    print("=" * 80)
    print()

    # Check if token and username are configured
    if not GITHUB_TOKEN or not USERNAME:
        print("ERROR: Please configure your GitHub Personal Access Token and Username")
        print()
        print("Steps:")
        print("1. Copy the .env.example file to .env")
        print("2. Go to https://github.com/settings/tokens")
        print("3. Click 'Generate new token (classic)'")
        print("4. Give it a name (e.g., 'Commits Fetcher')")
        print("5. Select scope: 'repo' (Full control of private repositories)")
        print("6. Click 'Generate token' and copy it")
        print("7. Edit the .env file and paste your token and username")
        print()
        sys.exit(1)

    # Validate token
    print("Validating GitHub token...", end=" ", flush=True)
    valid, result = validate_token(GITHUB_TOKEN)
    if not valid:
        print(f"\n\nERROR: {result}")
        print("Please check your GitHub token and try again.")
        sys.exit(1)
    print(f"✓\nAuthenticated as: {result}\n")

    # Get date range
    if len(sys.argv) != 3:
        print("Usage: python fetch_commits.py START_DATE END_DATE")
        print("Example: python fetch_commits.py 2024-01-01 2024-01-31")
        print()
        sys.exit(1)

    start_date = sys.argv[1]
    end_date = sys.argv[2]

    # Validate date format
    try:
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        print("ERROR: Dates must be in YYYY-MM-DD format")
        sys.exit(1)

    # Fetch commits
    fetcher = GitHubCommitsFetcher(USERNAME, GITHUB_TOKEN)
    commits, repo_commit_count = fetcher.fetch_all_commits(start_date, end_date)

    # Display results
    display_commits(commits, repo_commit_count)

    # Export options
    if commits:
        print("\n" + "=" * 80)
        print("EXPORT OPTIONS")
        print("=" * 80)

        while True:
            print("\nWould you like to export the commits?")
            print("1. Export to CSV")
            print("2. Export to Markdown")
            print("3. Export to both CSV and Markdown")
            print("4. No export, exit")

            choice = input("\nEnter your choice (1-4): ").strip()

            if choice == '1':
                csv_filename = f"commits_{start_date}_to_{end_date}.csv"
                export_to_csv(commits, csv_filename)
                break
            elif choice == '2':
                md_filename = f"commits_{start_date}_to_{end_date}.md"
                export_to_markdown(commits, repo_commit_count, start_date, end_date, md_filename)
                break
            elif choice == '3':
                csv_filename = f"commits_{start_date}_to_{end_date}.csv"
                md_filename = f"commits_{start_date}_to_{end_date}.md"
                export_to_csv(commits, csv_filename)
                export_to_markdown(commits, repo_commit_count, start_date, end_date, md_filename)
                break
            elif choice == '4':
                break
            else:
                print("Invalid choice. Please enter 1, 2, 3, or 4.")

    print("\nDone!")


if __name__ == "__main__":
    main()
