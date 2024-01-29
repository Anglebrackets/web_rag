****Web RAG -- Retrieval-Augmented Generation from Web content****

***An extension for Oobabooga's Text-Generation Web UI***
* This extension requires that the 'links' browser be installed on your machine
* I have only tested on Linux. I'm open to PRs to make the links integration work on other platforms


There are two kinds of retrieval: Manual and Auto.

Manual
  * You: get http://wikipedia.com/wiki/Charles_Martel
  * AI: Retrieved 5000 characters. Total is 5000.
  * You: get https://wikipedia.com/wiki/Charlemagne
  * AI: Retrieved 5000 characters. Total is 10000.
  * You: Did Charlemagne fulfill the destiny of his grandfather?

Auto -- pass prompt to a search engine, insert result into context, then process prompt
    - there are fields in the UI to set the keyword, url, etc. The prompt is url-encoded and inserted into the url
  * You: when will the super bowl be played?
  * AI: This year's Super Bowl LVII is scheduled to take place on February 12, 2023.
  * You: web, when will the super bowl be played?
  * [ query encoded as: when+will+the+super+bowl+be+played%3F and sent to search engine ]
  * [ prompt becomes "when will the super bowl be played?"]
  * AI: The Super Bowl 58 is scheduled for Sunday, February 11, 2024.


Notes
  * These examples were run using neuralhermes-2.5-mistral-7b.Q5_K_M.gguf
  * This extension only works on web pages that do not require javascript
  * Retrieved data is kept until the 'Clear Data' button is pressed
  * You can edit the data using the 'Show Data' button

