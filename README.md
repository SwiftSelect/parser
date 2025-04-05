# parser

- The branch consists of old code and new code as well.
- The new code with kafka implementation is in the folder 'main-application'.
- Kafka is implemented via docker, so you need to set up the container first.
- Run 'docker-compose up -d' to run in detached mode.
- To run the app.py, simply run 'python app.py'.
- The code is tested for PDF's as of now.
- There are snippets and functions which were commented out while testing. They will be deleted later.

Results:
- When you run the app.py file, kafka producer and consumer will run and you need to use Postman to check the working.
- Use the POST method and under Body section, upload your file and hit 'send'.
- Within 10 seconds, you will get the data in JSON format and the response status is 200.
