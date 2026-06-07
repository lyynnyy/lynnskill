# Cleanup Status Taxonomy

Use these status labels consistently in task lists and search indexes.

## Task Status

- `已清理释放空间`: files, models, caches, or folders are no longer occupying local disk space.
- `已整理待备份/外移`: files have been consolidated locally but still occupy local disk space.
- `待清理`: safe or likely-safe cleanup candidate, not yet executed.
- `待确认`: needs user judgment before delete, move, or archive.
- `不建议手动清理`: should be handled through the owning app or system tool.

## File Index Status

- `已归档_本机`: file was moved into a local archive folder and current path exists.
- `已归档_本机副本已清理或外移`: file was archived locally earlier, but current archive path is now missing.
- `已归档_本机副本已清理_用户确认`: same as above, with explicit user confirmation that cleanup is complete.
- `已归档_历史整理`: file was handled by an older cleanup manifest.
- `已删除_模型`: local model was deleted; it must be downloaded again if needed.
- `已删除_Office临时锁文件`: Office `~$` temporary lock file was deleted.
- `已删除_保留副本`: duplicate was deleted and current path points to the kept copy.
- `已删除_保留副本当前未找到`: duplicate was deleted, but the kept-copy path from historical records is also missing.
- `已清理或外移_第一轮大文件记录`: first-round scan saw the file, but a later check cannot find it.

## Evidence Rules

Each status should include at least one of:

- manifest path;
- scan CSV/report path;
- command output summary;
- user confirmation;
- current path existence check;
- size/count verification.
