# Engine (pinned copy)

`sfe/` is a pinned copy of the Safety Framework Engine, whose home is the CSEF repository
([engine/](https://github.com/eduardon83/child-safe-edtech-framework/tree/main/engine)). `ENGINE.lock` records the
CSEF commit it was copied from. Do not edit `sfe/` here: change it in CSEF, then run

```bash
python3 tooling/sync_engine.py --from ../child-safe-edtech-framework
```

CI checks that the copy matches the locked commit.
