# shsearch
Search the 1991 Sacred Harp for things you remember when you've forgotten the words.


# Installation

For installation, the backend requires Python 3.8, a current version of Pip, SQLite, and an internet connection. 
The installation commands will download the remaining dependencies, 

Clone the repository.
```
git clone https://github.com/leahvelleman/shsearch/
```

Inside the new directory, set up and activate a virtual environment.
```
cd shsearch
python -m venv --prompt shsearch env
source env/bin/activate
```

Then, install the project dependencies inside it.
```
pip install -r requirements.txt
```

# Usage

`flask run` starts the server running on `http://127.0.0.1:5000/`. 
