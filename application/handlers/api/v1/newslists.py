import json
import logging
import time

from application.config import constants
from application.handlers.base import BaseHandler
from google.appengine.api import urlfetch
from google.appengine.api import memcache


class NewsListsApiHandler(BaseHandler):
    def post(self):
        news_api_key = self.get_arg("news_api_key")
        page = self.get_arg("page")

        if not news_api_key:
            logging.debug("Required parameter `news_api_key` is missing.")
            self.api_response = {
                "code": constants.HTTP_CODE_BAD_REQUEST,
                "message": "Error! Missing required parameter `news_api_key`."
            }
            self.api_render()
            return
        if not page:
            logging.debug("Required parameter `page` is missing.")
            self.api_response = {
                "code": constants.HTTP_CODE_BAD_REQUEST,
                "message": "Error! Missing required parameter `page`."
            }
            self.api_render()
            return

        existing_memcache_data = memcache.get(page)

        should_fetch_from_news_api = True
        if not existing_memcache_data:
            logging.debug("Memcache data does not exist.")
            should_fetch_from_news_api = True
        elif existing_memcache_data and does_memcache_exceeds_ttl(existing_memcache_data):
            logging.debug("Memcache data exists but timestamp exceeds TTL.")
            should_fetch_from_news_api = True
        elif existing_memcache_data:
            logging.debug("Memcache data for page " + str(page) + " exists.")
            logging.debug("Returning memcache data.")
            should_fetch_from_news_api = False
            self.api_response = existing_memcache_data["data"]
            self.api_render()

            logging.debug(existing_memcache_data)

        if should_fetch_from_news_api:
            url = constants.NEWS_API_ENDPOINT \
                  + "?apiKey=" + news_api_key \
                  + "&page=" + str(page) \
                  + "&pageSize=" + str(constants.NEWS_API_PAGESIZE) \
                  + "&sources=" + constants.NEWS_API_SOURCES

            response = urlfetch.fetch(url)

            if response.status_code == 200:
                logging.debug("NewsAPI fetch successful.")

                data = json.loads(response.content)

                logging.debug(data)

                self.api_response = data
                self.api_render()

                add_data_to_memcache(page, data)
            else:
                logging.debug("NewsAPI fetch failed. Response code: ")
                logging.debug(response.status_code)

                # If something went wrong while fetching
                # data from NewsAPI and there's and existing_memcache_data.
                # Return existing_memcache_data.
                if existing_memcache_data:
                    logging.debug("Memcache data for page " + str(page) + " exists.")
                    logging.debug(existing_memcache_data)
                    self.api_response = existing_memcache_data["data"]
                    self.api_render()
                else:
                    self.api_response["code"] = 500
                    self.api_response["description"] = "Something went wrong. Please try again."
                    self.api_render()


def add_data_to_memcache(page, data):
    # https://stackoverflow.com/a/13891070/5285687
    current_time_in_seconds = time.time()

    memcache_data = {
        "page": page,
        "timestamp": current_time_in_seconds,
        "data": data
    }

    memcache_add = memcache.add(page, memcache_data)

    if memcache_add:
        logging.debug("Successfully added page=" + str(page)
                      + " and timestamp=" + str(current_time_in_seconds)
                      + " to memcache")
    else:
        logging.debug("Error in adding page=" + str(page)
                      + " and timestamp=" + str(current_time_in_seconds)
                      + " to memcache")


def does_memcache_exceeds_ttl(memcache_data):
    """
    Returns true if memcache_data["timestamp"] does
    not exceed constants.MEMCACHE_TTL.

    :return: Boolean
    """
    current_time_in_seconds = time.time()
    memcache_data_timestamp = memcache_data["timestamp"]

    difference = current_time_in_seconds - memcache_data_timestamp

    if difference > constants.MEMCACHE_TTL:
        logging.debug("difference " + str(difference)
                      + " exceeds MEMCACHE_TTL " + str(constants.MEMCACHE_TTL))
        return True
    else:
        logging.debug("difference " + str(difference)
                      + " does not exceed MEMCACHE_TTL " + str(constants.MEMCACHE_TTL))
        return False
