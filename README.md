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

<pre><code><span style="color: green; font-style: italic;">-- Comments start with `--`.</span>

<span style="color: green; font-style: italic;">-- Completed events.</span>
<span style="font-weight: bold;">podcast</span> @inner_french e147 00:00/45:00
19:00/19:30 <span style="font-weight: bold;">run</span> 5.2km

<span style="color: green; font-style: italic;">-- Tasks (prefixed with [ ] or [x]).</span>
[x] <b>do</b> the dishes
[ ] <b>clean</b> @bathroom

<span style="color: green; font-style: italic;">-- Future events (prefixed with >>>).</span>
>>> 20:00/ concert @radiohead
</code></pre>

### Objects

Define reusable objects to simplify your entries:

<pre><code><b>podcast</b> @innerfrench = Inner French Podcast .fr
<b>book</b> @dune = Dune by Frank Herbert</code></pre>

### Special Commands

Date entries help organize your journal chronologically:

<pre><code>2024-01-01 <span style="color: green; font-style: italic;">-- Sets the current date.</span>
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
