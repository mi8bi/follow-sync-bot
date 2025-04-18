# Follow Sync Bot
A simple GitHub bot to manage your followers and following list. This bot helps you keep track of users you follow and automatically follow back, as well as unfollow users who no longer follow you.

## Features

 - Automatically follow back new followers.
 - Unfollow users who are no longer following you.
 - --dry-run mode to simulate the changes without actually modifying your following list.
 - Supports GitHub API for managing followers and following.

## Requirements

 - Python 3.12+
 - requests library for GitHub API communication
 - responses library for mocking API requests during tests

## Installation

1. Clone the repository

```bash
git clone https://github.com/mi8bi/follow-sync-bot.git
cd follow-sync-bot
```

2. Install dependencies

```bash
pip install -r requirements.txt
pip install -r dev-requirements.txt
```

## Usage
To run the bot and sync your followers and following list, use the following command:

```bash
python scripts/main.py --dry-run
```

### Options:

 - --dry-run: Simulate the follow/unfollow process without making any actual changes.

## Authentication
This bot uses a GitHub personal access token for authentication. You can generate a fine-grained token on GitHub and set it as an environment variable:

```bash
export GITHUB_TOKEN="your_personal_access_token"
```

Alternatively, you can modify the scripts/main.py to read the token from a file or a configuration.

## Running Tests
To run the tests for this project, use the following command:

```bash
pytest tests
```
### Test Configuration
Tests are written using pytest and responses libraries to mock API calls. You can add new tests or modify existing ones in the tests/ directory.

## CI/CD
This project uses GitHub Actions for continuous integration. The tests are automatically run on every push and pull request to the main branch.

### Schedule Workflow
The bot is also scheduled to run every day at 7:00 AM JST via GitHub Actions.

## Contributing
We welcome contributions to improve this project! If you want to contribute, please fork the repository, make changes, and create a pull request.

### Steps to contribute:

1. Fork this repository.

2. Clone your forked repository.

3. Create a new branch for your feature or bugfix.

4. Commit your changes and push them to your fork.

5. Create a pull request with a clear description of your changes.


## License
This project is licensed under the MIT License - see the LICENSE file for details.
