# Logging and Observability

Umboni logs in JSON lines so the same log stream is easy to read in plain text, grep, Loki, or any downstream log system.

## Log files

- Python fetcher logs default to `artifacts/logs/python-fetcher.log.jsonl`
- Fortran engine logs default to `artifacts/logs/fortran-simulator.log.jsonl`

## Why JSON lines

JSON lines are useful because:

- Each line is self-contained.
- Tools like Loki and jq can parse them easily.
- They are still readable in a normal text editor.

## Local observability stack

The repository includes a ready-to-run Grafana, Loki, and Promtail stack in [`observability/docker-compose.yml`](https://github.com/gedrocht/Umboni/blob/main/observability/docker-compose.yml).

### Example command

```bash
docker compose -f observability/docker-compose.yml up -d
```

### What you get

- Promtail tails the JSON-line log files.
- Loki stores those log lines.
- Grafana gives you a visual query interface.
