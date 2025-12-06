# sonia
## . simple capture .

`sonia` is a command-line application designed to help you capture, organize, and manage your notes and thoughts without leaving the terminal. It combines `duckdb` for robust local storage and `rich` for beautiful, readable output.

---

## Features

* **Fast Capture**: Add single or multiple notes quickly.
* **Search**: Full-text search to find keywords across your history.
* **Time-Stamped**: All notes are automatically timestamped.
* **Persistent**: Data is stored locally in a high-performance `DuckDB` file.
* **Beautiful Output**: Formatted tables and colors via `Rich`.

## Installation

### Option 1: From a clone (recommended)
Install from a local checkout so you can run `sonia` from anywhere:

```bash
pipx install .
# OR
pip install .
# OR
uv tool install .
```

### Option 2: For Developers

If you want to contribute or modify the source code, this project uses `uv` for dependency management.

1.  **Clone the repository:**

    ```bash
    git clone [https://github.com/usefulmove/sonia.git](https://github.com/usefulmove/sonia.git)
    cd sonia
    ```

2.  **Install dependencies:**

    ```bash
    uv sync
    ```

3.  **Run locally:**

    ```bash
    python -m sonia list
    ```

## Usage

Once installed, use the `sonia` command.


**Add Notes**
Add one note or multiple notes at once.

```bash
sonia add "buy milk" "call the mechanic about the car"
```

**List Notes**
View your history with IDs and timestamps.

```bash
sonia list
```

**Search**
Find notes containing specific text.

```bash
sonia search "mechanic"
```

**Remove**
Delete a note using its ID (found via `list`).

```bash
sonia remove 1
```

**Clear All**
*Warning: This permanently deletes all data.*

```bash
sonia clear
```

## Technologies

  * **[DuckDB](https://duckdb.org/)**: Local SQL OLAP database.
  * **[Rich](https://rich.readthedocs.io/en/stable/)**: Terminal formatting.
  * **[uv](https://github.com/astral-sh/uv)**: Python package and project manager.

## Contributing

Contributions are welcome\! Please feel free to submit a Pull Request.

1.  Fork the project.
2.  Create your feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

## License

Distributed under the MIT License. See `LICENSE` for more information.
