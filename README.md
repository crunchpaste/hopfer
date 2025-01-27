![hopfer](thumbnail.svg)

# hopfer

**hopfer** is a Python-based GUI application that implements a wide range of halftoning algorithms from scratch, primarily designed for printmaking purposes.

The application uses Qt6 for the GUI and implements the halftoning algorithms using NumPy and Numba for much better performance.

This project was originally created as a companion to my PhD thesis on digital halftoning methods for analog printmaking techniques.

## Requirements

Not sure yet.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/crunchpaste/hopfer
```

### 2. Navigate to the project directory

```bash
cd hopfer
```

### 3. Install the dependencies

```bash
pip install -r requirements.txt
```

### 4. Run it

```bash
python src/hopfer.py
```

### Optional: Compile to a static binary

Despite depending on *numba* you can still compile **hopfer** to a single static binary using *nuitka*. To do so:

#### Compile all numba functions to a static binary

```bash
python src/algorithm_compiler.py
```

#### Install *nuitka*

```bash
pip install nuitka
```

#### Compile the whole project to a static binary.

```bash
nuitka --standalone --onefile --include-data-dir=res=res --nofollow-import-to=numba --enable-plugins=pyside6 src/hopfer.py
```




---

Enjoy halftoning!
