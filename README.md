# Chronicle

> A minimalist command-line journaling system for tracking daily activities,
metrics, and insights.

Chronicle is a lightweight tool that helps you systematically log and analyze
your daily life using simple, human-readable text files. It emphasizes privacy
by storing all data locally while maintaining flexibility in how you record and
review your information.

## Features

- Chronicle uses a **simple text format**: you can use any text editor with our `.chr`
file format.
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

<pre><code><span style="color: green;"><i>-- Comments start with `--`.</i></span>

<span style="color: green;"><i>-- Completed events.</i></span>
<b>podcast</b> @<u>inner_french</u> e147 00:00/45:00
19:00/19:30 <b>run</b> 5.2km

<span style="color: green;"><i>-- Tasks (prefixed with [ ] or [x]).</i></span>
[x] <b>do</b> <i>the dishes</i>
[ ] <b>clean</b> @<u>bathroom</u>

<span style="color: green;"><i>-- Future events (prefixed with >>>).</i></span>
>>> 20:00/ <b>concert</b> @<u>radiohead</u></code></pre>

### Objects

Define reusable objects to simplify your entries:

<pre><code><b>podcast</b> @<u>innerfrench</u> = <i>Inner French Podcast</i> .fr
<b>book</b> @<u>dune</u> = <i>Dune</i> by <i>Frank Herbert</i></code></pre>

### Special Commands

Date entries help organize your journal chronologically:

<pre><code><b>2024-01-01</b> <span style="color: green;"><i>-- Sets the current date.</i></span>
</code></pre>

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

## NeoVim Integration

Chronicle provides a Lua script (`scripts/chronicle.lua`) for NeoVim to help
manage tasks directly within your `.chr` files. This script adds convenient
commands and key mappings for working with tasks in your journal.

### Available NeoVim Commands

- `:ChronicleDone` or <kbd>Space</kbd> <kbd>d</kbd>
  - Marks the current task as done (completes the task under the cursor).
  - Changes the event end time to the current time.
  - If the task is recurring (e.g., contains `!every_day`), it will
    automatically schedule the next occurrence on the appropriate date.
  
- `:ChronicleStart` or <kbd>Space</kbd> <kbd>s</kbd>
  - Changes the event start time to the current time.
  
These commands are available after sourcing the script in NeoVim:

```vim
:source <path to Chronicle>/scripts/chronicle.lua
```

Or, if you have the script in your runtime path, it will be loaded
automatically.

### Example Usage

1. Place your cursor on a task line in a `.chr` file.
2. Press <kbd>Space</kbd> <kbd>d</kbd> to mark it as done, or
   <kbd>Space</kbd> <kbd>s</kbd> to start the task.
3. If the task is recurring, the script will automatically insert the next
   occurrence on the correct date.
