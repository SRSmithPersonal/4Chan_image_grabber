A python script for searching 4Chan boards for threads that have a given term/ phrase in their OP, then downloads all images from the found threads.

This script uses the 4Chan API and impliments PyQT5 for its GUI

Use the dropdown menu to select the board to search for a topic, type
the search topic in the text box (currently not cap sensitive), then
press "Add" to add the search topic for the selected board to the scrape list.

Press "Start" to perform a single immediate scrape for all items listed in
the scrape list.

Press "Auto" to start an hourly scrape for all items listed in
the scrape list.

Press "Stop" to stop any currently ongoing scrape process.

Items in the scrape list can be selected and then removed by pressing the
"Delete" button.