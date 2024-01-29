****Web RAG -- Retrieval-Augmented Generation from Web content****

***An extension for Oobabooga's Text-Generation Web UI***
* This extension requires that the 'links' browser be installed on your machine
* I have only tested on Linux. I'm open to PRs to make the links integration work on other platforms


There are two kinds of retrieval: Manual and Auto.

Manual
 * You: get https://www.sciencedaily.com/releases/2024/01/240123175550.htm
 * AI: Retrieved 5000 characters. Total is 5000.
 * You: How does gravity help study the strong force?
 * AI: Gravity helps study the strong force by connecting theories of gravitation to interactions among the smallest particles of matter, as demonstrated in recent research conducted by nuclear physicists at the U.S. Department of Energy's Thomas Jefferson National Accelerator Facility. This approach allows scientists to gain insights into the environment experienced by proton's building blocks (quarks) and reveal new details about the strong force inside the proton, such as its shear stress distribution. By observing how gravity interacts with subatomic particles like the proton, researchers can indirectly study the properties of the strong force in a unique way that was previously thought to be unattainable due to the vast difference between gravitational and electromagnetic forces.
 * You: How strong is the strong force?
 * AI: The research mentioned reveals that at its peak, a force of over four metric tons would be required to overcome the binding power of the strong force inside the proton. This highlights the immense strength of the strong force in holding quark particles together within the proton.
 - 
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

