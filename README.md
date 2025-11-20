# **. simple note capture .**

`note` is a command-line application designed to help you capture, organize, and manage your notes without leaving the terminal. It combines `typer` for a smooth CLI experience, `duckdb` for robust local storage, and `rich` for beautiful, readable output.

---

## Features

* **Quick Capture**: Add single or multiple notes instantly.
* **Search**: Full-text search to find keywords across your history.
* **Time-Stamped**: All notes are automatically timestamped.
* **Persistent**: Data is stored locally in a high-performance `DuckDB` file.
* **Beautiful Output**: Formatted tables and colors via `Rich`.

## Installation

### Option 1: For Users (Recommended)
To install the tool globally so you can run `note` from anywhere:

```bash
# Using pipx (Recommended for CLI tools to avoid dependency conflicts)
pipx install git+[https://github.com/usefulmove/note.git](https://github.com/usefulmove/note.git)

# OR using pip
pip install git+[https://github.com/usefulmove/note.git](https://github.com/usefulmove/note.git)
````

### Option 2: For Developers

If you want to contribute or modify the source code, this project uses `uv` for dependency management.

1.  **Clone the repository:**

    ```bash
    git clone [https://github.com/usefulmove/note.git](https://github.com/usefulmove/note.git)
    cd note
    ```

2.  **Install dependencies:**

    ```bash
    uv sync
    ```

3.  **Run locally:**

    ```bash
    python -m note list
    ```

## Usage

Once installed, use the `note` command.

**Initialize (Optional)**
The database (`.notes.db`) is created automatically on your first add, but you can force it:

```bash
note init
```

**Add Notes**
Add one note or multiple notes at once.

```bash
note add "Buy milk" "Call the mechanic about the car"
```

**List Notes**
View your history with IDs and timestamps.

```bash
note list
```

**Search**
Find notes containing specific text.

```bash
note search "mechanic"
```

**Remove**
Delete a note using its ID (found via `list`).

```bash
note remove 1
```

**Clear All**
*Warning: This permanently deletes all data.*

```bash
note clear
```

## Technologies

  * **[Typer](https://typer.tiangolo.com/)**: CLI interface construction.
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
