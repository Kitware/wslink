## [1.0.5](https://github.com/kitware/wslink/compare/v1.0.4...v1.0.5) (2021-08-13)


### Bug Fixes

* **python:** prevent raise condition when sending attachements ([667e68e](https://github.com/kitware/wslink/commit/667e68e947d4e6b6ef253cfc06891fd703e0c592))

## [1.0.4](https://github.com/kitware/wslink/compare/v1.0.3...v1.0.4) (2021-08-10)


### Bug Fixes

* **JavaScript:** SmartConnector default decorator ([2973c8f](https://github.com/kitware/wslink/commit/2973c8f0038f6a5f4106820fae833aeea24ed281))

## [1.0.3](https://github.com/kitware/wslink/compare/v1.0.2...v1.0.3) (2021-08-10)


### Bug Fixes

* **javascript:** smartConnect will apply a default config decorator ([11ce5a6](https://github.com/kitware/wslink/commit/11ce5a66372bd338080a8527b2e8c8268ac8187b))
* **publish:** Only send publish msgs to each client once ([65ab38d](https://github.com/kitware/wslink/commit/65ab38dde2851dd8a590c4a0ccc967ba86f64bb1))

## [1.0.2](https://github.com/kitware/wslink/compare/v1.0.1...v1.0.2) (2021-08-10)


### Bug Fixes

* **http:** Automatically server index.html ([e43dde4](https://github.com/kitware/wslink/commit/e43dde43af797ed73f92d1b6a1b6adbd2078ea49))
* **scheduling:** Support scheduling tasks before server starts ([17c6750](https://github.com/kitware/wslink/commit/17c6750cc98424ae6e28067b08a34fbb428f19c1))

## [1.0.1](https://github.com/kitware/wslink/compare/v1.0.0...v1.0.1) (2021-08-10)


### Bug Fixes

* **js:** Small code cleanup ([58e025e](https://github.com/kitware/wslink/commit/58e025efd4f4f3f6deca3c8b88a6046d601fe183))
* **Python:** Better isolate backends implementations ([457b181](https://github.com/kitware/wslink/commit/457b181840804831272c5820ce77dfccf16c3d6e))

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
