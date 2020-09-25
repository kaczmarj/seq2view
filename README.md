# seq2view

Browser-based visualization of data.

## Installation

1. Clone this repository
1. Install server dependencies (recommended to use a virtual environment)
    ```
    cd server
    python -m venv venv
    ./venv/bin/python -m pip install --no-cache-dir -U pip
    ./venv/bin/python -m pip install --no-cache-dir -r requirements.txt
    ```
1. Install client dependencies
    ```
    cd client
    npm install
    ```

## Usage

Instructions below are for development purposes only. **Not for production**.

1. Run development server in one terminal
    ```
    FLASK_APP=server/server.py FLASK_ENV=development PYTHONDONTWRITEBYTECODE=1 \
        ./server/venv/bin/flask run
    ```
1. Run client in another terminal
    ```
    npm run --prefix=client serve
    ```

Open browser to http://localhost:8080/

## Architecture

This project utilizes a server-client archicture. The server provides data in JSON format and is implemented using Python, Flask, H5py, and NumPy. The client provides the browser-based visualization and fetches data from the server. VueJS, D3, and Axios help make this happen.
