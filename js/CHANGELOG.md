# [1.0.0](https://github.com/kitware/wslink/compare/v0.1.10...v1.0.0) (2021-08-09)


### Bug Fixes

* **dependencies:** Move json5 from devDependencies to dependencies ([bcb2919](https://github.com/kitware/wslink/commit/bcb2919a54074acd1c1f5bca11210a38381dcfce))
* **dependencies:** update webpack for security updates. ([27d6744](https://github.com/kitware/wslink/commit/27d674431546f106db8d5a4c67beb79c479acefa))
* **deps:** Replace twisted/autobahn with asyncio/aiohttp ([2e804bb](https://github.com/kitware/wslink/commit/2e804bbde98c75f03a6268067ffd322c954644c2))
* **ProcessLauncher:** Allow user to provide custom http headers ([e831509](https://github.com/kitware/wslink/commit/e831509c7766c5315be1b3baf7c1ecf37c900d4f))
* **publish:** use manager to allow publish to all connected clients ([83b94ab](https://github.com/kitware/wslink/commit/83b94ab715c332f5a589d8649fa8bd80e879fcab))
* **python:** Automatic version handling ([964db33](https://github.com/kitware/wslink/commit/964db33dd806dafae2e7b7fd59e22aff521d1bb8))
* **python:** Fix exit methods ([a1627d0](https://github.com/kitware/wslink/commit/a1627d0d9b5784ba52efa1e915a2e7d283bd55fa))
* **SmartConnect:** Provide optional config decorator method ([9b6302f](https://github.com/kitware/wslink/commit/9b6302f68a1257cb834c1b4ab792a57853605edf))
* **twisted:** Update to 19.2.1 which is the same as PV ([b732f97](https://github.com/kitware/wslink/commit/b732f97dec10774d51342bbbeb5696ae37d6aa08))
* **version:** Update version to 0.1.12 ([71f8cce](https://github.com/kitware/wslink/commit/71f8cced0648b0729dcc9247fa31342016e86cbe))
* **version:** Update version to 0.1.13 ([6cc5441](https://github.com/kitware/wslink/commit/6cc544151079587228760eb8ccdf2ad5a7745c0e))
* **websocket:** allow publish before connect, as a no-op ([10bef95](https://github.com/kitware/wslink/commit/10bef955b826ff7bf678f19dfe02972f83844ba9))


### BREAKING CHANGES

* **deps:** remove Py2 support and switch to aiohttp server

Re-implement the back-end using the websocket server implementation
from aiohttp, while leaving open the possibility of swapping out other
backends down the road.
