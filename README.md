# Chronicle

A pretty simple command-line journalling tool for systematically logging and
analyzing daily life events, activities, and metrics.

Chronicle provides a simple, flexible human-readable plain text format for files
that may be privately stored locally and edited by any preferred text editor.

Chronicle allows you to
  - track events: exercises, meals, work, learning,
  - track metrics: sleep, body metrics, productivity,
  - track tasks,
  - generate insights and summaries.

# Data format

All data is written to text files with `.chr` extension.

Types of data:
  - events or tasks,
  - objects,
  - special commands.

## Events or tasks

In Chronicle, tasks are treated as planned future events.

Examples:
  - `podcast @inner_french e147 00:00/45:00`,
  - `19:00/19:30 run 5.2km`,
  - `--- clean @bathroom`.
  - `>>> 20:00/ concert @radiohead`.

## Objects

Examples:

  - `podcast @innerfrench = Inner French Podcast .fr`

## Special commands

  - Date setter. E.g. `2024-01-01`: set current date to 1 January 2024.

# Run

## Installation
