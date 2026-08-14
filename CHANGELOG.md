# Changelog

## [0.2.0](https://github.com/iloveitaly/lunchmoney-transaction-enhancer/compare/v0.1.0...v0.2.0) (2026-08-14)


### Features

* add cronfile and railpack configuration for scheduled tasks ([5fde480](https://github.com/iloveitaly/lunchmoney-transaction-enhancer/commit/5fde480f21d7107becc05deedf220529abdb1b4c))
* add extraction rules for Capital One Travel transactions ([e278352](https://github.com/iloveitaly/lunchmoney-transaction-enhancer/commit/e278352102d7cf540fd3f85b90370ed0e6a5ff82))
* **cli:** allow --lookback to override persisted state ([62ce0be](https://github.com/iloveitaly/lunchmoney-transaction-enhancer/commit/62ce0bec7e6d1d62dc4fdcb960a157c08a58b2b8))
* **config:** add extraction rules for Alliant interest and Wise transfers ([4d76545](https://github.com/iloveitaly/lunchmoney-transaction-enhancer/commit/4d76545546e935af748e58c50582079e08a837d6))


### Documentation

* document supported services and note preservation behavior ([b6a3544](https://github.com/iloveitaly/lunchmoney-transaction-enhancer/commit/b6a3544dcfc375e10cc15ac5b2cdea1492949b33))

## 0.1.0 (2026-08-14)


### Features

* add cli, config, enhancer, state and cron automation ([4bb7f12](https://github.com/iloveitaly/lunchmoney-transaction-enhancer/commit/4bb7f12919fb7566ba33eb9dcb468642fd4327a8))
* add dry-run mode to prevent modifications ([d4ebd69](https://github.com/iloveitaly/lunchmoney-transaction-enhancer/commit/d4ebd6993c40d77422314ab5c63e5baf660f7ba2))
* enhance transaction enrichment rules and configuration ([a00dafd](https://github.com/iloveitaly/lunchmoney-transaction-enhancer/commit/a00dafdf5ce4ed35904e623c0c55de736bbcc9b7))
* persist state in data/, improve date handling, add tests ([05d56fb](https://github.com/iloveitaly/lunchmoney-transaction-enhancer/commit/05d56fb0955924639bdb987a39796aa62d28835d))


### Bug Fixes

* **enhancer:** prevent overwriting existing transaction notes ([fa87b9f](https://github.com/iloveitaly/lunchmoney-transaction-enhancer/commit/fa87b9f8938e2593da3a1dc68979401909415d6c))
* handle same-day transaction date ranges for api fetch ([c0cada6](https://github.com/iloveitaly/lunchmoney-transaction-enhancer/commit/c0cada69dbcd34738937a39886212ddaf3b4a06e))
* resolve ruff 0.16 lint failures ([#49](https://github.com/iloveitaly/lunchmoney-transaction-enhancer/issues/49)) ([da67128](https://github.com/iloveitaly/lunchmoney-transaction-enhancer/commit/da67128ab2d6101f79480d8e84957128f2253d2d))


### Documentation

* update installation and usage instructions to use uvx ([bbccdb2](https://github.com/iloveitaly/lunchmoney-transaction-enhancer/commit/bbccdb278b32f12515be20c6c1fe45e331ac9f1e))
* update project description and readme documentation ([4c818d8](https://github.com/iloveitaly/lunchmoney-transaction-enhancer/commit/4c818d8d4af6ad9be3138f5da03a67f7619f391a))
