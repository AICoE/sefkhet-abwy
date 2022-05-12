#!/usr/bin/env python3
# Sefkhet-Abwy
# Copyright(C) 2019,2020 Christoph Görn
#
# This program is free software: you can redistribute it and / or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


"""Sesheta's actions."""


import asyncio
import os
import logging
import typing
import random
import re


from httplib2 import Http
from apiclient.discovery import build, build_from_document
from oauth2client.service_account import ServiceAccountCredentials


_LOGGER = logging.getLogger(__name__)
THOTH_DEVOPS_SPACE = os.getenv("SESHETA_THOTH_DEVOPS_SPACE", None)  # pragma: no cover
AIOPS_DEVOPS_SPACE = os.getenv("SESHETA_AIOPS_DEVOPS_SPACE", None)  # pragma: no cover

# pragma: no cover
GITHUB_REALNAME_MAP = {
    "4n4nd": "Anand Sanmukhani",
    "anishasthana": "Anish Asthana",
    "bissenbay": "Bissenbay Dauletbayev",
    "bjoernh2000": "Bjoern Hasemann",
    "cermakm": "Marek Cermak",
    "chauhankaranraj": "Karan Chauhan",
    "codificat": "Pep Turro Mauri",
    "ddehueck": "Devin de Hueck",
    "dfeddema": "Diane Feddema",
    "durandom": "Marcel Hild",
    "elmiko": "Michael McCune",
    "erikerlandson": "Erik Erlandson",
    "fridex": "Frido Pokorny",
    "giorgoskarantonis": "Giorgos Karantonis",
    "goern": "Christoph Goern",
    "Gregory-Pereira": "Gregory Pereira",
    "harshad16": "Harshad Reddy Nalla",
    "hemajv": "Hema Veeradhi",
    "humairak": "Humair Khan",
    "kpostoffice": "Kevin Postlethwait",
    "larsks": "Lars Kellogg-Stedman",
    "llunved": "Daniel Riek",
    "mayacostantini": "Maya Costantini",
    "pacospace": "Francesco Murdaca",
    "saisankargochhayat": "Sai Sankar Gochhayat",
    "sefkhet-abwy[bot]": "Sesheta",
    "sentry-io[bot]": "Sentry",
    "sesheta": "Thoth Bot",
    "shruthi-raghuraman": "Shruthi Raghuraman",
    "shuels": "Steven Huels",
    "srushtikotak": "Srushti Vijay Kotak",
    "sub-mod": "Subin Modeel",
    "thoth-zuul[bot]": "Thoth's Zuul",
    "tumido": "Tomáš Coufal",
    "tushar7sharma": "Tushar Sharma",
    "xtuchyna": "Dominik Tuchyna",
    "zmhassan": "Zak Hassan",
}

# pragma: no cover
REALNAME_HANGOUTS_MAP = {
    "Aakanksha Duggal": "116540001948970893165",
    "Anand Sanmukhani": "109564390983160712413",
    "Anish Asthana": "106581684824747208909",
    "Bissenbay Dauletbayev": "114127285145989031675",
    "Bjoern Hasemann": "104621152329688050734",
    "Christoph Goern": "102814839969738411580",
    "Daniel Riek": "108515811437474839783",
    "Dominik Tuchyna": "101087488035276666197",
    "Francesco Murdaca": "108929048208403662680",
    "Frido Pokorny": "106810069271823707995",
    "Gage Krumbach": "113871793657874355068",
    "Giorgos Karantonis": "105147362480487195696",
    "Gregory Pereira": "110871412292783354026",
    "Harshad Reddy Nalla": "102648456274370715335",
    "Hema Veeradhi": "108530691726729807637",
    "Humair Khan": "117385119761143413973",
    "Jay Koehler": "114322650206028409507",
    "Karan Chauhan": "110694159944095156438",
    "Kevin Postlethwait": "102547849534309033904",
    "Lars Kellogg-Stedman": "115262905965225092168",
    "Lumir Balhar": "112869503906875156604",
    "Marcel Hild": "116445288136441446998",
    "Maya Costantini": "114714675359837244370",
    "Michael Clifford": "109712205974970623061",
    "Oindrilla Chatterjee": "116534249849252473521",
    "Pep Turro Mauri": "116298489646489899913",
    "Peter Patnaik": "110765933482047866243",
    "Sai Sankar Gochhayat": "112057774963535139749",
    "Sanjay Arora": "113204564998958160149",
    "Shrey Anand": "111485576658452106792",
    "Shruthi Raghuraman": "103427213209555601141",
    "Srushti Vijay Kotak": "117644001277054930712",
    "Steven Huels": "110846043168213103522",
    "Subin Modeel": "100912928295723672901",
    "Thorsten Schwesig": "113225722019550298128",
    "Tom Coufal": "117471959508522471287",
    "Tomáš Coufal": "117471959508522471287",
    "Tushar Sharma": "117540998919883245003",
    "Viliam Podhajecky": "107991398788108238503",
}

# pragma: no cover
# this is a set of github logins we dont want to see in hangout notifications
GITHUB_LOGIN_FILTER = [
    "bissenbay",
    "cermakm",
    "ddehueck",
    "dfeddema",
    "elmiko",
    "saisankargochhayat",
    "shruthi-raghuraman",
    "shuels",
    "srushtikotak",
    "zmhassan",
    "giorgoskarantonis",
]

# pragma: no cover
POSITIVE_GOOGLE_CHAT_EMOJIS = ["😸", "😊", "😌", "🙏", "👍", "😇", "☺️", "👌", "ヽ(ヅ)ノ"]


# pragma: no cover
URL_REGEX = re.compile(
    r"^(?:http|ftp)s?://"  # http:// or https://
    r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # domain...
    r"localhost|"  # localhost...
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|"  # ...or ipv4
    r"\[?[A-F0-9]*:[A-F0-9:]+\]?)"  # ...or ipv6
    r"(?::\d+)?"  # optional port
    r"(?:/?|[/?]\S+)$",
    re.IGNORECASE,
)


def hangouts_room_for(data: str) -> str:
    """Return the Google Hangout Chat Room for the given GitHub repository name."""
    if any(org in data.lower() for org in ["thoth-station", "sefkhet-abwy", "sesheta", "srcopsmetrics"]):
        return THOTH_DEVOPS_SPACE
    if "AICoE" in data:
        return AIOPS_DEVOPS_SPACE
    else:
        return None


def hangouts_userid(github_user: str) -> str:
    """Map GitHub user to Google Hangout Chat user ID."""
    try:
        return f"<users/{REALNAME_HANGOUTS_MAP[GITHUB_REALNAME_MAP[github_user.lower()]]}>"
    except KeyError as exc:
        return github_user


def realname(github_user: str) -> str:
    """Map GitHub user to Real Name."""
    return GITHUB_REALNAME_MAP.get(github_user.lower(), github_user)


def notify_channel(kind: str, message: str, thread_key: str, url: str) -> None:
    """Send message to a Google Hangouts Chat space."""
    response = None
    scopes = ["https://www.googleapis.com/auth/chat.bot"]
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        "/opt/app-root/etc/gcloud/sesheta-chatbot.json", scopes,
    )
    http_auth = credentials.authorize(Http())

    chat = build("chat", "v1", http=http_auth)

    SPACE = hangouts_room_for(url)

    if SPACE is None:
        return

    if kind.upper() in ["NEW_PULL_REQUEST", "NEW_PULL_REQUEST_REVIEW", "PULL_REQUEST_REVIEW", "REBASE_PULL_REQUEST"]:
        response = (
            chat.spaces()
            .messages()
            .create(parent=SPACE, body=create_pull_request_response(message, url), threadKey=thread_key)
        )
    elif kind.upper() == "NEW_ISSUE":
        response = (
            chat.spaces()
            .messages()
            .create(parent=SPACE, body=create_issue_response(message, url), threadKey=thread_key)
        )
    elif (kind.upper() == "MERGED_PULL_REQUEST") or (kind.upper() == "PLAIN"):
        response = chat.spaces().messages().create(parent=SPACE, body={"text": message}, threadKey=thread_key)
    elif kind.upper() == "PROMETHEUS_ALERT":
        response = (
            chat.spaces()
            .messages()
            .create(parent=SPACE, body=create_prometheus_alert(message, url), threadKey=thread_key)
        )

    if response is not None:
        response.execute()


def create_pull_request_response(message: str, url: str) -> dict:
    """Create a Google Hangouts Chat Card."""
    response = dict()
    cards = list()
    widgets = list()
    header = None

    widgets.append({"textParagraph": {"text": message}})
    widgets.append({"buttons": [{"textButton": {"text": "open this PR", "onClick": {"openLink": {"url": url}}}}]})

    cards.append({"sections": [{"widgets": widgets}]})

    response["cards"] = cards
    id = url.split("/")[-1]
    response["name"] = f"pull_request-{id}"

    return response


def create_prometheus_alert(message: str, url: str) -> dict:
    """Create a Google Hangouts Chat Card for prometheus alert."""
    response = dict()
    cards = list()
    widgets = list()

    widgets.append({"textParagraph": {"text": message}})
    widgets.append({"buttons": [{"textButton": {"text": "open the Alert", "onClick": {"openLink": {"url": url}}}}]})
    cards.append({"sections": [{"widgets": widgets}]})
    response["cards"] = cards
    response["name"] = f"prometheus_alert"
    return response


def create_issue_response(message: str, url: str) -> dict:
    """Create a Google Hangouts Chat Card."""
    response = dict()
    cards = list()
    widgets = list()
    header = None

    widgets.append({"textParagraph": {"text": message}})
    widgets.append({"buttons": [{"textButton": {"text": "open this Issue", "onClick": {"openLink": {"url": url}}}}]})
    widgets.append(
        {
            "buttons": [
                {
                    "textButton": {
                        "text": "list all open Issues",
                        "onClick": {
                            "openLink": {
                                "url": "https://github.com/issues?q=is%3Aopen+is%3Apr+archived%3Afalse+user%3Athoth-station",  # Ignore PycodestyleBear (E501)
                            },
                        },
                    },
                },
            ],
        },
    )

    cards.append({"sections": [{"widgets": widgets}]})

    response["cards"] = cards
    id = url.split("/")[-1]
    response["name"] = f"issue-{id}"

    return response


def eligible_release_pullrequest(pullrequest: dict) -> bool:
    """Check if the merged Pull Request is eligible to trigger a release."""
    # check if we have the 'bots' label
    try:
        if not any(label.get("name", None) == "bot" for label in pullrequest["labels"]):
            _LOGGER.debug(
                f"No 'bot' label on Release Pull Request: '{pullrequest['title']}', not eligible for release!",
            )
            return False
    except KeyError as exc:
        _LOGGER.debug(f"Not any label on Release Pull Request")
        _LOGGER.exception(exc)
        return False

    # check if Kebechet was the author pullrequest['user']['login']
    if pullrequest["user"]["login"] not in ["sesheta", "khebhut[bot]"]:
        _LOGGER.debug(
            f"Author of Release Pull Request: '{pullrequest['title']}' is not 'Sesheta', not eligible for release!",
        )
        return False

    return True


def get_release_issue(pullrequest: dict) -> int:
    """Figure out which Issue is related to this Release Pull Request."""
    try:
        # TODO maybe we need to split the body by \n and process each line?!
        for line in pullrequest["body"].splitlines():
            if line.upper().startswith("CLOSES"):
                _, issue = line.split("#", maxsplit=1)
                return int(issue)  # FIXME this might fail
    except KeyError as exc:
        _LOGGER.error(exc)
        return None

    return None


def random_positive_emoji2() -> str:
    """Pick a random positive emoji."""
    return random.choice(POSITIVE_GOOGLE_CHAT_EMOJIS)


def extract_url_from_text(text: str) -> typing.Union[typing.List[str], str, None]:
    """Extract the URL from a piece of text."""
    return URL_REGEX.search(text)
