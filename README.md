# Selenium Data Extraction and MongoDB Integration

This project uses **Selenium** to scrape data from a web page, processes the data, and stores it in a **MongoDB** database. Below are the details of the components and how to set them up.

## Prerequisites

- Python 3.7+
- Chrome WebDriver
- MongoDB
- `dotenv` package for managing environment variables
- `pymongo` package for interacting with MongoDB

## Setup

### Step 1: Install Required Packages

```bash
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables

Create a `.env` file in the root directory of your project and add the following environment variables:

```bash
CONNECTION_STRING=your_mongodb_connection_string
DATABASE=your_database_name
COLLECTION=your_collection_name
```

### Step 3: Download Chrome WebDriver

Download the Chrome WebDriver that matches your browser version from [here](https://sites.google.com/a/chromium.org/chromedriver/downloads), and place it in a known directory.

## Code Structure

The main functions of this script include:

- **get_main_link()**
    - Connects to the webpage using Selenium.
    - Extracts main links and other related information from the HTML table.
    - Saves the extracted data to `output.json`.

- **extract_sub_link(sub_links)**
    - Reads the sub-links from `output.json`.
    - Navigates through each link to scrape more detailed information.
    - Saves the final data to `db_json.json`.

- **delete_data_database()**
    - Deletes all documents from the specified MongoDB collection.

- **read_data_database()**
    - Reads and prints all documents from the MongoDB collection.

- **get_database_collection_database()**
    - Prints the names of databases and collections in MongoDB.
    - Displays the total number of documents in the specific collection.

- **insert_data_mongodb(json_data)**
    - Inserts the processed data into MongoDB from `db_json.json`.

## Running the Script

### Step 1: Execute the Script

Make sure the Chrome WebDriver is located correctly as specified in the `Service` object within the script:

```python
service = Service(executable_path=r"C:\chromedriver-win64\chromedriver.exe")
```

Run the script using Python:

```bash
python main.py
```

Follow the on-screen prompts to either delete existing data or continue with inserting new data.

### Step 2: Check MongoDB

After running the script, verify the inserted data using MongoDB Compass or any MongoDB client of your choice.

## Example Usage

Here is how you can use the utility functions individually:

```python
# Load sub-links from JSON and extract detailed data.
with open('output.json') as data:
    sub_links = json.load(data)
json_data = extract_sub_link(sub_links)

# Delete all existing data (if confirmed).
delete_data_database()

# Insert extracted data into MongoDB.
insert_data_mongodb(json_data)

# Read data from MongoDB.
read_data_database()

# Display database and collection details.
get_database_collection_database()
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.