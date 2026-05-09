Read the file `config/system.yaml` to get `loop_interval_hours`.

Then use CronCreate to schedule a recurring task with these exact settings:
- command: `python src/orchestrator.py`
- schedule: every {loop_interval_hours} hours (convert to a cron expression)
- working directory: the current project root (D:\autonomous-mind)
- description: "autonomous-mind cycle runner"

After creating the cron job, immediately run one cycle now by executing:
```
python src/orchestrator.py
```

Report: the cron job ID, the next scheduled run time, and a summary of what the first cycle produced.
