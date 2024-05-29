#!/usr/bin/env python3

import os
import re
import argparse
import json

from typing import Any
from github import Github
from github import Auth
import xml.etree.ElementTree as ET


def parse_arguments() -> Any:
    parser = argparse.ArgumentParser(
        prog="main.py",
    )

    parser.add_argument("-m", "--manifest", type=str, required=True)
    parser.add_argument("-p", "--pull_requests", type=str, required=True)

    return parser.parse_args()


if __name__ == "__main__":
    auth = Auth.Token(os.environ.get("GITHUB_TOKEN"))

    gh = Github(auth=auth)

    args = parse_arguments()
    pull_requests = args.pull_requests.split(",")

    tree = ET.parse(args.manifest)
    root = tree.getroot()

    revisions = {}

    for pull_request_url in pull_requests:
        pull_request_url = pull_request_url.strip()
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

        # print(f"Repo: {repo}")
        # print(f"PR: {pull_request}")
        # print(f"Last Commit: {pull_request.get_commits().reversed[0]}")

        revisions[repo.name] = pull_request.get_commits().reversed[0].sha

    for project in root.iter("project"):
        repo_name = project.get("name")
        if repo_name in revisions.keys():
            project.set("revision", revisions[repo_name])

    tree.write(f"new-{args.manifest}")

    # To close connections after use
    gh.close()

    print(f"prs={[pr.strip() for pr in pull_requests]}")
