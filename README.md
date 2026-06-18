# HelioResearch

This project is dedicated to the study of solar oscillations using **SunPy** and **ds9**. The analyzed data originates from the SDO (Solar Dynamics Observatory) satellite.

## Project Structure

```text
├── notebooks/          # Jupyter Notebooks for exploratory data analysis
├── src/                # Python scripts
│   ├── utils/          # Reusable functions and tools
│   └── dev/            # Scripts currently under development
├── .gitignore          # Configuration to exclude data and environments
├── requirements.txt    # Project dependencies
└── README.md
```

## Requirements

Since this project is primarily based on [SunPy](https://docs.sunpy.org/en/stable/tutorial/installation.html), we recommend using **Python 3.11** for optimal performance. It is also strongly recommended to work within a virtual environment (such as Conda, venv or the environment provided by `SunPy`). 

## Installation

1. ***Clone this repository:*** It is recommended to clone both repositories in the same parent folder to ensure the relative paths are correct:

```Bash
git clone https://github.com/FlppeG/HelioResearch
git clone https://github.com/AngelDMartinezC/sunpython.git
   cd helioresearch
```

If done right, the folder structure should look like this:

```text
Parent_folder/
├── helioresearch/
└── sunpython/
```


2. ***Create and activate a virtual environment:*** You can either use a custom environment or the one provided by `SunPy`. For the first option:

```Bash
# On Windows:
   python -m venv venv
   .\venv\Scripts\activate

# On Mac/Linux:
   python -m venv venv
   source venv/bin/activate
```

For the second option use

```Bash
conda create -n helio-env python=3.11
conda activate helio-env
```

3. ***Install the dependencies:*** Install all the required libraries at once. This command will automatically install the necessary packages and set up `sunpython` in editable mode:

```Bash
pip install -r requirements.txt
```

## Data management

The data for analysis consists of **FITS** (Flexible Image Transport System). These can be obtainded from the [JSOC Website](http://jsoc.stanford.edu/ajax/lookdata.html) or by using the `Fido.search` utility included in the `src/` directory.
