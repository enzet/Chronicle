# Chronicle

> A minimalist command-line journaling system for tracking daily activities,
metrics, and insights.

Chronicle is a lightweight tool that helps you systematically log and analyze
your daily life using simple, human-readable text files. It emphasizes privacy
by storing all data locally while maintaining flexibility in how you record and
review your information.

## Features

  - Chronicle uses a **simple text format**: you can use any text editor with
    our `.chr` file format.
  - It is **privacy-first**: all data stored locally on your machine.
  - You can **track multiple metrics**:
      - daily activities and events,
      - health and fitness metrics,
      - tasks and goals,
      - sleep patterns,
      - custom metrics.
  - Chronicle allows you to **generate insights**: analyze patterns and create
    summaries.
  - `.chr` files have a **flexible syntax**: intuitive format for quick entries.

## Data Format

Chronicle uses plain text files with the `.chr` extension. The syntax is
designed to be both human-readable and machine-parseable.

Each line in the file is a separate record, that can be an event (or a task),
an object definition, a special command, or a comment.

### Events and Tasks

Events are activities that have occurred, while tasks are planned future events.

<pre><code><i style="color: green;">-- Comments start with `--`.</i>

<i style="color: green;">-- Completed events.</i>
<b>podcast</b> @<u>inner_french</u> e147 00:00/45:00
19:00/19:30 <b>run</b> 5.2km

<i style="color: green;">-- Tasks (prefixed with [ ] or [x]).</i>
[x] <b>do</b> <i>the dishes</i>
[ ] <b>clean</b> @<u>bathroom</u>

<i style="color: green;">-- Future events (prefixed with >>>).</i>
>>> 20:00/ <b>concert</b> @<u>radiohead</u></code></pre>

### Objects

Define reusable objects to simplify your entries:

<pre><code><b>podcast</b> @<u>innerfrench</u> = <i>Inner French Podcast</i> .fr
<b>book</b> @<u>dune</u> = <i>Dune</i> by <i>Frank Herbert</i></code></pre>

### Special Commands

Date entries help organize your journal chronologically:

<pre><code><b>2024-01-01</b> <i style="color: green;">-- Sets the current date.</i>
</code></pre>

## Example

### Chronicle file

<pre><code><b>book</b> @<u>dune</u> = <i>Dune</i> by <i>Frank Herbert</i> .en /fiction 896p
<b>podcast</b> @<u>inner_french</u> = <i>Inner French Podcast</i> .fr

<b>2000-01-01</b>

00:00/08:00 <b>sleep</b>
09:00/09:30 <b>run</b> 5.2km

<b>read</b> @<u>dune</u> 120/140p
<b>podcast</b> @<u>inner_french</u> e50 45:00

>>> 20:00/ <b>concert</b> <i>Radiohead</i>

[x] <b>buy</b> <i>milk</i>
[ ] <b>pay</b> for <i>internet</i> 15usd
</code></pre>

### Text representation

Objects:
  - Book _Dune_ by Frank Herbert, 896 pages, in English, fiction.
  - Podcast _Inner French Podcast_ in French.

1 January 2000.
  - Events:
    - 00:00—08:00 Sleep.
    - 09:00—09:30 Run 5.2 km.
    - Read _Dune_ from page 120 to 140.
    - Listen to _Inner French Podcast_ episode 50 for 45 minutes.
  - Planned:
    - 20:00 Concert _Radiohead_.
  - Tasks:
    - [x] Buy milk.
    - [ ] Pay for internet $15.

## Commands

### `view` — Visualize data

```shell
chronicle --input <files> view [--style <style>] [--colors light|dark|no] <subcommand>
```

#### `view language` — Language learning statistics

```shell
chronicle --input <files> view language \
    [--form table|plot] \
    [--file <output file>] \
    [--period day|week|month|year] \
    [--smooth <days>] \
    [--interval <days>] \
    [--plot-type fill|stack|bar|percent] \
    [--margin <hours>] \
    [--exclude-languages <lang> ...] \
    [--services <service> ...] \
    [--cumulative]
```

#### `view travel` — Travel map

```shell
chronicle --input <files> view travel [--svg-output <file>]
```

#### `view books` — Book list

```shell
chronicle --input <files> view books [--year <year>] [--title <title>] [--finished]
```

#### `view podcasts` — Podcast list

```shell
chronicle --input <files> view podcasts [--title <title>]
```

#### `view sport` — Sport activity plot

```shell
chronicle --input <files> view sport
```

#### `view objects` — Object list as HTML

```shell
chronicle --input <files> view objects
```

### Other commands

| Command | Description |
|---|---|
| `timeline` | Print the full timeline. |
| `summary` | Print a summary of all events. |
| `shows` | Show TV show progress. |
| `movies` | List watched movies. |
| `expired` | Show expired tasks. |
| `dishes` | Show dishes log. |
| `objects` | List all objects. |
| `graph` | Build an object graph. |
| `interpret` | Interactive mode: read commands from stdin. |

## Requirements

- Python 3.12+.

## Installation

```shell
pip install .
```

## Usage

For the most detailed help, run:

```shell
chronicle --help
```

Common usage:

```shell
chronicle \
    --input <input Chronicle files> \
    <import options> \
    <command>
```

Example:

```shell
chronicle \
    --input timeline.chr \
    --import-wikimedia User1@en.wikipedia.org User2@wikidata.org \
    --import-memrise memrise.html \
    view language --form table
```

### Importing Data

- `--import-memrise`: exported Memrise `.html` files. File can be requested at
  [Memrise settings](https://app.memrise.com/settings/) by "Download Personal
  Data" button.
- `--import-duome`: exported Duome `.txt` files.
- `--import-wikimedia`: import contributions from Wikimedia projects.
  Argument format is `<username>@<url>`, e.g. `User1@en.wikipedia.org`
  or `User2@wikidata.org`.

## Vim Syntax Highlighting

Chronicle can generate a Vim syntax file for `.chr` files that highlights event
types, object definitions, timestamps, tags, languages, and other values.

### How it works

Every time `chronicle` runs it writes a generated syntax file to
`syntax/chronicle.vim` in the repository and, if `~/.vim/syntax/` exists, also
to `~/.vim/syntax/chronicle.vim`. The generated file is built from the static
header `syntax/chronicle_header.vim` with auto-generated rules for every known
event and object type appended.

### Setup

1. Associate the `.chr` extension with the `chronicle` filetype. Add this line
   to your `~/.vimrc` or `~/.config/nvim/init.vim`:

   ```vim
   au BufRead,BufNewFile *.chr set filetype=chronicle
   ```

2. Copy the pre-generated syntax file into your Vim syntax directory:

   ```shell
   cp syntax/chronicle.vim ~/.vim/syntax/chronicle.vim
   ```

   After that, re-running `chronicle` will keep `~/.vim/syntax/chronicle.vim`
   up to date automatically.

### What is highlighted

| Element | Examples |
|---|---|
| Event and object types | `sleep`, `run`, `book`, `podcast` |
| Timestamps and dates | `2024-01-01`, `09:00/09:30` |
| Object references | `@inner_french` |
| Languages | `.fr`, `.en` |
| Tags | `!work`, `!every_day` |
| Subjects | `/fiction`, `/language/de` |
| Intervals and durations | `10:00/45:00`, `1:52:00` |
| Season and episode numbers | `s2`, `e15` |
| URLs | `https://...` |
| Comments | `-- ...` |
| Task markers | `[ ]`, `[x]` |

## Neovim Integration

Chronicle provides a Lua script (`scripts/chronicle.lua`) for Neovim to help
manage tasks directly within your `.chr` files. This script adds convenient
commands and key mappings for working with tasks in your journal.

### Available Neovim Task Commands

- `:ChronicleStart` or <kbd>Space</kbd> <kbd>s</kbd>
  - Changes the event start time to the current time.

- `:ChronicleDone` or <kbd>Space</kbd> <kbd>d</kbd>
  - Marks the current task as done (completes the task under the cursor).
  - Changes the event end time to the current time.
  - If the task is recurring (e.g., contains `!every_day`), it will
    automatically schedule the next occurrence on the appropriate date.

- `:ChroniclePause` or <kbd>Space</kbd> <kbd>p</kbd>
  - Marks the current task as done and creates a new identical task.

These commands are available after sourcing the script in Neovim:

```vim
:source <path to Chronicle>/scripts/chronicle.lua
```

### Example Usage

1. Place your cursor on a task line in a `.chr` file.
2. Press <kbd>Space</kbd> <kbd>d</kbd> to mark it as done, or
   <kbd>Space</kbd> <kbd>s</kbd> to start the task.
3. If the task is recurring, the script will automatically insert the next
   occurrence on the correct date.
