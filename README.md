# seq2view

Browser-based visualization of data.

## Architecture

This project utilizes a server-client archicture. The server provides data in JSON format and is implemented using Python and Flask. The client provides the browser-based visualization and fetches data from the server. VueJS, D3, and Axios help make this happen.

## Installation

1. Clone this repository
1. Install server components (instructions use virtual environment)
    - Create virtual environment and install dependencies:
        ```
        cd server
        python -m venv venv
        ./venv/bin/python -m pip install \
            --no-cache-dir -r requirements.txt
        ```
1. Install client components
    ```
    cd client
    npm install
    ```

## Usage

Instructions below are for development purposes only. **Not for production**.

1. Run development server
    ```
    cd server
    FLASK_APP=server.py FLASK_ENV=development \
        ./venv/bin/flask run
    ```
1. Run client
    ```
    cd client
    npm run serve
    ```

Open browser to http://localhost:8080/
