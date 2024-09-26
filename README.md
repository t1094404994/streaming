1. Start the Python Server
Open a terminal and run:

bash
Copy code
python server.py
The server will start and wait for client connections.

2. Serve the HTML Page
To run the JavaScript client, you need to serve index.html over HTTP (not opening it directly from the file system).

Option A: Use Python's SimpleHTTPServer (Python 2)
bash
Copy code
python -m SimpleHTTPServer 8000
Option B: Use Python's http.server (Python 3)
bash
Copy code
python -m http.server 8000
This will serve files in the current directory at http://localhost:8000.

3. Open the Web Page
Open your web browser and navigate to:

bash
Copy code
http://localhost:8000/index.html
The page should load, and the video stream should appear in the <img> element.

