#!/usr/bin/env python3
# Max Goldt Bot -- a Reddit bot that responds to bild.de links in comments
# with a quote from writer Max Goldt and an archive.is version of the linked
# bild.de article(s)
#
# Version:      0.5.0
# Authors:      Eric Haberstroh <eric@erixpage.de>,
#               Jonas Schatz <jonas.schatz+github@googlemail.com>
# License:      MIT <https://opensource.org/licenses/MIT>

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, List
import archiveis
from urllib.parse import ParseResult, urlparse
import logging
import os
import praw
import prawcore.exceptions
import re
import sys
import time


@dataclass
class Config:
    subreddit: str
    client_id: str
    client_secret: str
    user_agent: str
    username: str
    password: str

    def __init__(self):
        self.subreddit = os.environ["subreddit"]
        self.client_id = os.environ["client_id"]
        self.client_secret = os.environ["client_secret"]
        self.user_agent = os.environ["user_agent"]
        self.username = os.environ["username"]
        self.password = os.environ["password"]


class MaxGoldtBotEntityParser(ABC):
    regex: str = "(?<!/)(http[s]?://(?:www|m).bild.de/(?:[-a-zA-Z0-9/_\.\?=,])+)"
    sleeptime: int = 1500
    processed_entities: List[str] = []

    processed_entities_file: str
    entity_type: str
    reddit: praw.Reddit
    subreddit: Any
    entity_provider: Any

    def __init__(self, config: Config):

        logging.debug(
            f"{self.entity_type} Creating Reddit instance for username {config.username}"
        )

        self.reddit = praw.Reddit(
            client_id=config.client_id,
            client_secret=config.client_secret,
            user_agent=config.user_agent,
            username=config.username,
            password=config.password,
        )

        self.subreddit = self.reddit.subreddit(config.subreddit)

        self.processed_entities_file: str = (
            f"processed_{self.entity_type}_file_{config.subreddit}.txt"
        )

        logging.debug(
            f"[{self.entity_type}] Storing processed entites in {self.processed_entities_file}"
        )

        try:
            with open(self.processed_entities_file, "r+") as file:
                for line in file:
                    line = line.strip()
                    self.processed_entities.append(line)
            logging.debug(
                f"[{self.entity_type}] Read {len(self.processed_entities)} processed {self.entity_type} in total"
            )
        except (FileNotFoundError, IOError):
            logging.warning(
                f"[{self.entity_type}] File {self.processed_entities_file} could not be read"
            )

    def run(self):
        while True:
            try:
                for entity in self.entity_provider:
                    if entity.id in self.processed_entities:
                        continue
                    self.handle_entity(entity)
                    self.processed_entities.append(entity.id)

                try:
                    with open(self.processed_entites_file, "a") as file:
                        file.write(entity.id + "\n")
                except IOError as e:
                    logging.error(
                        f"[{self.entity_type}] IO error while writing to {self.processed_entities_file}: {e}"
                    )
                if len(self.processed_entities) > 600:
                    self.processed_entities = self.prune_logfile()

            except (
                praw.exceptions.APIException,
                praw.exceptions.ClientException,
                prawcore.exceptions.RequestException,
            ) as e:
                logging.warning(f"[{self.entity_type}] Got an exception: {e}")
                logging.warning(
                    f"[{self.entity_type}] Will go to sleep for {self.sleeptime} seconds"
                )
                time.sleep(self.sleeptime)
            except KeyboardInterrupt:
                logging.critical(
                    f"[{self.entity_type}] Bot has been killed by keyboard interrupt. Exiting"
                )
                sys.exit(0)

    def handle_entity(self, entity):
        logging.debug("[comments] Processing new comment %s", entity.id)
        urls: List[str] = self.extract_urls
        if urls:
            logging.info(
                f"[{self.entity_type}] New {self.entity_type} with bild.de URLs found"
            )
            archive_urls: List[str] = self.search_and_archive_bild_urls(urls)

            if archive_urls:
                body = self.create_submission_body(archive_urls)
                entity.reply(body)
                logging.info(
                    "[comments] Replied to %s with %d links",
                    entity.id,
                    len(archive_urls),
                )
            else:
                logging.warning(
                    "[comments] No reply to %s: %d bild.de links found, none archived",
                    entity.id,
                    len(urls),
                )

        else:
            logging.debug(f"[{self.entity_type}] No relevant URLs found in {entity.id}")

    @abstractmethod
    def extract_urls(self, entity) -> List[str]:
        pass

    def search_and_archive_bild_urls(self, urls: List[str]) -> List[str]:
        archive_urls: List[str] = []
        bildplus: int = 0

        for url in urls:
            parsed_url: ParseResult = urlparse(url)
            if parsed_url.path.startswith("/bild-plus/"):
                logging.info(
                    f"[{self.entity_type}] Skipping {url} because it is probably a BILD+ link"
                )
                bildplus += 1
                continue
            logging.info(f"[{self.entity_type}] Capturing url")
            archive_url: str = archiveis.capture(url)
            if archive_url:
                archive_urls.append(archive_url)
                logging.info(f"[{self.entity_type}] Captured: {archive_url}")
            else:
                logging.warning(
                    f"[{self.entity_type}] Got an empty archive.is URL back. Something is wrong"
                )
        if len(urls) != len(archive_urls) + bildplus:
            logging.warning(
                f"[{self.entity_type}] Found {len(urls)} bild.de URLs, but got only {len(archive_urls)} archive.is links"
            )

        return archive_urls

    def create_submission_body(archive_urls: List[str]) -> str:
        links: str = "\n- ".join(archive_urls)
        body: str = (
            "> Diese Zeitung ist ein Organ der Niedertracht. Es ist falsch, sie zu lesen.\n"
            "> Jemand, der zu dieser Zeitung beiträgt, ist gesellschaftlich absolut inakzeptabel.\n"
            "> Es wäre verfehlt, zu einem ihrer Redakteure freundlich oder auch nur höflich zu sein.\n"
            "> Man muß so unfreundlich zu ihnen sein, wie es das Gesetz gerade noch zuläßt.\n"
            "> Es sind schlechte Menschen, die Falsches tun.\n\n"
            "[Max Goldt](https://de.wikipedia.org/wiki/Max_Goldt), deutscher Schriftsteller\n\n"
            "Du kannst diesen Artikel auf archive.is lesen, wenn du nicht auf bild.de gehen willst:\n\n- "
            + links
            + "\n\n"
            "----\n\n"
            "^^[Info](https://www.reddit.com/r/MaxGoldtBot)&nbsp;|&nbsp;"
            "[Autor](https://www.reddit.com/u/joni_corazon)&nbsp;|&nbsp;"
            "[GitHub](https://github.com/jonasschatz/MaxGoldtBot)&nbsp;|&nbsp;"
            "[Warum&nbsp;die&nbsp;Bild&nbsp;schlecht&nbsp;ist]"
            "(http://www.bildblog.de/62600/warum-wir-gegen-die-bild-zeitung-kaempfen/)"
        )
        return body

    def prune_logfile(self):
        logging.info(
            f"[{self.entity_type}] Pruning {self.processed_entities_file} to 500 {self.entity_type}"
        )
        try:
            with open(self.processed_entities, "w") as file:
                for entity in self.processed_entities[-500:]:
                    file.write(entity + "\n")
            return self.processed_entities[-500:]
        except IOError as e:
            logging.error(
                f"{[self.entity_type]} IO error while writing to {self.processed_entities_file}: {e}"
            )


class MaxGoldtBotCommentParser(MaxGoldtBotEntityParser):
    def __init__(self, config: Config):
        self.entity_type: str = "comments"
        super().__init__(config)
        self.entity_provider = self.subreddit.stream.comments(skip_existing=True)

    def extract_urls(self, entity) -> List[str]:
        return re.findall(self.regex, entity.body)


class MaxGoldtBotSubmissionParser(MaxGoldtBotEntityParser):
    def __init__(self, config: Config):
        self.entity_type: str = "submissions"
        super().__init__(config)
        self.entity_provider = self.subreddit.stream.submissions(skip_existing=True)

    def extract_urls(self, entity) -> List[str]:
        if entity.selftext == "":
            return re.findall(self.regex, entity.url)
        else:
            return re.findall(self.regex, entity.selftext)


if __name__ == "__main__":
    config: Config = Config()

    newpid: int = os.fork()
    if newpid == 0:
        logging.info("Started handling submissions")
        submission_parser = MaxGoldtBotSubmissionParser(config)
        submission_parser.run()
    else:
        logging.info("Started handling comments (submissions given to PID %d)", newpid)
        comment_parser = MaxGoldtBotCommentParser(config)
        comment_parser.run()
