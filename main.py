import datetime as dt
import os
import re
import sys
from argparse import ArgumentParser

import requests

API_KEY = os.environ['API_KEY']
DATE = re.compile(r"(\d\d\d\d)-(\d\d)-(\d\d)")
TIMEOUT = 20


def main() -> None:
    """
    Validates the API key and command line arguments using argparse, then calls
    the relevant methods.

    :returns: None
    """

    if not API_KEY:
        sys.exit("API Key not set")

    parser = ArgumentParser(description="PyCuriosity is an API explorer that can get Mars rover Curiosity's images")
    parser.add_argument("-m", "--mars", nargs=2, dest="mars", metavar=("file_name", "date"),
                        help="write the Mars rover image urls to a text file")

    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit()

    if args.mars is not None:
        file_name, date = args.mars
        explore_mars_rover_photos(file_name, date)


def explore_mars_rover_photos(file_name: str, date: str) -> int:
    """
    Accesses NASA's Mars Rover Photos API, and puts image urls taken by the Curiosity Mars rover
    in specified text file, and saves the first image found. See NASA's Mars Rover Photos API at
    https://api.nasa.gov for more information and to signup for an API key.

    See the API documentation at https://github.com/corincerami/mars-photo-api

    :param date: The date to photos were captured, can't be today
    :type date: str
    :param file_name: The text file to write the image URLs
    :type file_name: str
    :returns: API response code
    :rtype: int
    """
    # Using regex, validates date
    if not re.search(DATE, date):
        print("Invalid date format, use YYYY-MM-DD.")
        return False

    # Check if file name is valid
    if not file_name or file_name == " " or not file_name.endswith("txt"):
        print("Invalid file name, must contain characters and end with .txt .")
        return False

    date_year, date_month, date_day = date.split("-")
    try:
        date_dt = dt.datetime(year=int(date_year), month=int(date_month), day=int(date_day))
    except ValueError:
        print("Invalid date, use correct values for year, month, day")
        return False

    if date_dt > dt.datetime.today():
        print("Date must not be after today.")
        return False

    # Sets up request parameters
    mars_endpoint = "https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos"
    params = {
        "earth_date": date,
        "api_key": API_KEY
    }

    print("Getting API response...")
    # Gets API response
    api_response = requests.get(mars_endpoint, params, timeout=TIMEOUT)
    rover_images = api_response.json()

    try:
        photos = rover_images["photos"]
    except KeyError:
        print("Invalid date/API key.")
        return False

    images = []
    print(f"Saving urls to {file_name}...")
    # Writes url to file
    with open(file_name, "w", encoding="utf-8") as file:
        for photo in photos:
            image_url = photo['img_src']
            file.write(f"{image_url}\n")

            images.append(image_url)

    print(f"Saved urls to {file_name}.")

    # Gets image if images were found
    try:
        file_extension = os.path.splitext(images[0])[-1].lower()
    except IndexError:
        sys.exit()

    print("Saving first image...")
    # Gets image and saves it
    file_name = f"mars{file_extension}"
    image = requests.get(image_url, timeout=TIMEOUT)

    with open(file_name, 'wb', encoding=None) as file:
        file.write(image.content)

    print(f"Image saved as {file_name}.")
    return api_response.status_code


if __name__ == "__main__":
    main()
