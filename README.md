scrum-cards-gen
===============
Scrum cards generator based in csv files.

usage
-----

Make sure you have python and pip installed and then, install the dependencies:

    pip install -r requirements.txt

Then run the main.py to create an empty sheet of cards:

    python main.py -e empty-cards.pdf

To create cards for a CSV run:

    python main.py -i input-file.csv cards.pdf
