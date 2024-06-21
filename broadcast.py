"""
This script is used to sent broadcast message to remind task proposer to submit pull requests.
"""

import requests

# Configuration
TOKEN = "YOUR GITHUB TOKEN"
REPO_OWNER = "dynamic-superb"
REPO_NAME = "dynamic-superb"
LABEL = "proposal confirmed"
COMMENT = "Just a friendly reminder to submit your pull request by June 28, 2024 (AoE time). If you've already done so, you can ignore this message. For details about task submission, please refer to the [task submission guidelines](https://github.com/dynamic-superb/dynamic-superb/blob/main/docs/task_submission.md). If you have any questions, feel free to leave a message here or send an email to dynamic.superb.official@gmail.com."

# Set up the headers with our token
headers = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}


def fetch_issues(url):
    while url:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            issues = response.json()
            for issue in issues:
                # Ensure the issue is not a pull request
                if "pull_request" not in issue:
                    # Post a comment on each issue
                    comment_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues/{issue['number']}/comments"
                    post_response = requests.post(
                        comment_url, headers=headers, json={"body": COMMENT}
                    )
                    print(
                        f"Commented on issue #{issue['number']} - Status: {post_response.status_code}"
                    )
            # Check for the 'next' page link
            if "next" in response.links:
                url = response.links["next"]["url"]
            else:
                url = None
        else:
            print(f"Failed to fetch issues - Status: {response.status_code}")
            url = None


# Start fetching issues
initial_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues?labels={LABEL}&per_page=100"
fetch_issues(initial_url)
