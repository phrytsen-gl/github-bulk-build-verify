#!/usr/bin/env python3

import os
import re
import argparse
import json

from typing import Any
from github import Github
from github import Auth


def parse_arguments() -> Any:
    parser = argparse.ArgumentParser(
        prog="main.py",
    )

    parser.add_argument("-p", "--pull_requests", type=str, required=True)

    return parser.parse_args()


if __name__ == "__main__":
    auth = Auth.Token(os.environ.get("GITHUB_TOKEN"))

    gh = Github(auth=auth)

    args = parse_arguments()
    pull_requests = json.loads(args.pull_requests)

    for pull_request_url in pull_requests:
        if not re.match(
            r"https://github.com/[a-zA-Z0-9\-_.]+/[a-zA-Z0-9\-_.]+/pull/[0-9]+",
            pull_request_url,
        ):
            raise ValueError(
                f"Invalid GitHub PullRequest URL provided: {pull_request_url}"
            )

        url_parts = pull_request_url.split("/")
        repo = gh.get_repo("/".join(url_parts[-4:-2]))
        pull_request = repo.get_pull(int(url_parts[-1]))

        print(f"Repo: {repo}")
        print(f"PR: {pull_request}")
        print(f"Last Commit: {pull_request.get_commits().reversed[0]}")

    # To close connections after use
    gh.close()
