# speculum

`speculum` is an Arch Linux mirror list filtering and sorting tool, not unlike `reflector`.

It downloads the public Arch Linux mirror-status data, filters and orders the
available mirrors, and writes pacman's `Server = …` entries.  It does not test
mirror download speed itself.

## Requirements and installation

`speculum` requires Python 3.8 or newer and network access to the Arch Linux
mirror-status service.  Install it from a checkout with:

```console
$ python -m pip install .
```

This installs the `speculum` command.  See the command-line reference with:

```console
$ speculum --help
```

## Basic use

Running `speculum` prints a pacman mirrorlist to standard output.  Redirect it
to a temporary file first so that you can inspect the result before replacing
your active mirrorlist:

```console
$ speculum --countries de at ch --protocols https --complete --active \
    --sort score --limit 10 --header > /tmp/mirrorlist
$ less /tmp/mirrorlist
$ sudo install -m 644 /tmp/mirrorlist /etc/pacman.d/mirrorlist
```

All selected filters must match.  For example, the command above selects active,
fully synced HTTPS mirrors in Germany, Austria, or Switzerland, sorts them by
their reported `score`, and keeps the first ten.  Country names and ISO country
codes are accepted case-insensitively.

Use `--output FILE` when the result has already been reviewed or the destination
is intentional:

```console
$ sudo speculum --countries de --protocols https --complete --active \
    --sort score --limit 10 --output /etc/pacman.d/mirrorlist
```

`--output` overwrites the target file.  If the command finds no mirrors, it
exits with status 1 and does not write a mirrorlist.

## Selecting and ordering mirrors

The most useful options are:

| Option | Meaning |
| --- | --- |
| `-c`, `--countries COUNTRY …` | Keep mirrors in one or more countries (name or code). |
| `-p`, `--protocols PROTOCOL …` | Keep mirrors using listed protocols, such as `https`. |
| `-a`, `--max-age HOURS` | Keep mirrors whose last sync is no older than the given number of hours. |
| `-m`, `--match REGEX` | Keep mirror URLs matching a Python regular expression. |
| `-n`, `--nomatch REGEX` | Exclude mirror URLs matching a regular expression. |
| `-t`, `--complete` | Keep only completely synchronized mirrors. |
| `-u`, `--active` | Keep only active mirrors. |
| `-4`, `--ipv4`; `-6`, `--ipv6`; `-i`, `--isos` | Require IPv4, IPv6, or ISO support. |
| `-s`, `--sort OPTION …` | Sort by one or more fields, in priority order. |
| `-r`, `--reverse` | Reverse the selected sort order (and country/sort-option listings). |
| `-l`, `--limit N` | Emit at most `N` mirrors; `N` must be greater than zero. |
| `-H`, `--header` | Add generation time and effective configuration as comments. |

List the country values currently reported by Arch with `speculum --list-countries`.
List valid sort fields with `speculum --list-sortopts`; these currently include
`score`, `delay`, `duration_avg`, `duration_stddev`, `last_sync`, `completion_pct`,
`country`, `country_code`, `protocol`, and `url`.  Lower reported scores are
normally preferable, so `--sort score` is a sensible starting point.

## Configuration file

The same settings can be stored in an INI file and loaded with `--config FILE`.
[`files/speculum.conf`](files/speculum.conf) is a ready-to-copy example:

```ini
[sorting]
sort = score

[filtering]
countries = de, at, ch
protocols = https
max_age = 12
complete = true
active = true

[output]
limit = 10
header = true
file = /etc/pacman.d/mirrorlist
```

Comma-separated and whitespace-separated country, protocol, and sort values
are supported.  Command-line values take precedence when they are provided.
For example, use a conservative scheduled configuration in `/etc/speculum.conf`
and override its limit for a one-off run:

```console
$ sudo speculum --config /etc/speculum.conf --limit 20
```

The `file` setting, like `--output`, overwrites its destination.  Omit it to
print the generated list instead.

## Scheduled updates with systemd

The repository includes a oneshot service and weekly timer.  After installing
the command, install and review the example configuration before enabling them:

```console
$ sudo install -Dm644 files/speculum.conf /etc/speculum.conf
$ sudoedit /etc/speculum.conf
$ sudo install -Dm644 files/speculum.service /etc/systemd/system/speculum.service
$ sudo install -Dm644 files/speculum.timer /etc/systemd/system/speculum.timer
$ sudo systemctl daemon-reload
$ sudo systemctl enable --now speculum.timer
```

The supplied timer runs weekly, persists missed runs, and adds a random delay of
up to 12 hours.  Test the exact configuration once before relying on the timer:

```console
$ sudo systemctl start speculum.service
$ systemctl status speculum.service
```
