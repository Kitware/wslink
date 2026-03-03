# CHANGELOG

<!-- version list -->

## v2.5.3 (2026-03-03)

### Bug Fixes

- Provenance repository url
  ([`3b6409f`](https://github.com/Kitware/wslink/commit/3b6409f65604fe571e3a75dac7369410fb61ef23))


## v2.5.2 (2026-03-03)

### Bug Fixes

- Force release
  ([`bdb476c`](https://github.com/Kitware/wslink/commit/bdb476c134294c371cd98a854b5a218fb37d54dc))

- Update validate-pyproject
  ([`29c85a2`](https://github.com/Kitware/wslink/commit/29c85a29936720610d1773033345b6531bef634c))


## v2.5.1 (2026-03-02)

### Bug Fixes

- **ci**: Install uv
  ([`6d84d75`](https://github.com/Kitware/wslink/commit/6d84d75467e6ab40f5efbc331cb4430bc29561bd))

- **ci**: Install uv in the release job
  ([`b660cd3`](https://github.com/Kitware/wslink/commit/b660cd37da103e0adc09cf31af0effedddf6dd7a))

- **ci**: Test release
  ([`cbc46ec`](https://github.com/Kitware/wslink/commit/cbc46ec00af4ae3228534db7cee4ca5fcd8f6fd8))

### Chores

- Py + js
  ([`2609fd7`](https://github.com/Kitware/wslink/commit/2609fd729aba7c81937d7e49790ec87b6e128c68))

### Continuous Integration

- Another take at installing uv
  ([`38013ec`](https://github.com/Kitware/wslink/commit/38013eca081bef13cb320d8f1e535c0343bca17c))

- Install pytest
  ([`c91768d`](https://github.com/Kitware/wslink/commit/c91768dad9475dfb5e6a5287e4e433a10cc3fad0))

- Setup
  ([`c63049e`](https://github.com/Kitware/wslink/commit/c63049e77c5dbf734e4f222ffd8bfee49692cbfd))

- Yet anoter attempt at installing uv
  ([`19ad5cc`](https://github.com/Kitware/wslink/commit/19ad5ccf601f3e15860a9cea4e154e87433b7943))


## v2.5.0 (2025-10-20)

### Chores

- **release**: 2.5.0 [skip ci]
  ([`5c4e459`](https://github.com/Kitware/wslink/commit/5c4e459df879479459d497c69e479c71e21c903d))

### Features

- **symlinks**: Add option to enable symlinks for static web serving
  ([`d865d49`](https://github.com/Kitware/wslink/commit/d865d49272a970b82fbaee604168aafde553da5b))


## v2.4.0 (2025-08-18)

### Chores

- **release**: 2.4.0 [skip ci]
  ([`3222baa`](https://github.com/Kitware/wslink/commit/3222baa274250af938a4c4502aae8b651f9e5c5c))

### Features

- **launcher**: Allow to retry launcher request
  ([`0b9b173`](https://github.com/Kitware/wslink/commit/0b9b173a044ed305dda111e0cac3821242d5f9b4))


## v2.3.4 (2025-05-20)

### Bug Fixes

- **http-headers**: Override settings on reload only if env available
  ([`721eb54`](https://github.com/Kitware/wslink/commit/721eb5492bcca40e7ba77638c81d36667f151d86))

### Chores

- **release**: 2.3.4 [skip ci]
  ([`02841cc`](https://github.com/Kitware/wslink/commit/02841cc92a533ff495adde410b9f32b0eb6d377f))


## v2.3.3 (2025-03-23)

### Bug Fixes

- **HEART_BEAT**: Properly reload env when overriden
  ([`c5b7f3a`](https://github.com/Kitware/wslink/commit/c5b7f3a3ec5b89dbbd987b1887f3a552e511de13))

### Chores

- **ci**: Add import tests and integrate existing test in the ci
  ([`bbf8f48`](https://github.com/Kitware/wslink/commit/bbf8f48940d6251aa4dd0150078d8f907c2497aa))

- **release**: 2.3.3 [skip ci]
  ([`a149675`](https://github.com/Kitware/wslink/commit/a14967505c6337f9830707c68c869885a82dd282))


## v2.3.2 (2025-02-21)

### Bug Fixes

- **emitter**: Add EventEmitter tests and a way to specify allowed events
  ([`b079e2e`](https://github.com/Kitware/wslink/commit/b079e2e1eeb1bbed35220d537ab64426946cbde7))

### Chores

- **release**: 2.3.2 [skip ci]
  ([`c7501b4`](https://github.com/Kitware/wslink/commit/c7501b4c7acf72044380b7e5fe59b6cc56ff6e3a))


## v2.3.1 (2025-02-21)

### Bug Fixes

- **typing**: Remove typing messing up ParaView apps
  ([`158bbda`](https://github.com/Kitware/wslink/commit/158bbda82977a3311f0a6580dda94dc3def85653))

### Chores

- **release**: 2.3.1 [skip ci]
  ([`fdadf69`](https://github.com/Kitware/wslink/commit/fdadf69804c2f6e49f9ce9a9bdd2a2a1f8e2e0cd))


## v2.3.0 (2025-02-20)

### Chores

- **release**: 2.3.0 [skip ci]
  ([`5a3c092`](https://github.com/Kitware/wslink/commit/5a3c092600874a3773ce0dd89040dd84cf4dbe7c))

### Features

- **protocol**: Log internal events through an object that can be subscribed to
  ([`89175ba`](https://github.com/Kitware/wslink/commit/89175baee9f1956ab007368e577fff1d2709e30e))


## v2.2.2 (2025-01-07)

### Bug Fixes

- **aiohttp**: Use AppKey for state
  ([`3a313f9`](https://github.com/Kitware/wslink/commit/3a313f9418498a6f9de66f45ecb7ca691ace45e5))

### Chores

- **release**: 2.2.2 [skip ci]
  ([`9d88c5c`](https://github.com/Kitware/wslink/commit/9d88c5c0dc5af3227bdc09a84b819497ae7f4a69))


## v2.2.1 (2024-09-16)

### Bug Fixes

- **NetworkMonitor**: Add async completion() method
  ([`62e4c68`](https://github.com/Kitware/wslink/commit/62e4c6812d111f3a50cbaeb9a7a4a988822efef5))

### Chores

- **release**: 2.2.1 [skip ci]
  ([`b48f83a`](https://github.com/Kitware/wslink/commit/b48f83ab0e7f32b7e00a183e0271af50ea08717b))


## v2.2.0 (2024-09-16)

### Chores

- **release**: 2.2.0 [skip ci]
  ([`64817de`](https://github.com/Kitware/wslink/commit/64817de8b1a9650a4f1d75136992bd14e908c3d9))

### Features

- **NetworkMonitor**: Add support for network completion monitoring
  ([`3202aad`](https://github.com/Kitware/wslink/commit/3202aad42f71f2be156830412d77786f695684e9))


## v2.1.3 (2024-09-09)

### Bug Fixes

- **generic**: Proper api call
  ([`c443c74`](https://github.com/Kitware/wslink/commit/c443c7490efcb0b030b303025946088af72c4476))

### Chores

- **release**: 2.1.3 [skip ci]
  ([`5cbc713`](https://github.com/Kitware/wslink/commit/5cbc713c3fa818bde134c890b65f2585dfc1ab8c))


## v2.1.2 (2024-08-07)

### Bug Fixes

- **js**: SessionManagerURL use baseURI
  ([`bb4c34c`](https://github.com/Kitware/wslink/commit/bb4c34ce64f5056f1dc1b442edc2f79410983ac1))

### Chores

- **release**: 2.1.2 [skip ci]
  ([`1747ac7`](https://github.com/Kitware/wslink/commit/1747ac7ce59d8da88b371f95b02cc2421b5b7d8c))


## v2.1.1 (2024-06-20)

### Bug Fixes

- Add missing __future__ annotations for type hints
  ([`472950f`](https://github.com/Kitware/wslink/commit/472950f98cee2175a507e664ef993eec471469fc))

### Chores

- **release**: 2.1.1 [skip ci]
  ([`cce64ab`](https://github.com/Kitware/wslink/commit/cce64abe4b2da1e6b75b6518cee4e1b60504b355))


## v2.1.0 (2024-06-19)

### Chores

- **release**: 2.1.0 [skip ci]
  ([`9353534`](https://github.com/Kitware/wslink/commit/9353534b71432edae88521dba5b5274cf0f58d18))

### Features

- **http**: Add WSLINK_HTTP_HEADERS for HTTP header addon
  ([`7d16203`](https://github.com/Kitware/wslink/commit/7d16203788c29ff234b693689e85491dc94c86e1))


## v2.0.5 (2024-06-06)

### Bug Fixes

- **py**: Add msg overhead in size limit
  ([`5481a72`](https://github.com/Kitware/wslink/commit/5481a72148ff03bb11ed658952ab4c64f69950fe))

### Chores

- **release**: 2.0.5 [skip ci]
  ([`f25f758`](https://github.com/Kitware/wslink/commit/f25f758fc6216d439530b5bf505fbf3ad1c022a5))


## v2.0.4 (2024-05-24)

### Bug Fixes

- **header**: Add default headers for shared_array_buffer
  ([`0f9f22c`](https://github.com/Kitware/wslink/commit/0f9f22c2e9fb9db199d483bc6ad5fe7e26db8084))

### Chores

- **release**: 2.0.4 [skip ci]
  ([`bc53ca4`](https://github.com/Kitware/wslink/commit/bc53ca4896b36d1b3818561bcfc5da6202788cab))

### Continuous Integration

- Setuptools
  ([`401cc32`](https://github.com/Kitware/wslink/commit/401cc322faee8d2d55b5d105504caf042f2cbe5f))


## v2.0.3 (2024-05-20)

### Bug Fixes

- **unchunker**: Initial allowed message size to env var
  ([#158](https://github.com/Kitware/wslink/pull/158),
  [`488d637`](https://github.com/Kitware/wslink/commit/488d637eb9df2649444c5223c61669e142096a2b))

### Chores

- Delete cpp directory
  ([`3508390`](https://github.com/Kitware/wslink/commit/35083905012575ab5f854d9f72a2d84ee26791af))

- **release**: 2.0.3 [skip ci]
  ([`f7ff40d`](https://github.com/Kitware/wslink/commit/f7ff40d4a5c42a60c88384937f892b47f958fa09))


## v2.0.2 (2024-04-18)

### Bug Fixes

- **jupyter**: Properly handle generic ws for jupyter
  ([`3bb84de`](https://github.com/Kitware/wslink/commit/3bb84dea56818f074628412fcc6c8063eaf87c01))

### Chores

- **release**: 2.0.2 [skip ci]
  ([`9520279`](https://github.com/Kitware/wslink/commit/95202796da9980dbe6d7d1a1c79216d859558b94))


## v2.0.1 (2024-04-16)

### Bug Fixes

- **cli**: Remove shorthand args
  ([`880951a`](https://github.com/Kitware/wslink/commit/880951a8bd3e5d4d8c2a916f602f71c10c61e84e))

### Chores

- **release**: 2.0.1 [skip ci]
  ([`9206d1a`](https://github.com/Kitware/wslink/commit/9206d1a6e8b6e597e49e4b0aa828d996fa053fd4))


## v2.0.0 (2024-04-10)

### Bug Fixes

- **python**: Make msgpack/chunking compatible down to python 3.7
  ([`897ece7`](https://github.com/Kitware/wslink/commit/897ece73de93ddf4d0333d84ad778bf5e445ead7))

### Chores

- **release**: 2.0.0 [skip ci]
  ([`5f58fb1`](https://github.com/Kitware/wslink/commit/5f58fb11aaa98c80b9edbe622db4a380b23cd6b4))

### Features

- **chunking**: Implement chunking of client/server messages
  ([`a77a680`](https://github.com/Kitware/wslink/commit/a77a680326ae491eee023d01d990cdf3e5808f10))

- **msgpack**: Use msgpack to serialize/deserialize messages
  ([`4968ac1`](https://github.com/Kitware/wslink/commit/4968ac1cfab9aeaf1fcd0525319214f81ddd8973))

### Breaking Changes

- **chunking**: Each message has a header and is possibly chunked


## v1.12.4 (2023-10-25)

### Bug Fixes

- **logging**: Implement scoped logging ([#152](https://github.com/Kitware/wslink/pull/152),
  [`07094c3`](https://github.com/Kitware/wslink/commit/07094c3d6ee502a5e35a1f9aa0c0e88fac377f9c))

### Chores

- **release**: 1.12.4 [skip ci]
  ([`4ae4762`](https://github.com/Kitware/wslink/commit/4ae47625a52b60c10001e6a739f44b57d2cd1e19))


## v1.12.3 (2023-10-05)

### Bug Fixes

- **backend**: Properly handle async run state for generic
  ([`247b046`](https://github.com/Kitware/wslink/commit/247b0460f96c7277fb597b8dced80d81c65cba0a))

### Chores

- **release**: 1.12.3 [skip ci]
  ([`9a6243c`](https://github.com/Kitware/wslink/commit/9a6243c7029cda26a827590210783b030e49ca01))


## v1.12.2 (2023-09-27)

### Bug Fixes

- **ci**: Semantic-release automation
  ([`5967efc`](https://github.com/Kitware/wslink/commit/5967efc2811dcfa662dd51e4388c973c0403f4d5))

### Chores

- **release**: 1.12.2 [skip ci]
  ([`25e0703`](https://github.com/Kitware/wslink/commit/25e07034dea440b8f1b2b61da65eac053599192d))


## v1.12.1 (2023-09-27)

### Bug Fixes

- Try to fix semantic-release
  ([`7f50565`](https://github.com/Kitware/wslink/commit/7f50565b56cfa658d3765a4138f18afbad788f0c))

### Continuous Integration

- Semantic-release update
  ([`f4a85c3`](https://github.com/Kitware/wslink/commit/f4a85c30fdfc8a82a2c5e9e43e4035251f845567))


## v1.12.0 (2023-09-27)

### Chores

- **release**: 1.12.0 [skip ci]
  ([`b3442f5`](https://github.com/Kitware/wslink/commit/b3442f5f3e865e333aa4c77f6e89b3e8413756e6))

### Features

- **jupyter**: Add jupyter backend
  ([`db1bb39`](https://github.com/Kitware/wslink/commit/db1bb3943093b1f420bf30f4d887893b556fccc9))


## v1.11.4 (2023-09-06)

### Bug Fixes

- **protocol**: Const definition and usage
  ([`0c34a25`](https://github.com/Kitware/wslink/commit/0c34a25456611cebf80be801b58c993bdee3b3f5))

### Chores

- **release**: 1.11.4 [skip ci]
  ([`bb133ce`](https://github.com/Kitware/wslink/commit/bb133cec74462201266e18b969169629f3283c93))


## v1.11.3 (2023-09-05)

### Bug Fixes

- **pub_manager**: Handle old global publish manager
  ([`d842b88`](https://github.com/Kitware/wslink/commit/d842b88d841f9c560bc534a5647f3ffcdcd1c070))

### Chores

- **release**: 1.11.3 [skip ci]
  ([`20cf399`](https://github.com/Kitware/wslink/commit/20cf3997b3157da1f1d7d4dd1ecb23060e467c76))


## v1.11.2 (2023-08-30)

### Bug Fixes

- **publish_manager**: Separation at server level for broadcast
  ([`ffd269d`](https://github.com/Kitware/wslink/commit/ffd269d152abec57b8590f3c7e52172eb9841c91))

### Chores

- **release**: 1.11.2 [skip ci]
  ([`8714016`](https://github.com/Kitware/wslink/commit/871401616b46c17fca6a01112d7adba132261676))


## v1.11.1 (2023-06-30)

### Bug Fixes

- **aiohttp**: Use app var instead of inheritance
  ([`a0c7e64`](https://github.com/Kitware/wslink/commit/a0c7e64c6d18dd7e781ee59fae530fd29e130b00))

- **js**: Allow JS to use custom WebSocket implementation
  ([`f7fad26`](https://github.com/Kitware/wslink/commit/f7fad26c58f3808c28cca0f20a3e90d8253c391c))

### Chores

- **release**: 1.11.1 [skip ci]
  ([`f5799a5`](https://github.com/Kitware/wslink/commit/f5799a56d36aaa2e0f713bcd56efc36e23508e74))

### Refactoring

- Rename classes for generic backend
  ([`b82483b`](https://github.com/Kitware/wslink/commit/b82483b524756de1c30e3cb283cd3511d1ae5d54))


## v1.11.0 (2023-06-09)

### Chores

- **release**: 1.11.0 [skip ci]
  ([`658549d`](https://github.com/Kitware/wslink/commit/658549ddde2683d87822212b1f37ecf222b3f5bc))

### Features

- Rework code to simplify backends
  ([`114c422`](https://github.com/Kitware/wslink/commit/114c4224b99cb67bacb44d43206fdc588fe22ce6))

- **backend**: Add generic backend
  ([`d1b2b1b`](https://github.com/Kitware/wslink/commit/d1b2b1baa62f46215aed426fa1d90d3799cc3398))

- **backend**: Add tornado using the generic backend
  ([`ee15e86`](https://github.com/Kitware/wslink/commit/ee15e86303b1e83d1c2bcb7a7b7e140012b9a22a))


## v1.10.2 (2023-05-19)

### Bug Fixes

- **SmartConnect**: Allow delete to call exit later
  ([`eeb7637`](https://github.com/Kitware/wslink/commit/eeb76372e55e6f0b1a9717c679400407997f303a))

### Chores

- **dep**: Update dependencies
  ([`7e77b1f`](https://github.com/Kitware/wslink/commit/7e77b1fa66724ec2049f1a5935b81d166a3f1623))

- **deps**: Bump decode-uri-component
  ([`871796c`](https://github.com/Kitware/wslink/commit/871796cae560ff595c311087767c32d29cb16df9))

- **deps**: Bump express in /tests/chat-rpc-pub-sub/clients/js
  ([`c156657`](https://github.com/Kitware/wslink/commit/c156657a6e122cf2e97041cb82548fe7954629a8))

- **deps**: Bump http-cache-semantics from 4.1.0 to 4.1.1 in /js
  ([`b1bda02`](https://github.com/Kitware/wslink/commit/b1bda021e0fe460439b41783edace7092917188d))

- **deps**: Bump minimatch from 3.0.4 to 3.1.2 in /js
  ([`b8a220b`](https://github.com/Kitware/wslink/commit/b8a220b3add451c78d5502173aa6ae146de516e3))

- **deps**: Bump minimatch in /tests/chat-rpc-pub-sub/clients/js
  ([`428b8ca`](https://github.com/Kitware/wslink/commit/428b8cac286f812c67168f81e3e001b6171b1c9d))

- **deps**: Bump minimist in /tests/chat-rpc-pub-sub/clients/js
  ([`0e0d854`](https://github.com/Kitware/wslink/commit/0e0d8545a71774c2afc24cff7e0e9ec9139ffc9c))

- **deps**: Bump qs in /tests/chat-rpc-pub-sub/clients/js
  ([`c050afc`](https://github.com/Kitware/wslink/commit/c050afcb83b7c814387719e9b0cac1bee988f5e7))

- **deps**: Bump semver-regex from 3.1.2 to 3.1.4 in /js
  ([`4e29557`](https://github.com/Kitware/wslink/commit/4e29557d7bfb8bfe565f9fe6f7a6fa508660eb9e))

- **deps**: Bump shell-quote in /tests/chat-rpc-pub-sub/clients/js
  ([`1dc400c`](https://github.com/Kitware/wslink/commit/1dc400c9fbb2d589528321dcb4b38cd31dd7a232))

- **deps**: Bump terser in /tests/chat-rpc-pub-sub/clients/js
  ([`ab5a3a3`](https://github.com/Kitware/wslink/commit/ab5a3a36ceb8da579c5f09a14a029b4ca994fdcc))

- **lock**: Update lock
  ([`bf724a5`](https://github.com/Kitware/wslink/commit/bf724a5d20edb4da786d8989a01b8f49f7d71bcf))

- **release**: 1.10.2 [skip ci]
  ([`9ff0ba7`](https://github.com/Kitware/wslink/commit/9ff0ba70bf22f54ab9671f124e59453f51338d3b))

### Continuous Integration

- Update os matrix
  ([`a1db296`](https://github.com/Kitware/wslink/commit/a1db296847141f0fca07ac63b5a9debb2b8ff38a))

### Documentation

- **example**: Update build tool
  ([`1a2ceba`](https://github.com/Kitware/wslink/commit/1a2cebae2cfe9fc479ab1f20522f0ac514d390f4))


## v1.10.1 (2023-02-15)

### Bug Fixes

- **gracefulexit**: Handle server exit for exec_mode=main
  ([`9e06313`](https://github.com/Kitware/wslink/commit/9e063134b8e171116b374e80fa1ddcd790ca5109))

- **json5**: Bump version
  ([`4d2e972`](https://github.com/Kitware/wslink/commit/4d2e9725199d3504897b2419880b07bdc606048c))

### Chores

- **deps**: Bump json5 from 2.2.0 to 2.2.2 in /js
  ([`d235c0c`](https://github.com/Kitware/wslink/commit/d235c0c29475161b3c7c860d271f2faf73c9533d))

- **release**: 1.10.1 [skip ci]
  ([`7741944`](https://github.com/Kitware/wslink/commit/7741944b94160b9efa580cb4a8b5fdbe7cf31dbf))

### Documentation

- **readme**: Fix invalid bold syntax
  ([`d5d832a`](https://github.com/Kitware/wslink/commit/d5d832a02694a8f30f6b77095269af9632ec35b2))


## v1.10.0 (2022-12-20)

### Chores

- **release**: 1.10.0 [skip ci]
  ([`e3a9cc9`](https://github.com/Kitware/wslink/commit/e3a9cc9c7566ebebe322d8072a4921c3eecc53ce))

### Features

- **launcher**: Make GET/DELETE endpoint optionals
  ([`2dc2916`](https://github.com/Kitware/wslink/commit/2dc291639fc8fc709c9969df6f1872a19a9b51a0))


## v1.9.3 (2022-12-19)

### Bug Fixes

- **launcher**: Get/delete now works
  ([`c95a23d`](https://github.com/Kitware/wslink/commit/c95a23d87d0360d68e1a58c3dbe63757e9268818))

### Chores

- **release**: 1.9.3 [skip ci]
  ([`6209721`](https://github.com/Kitware/wslink/commit/62097214e46f332205f577861bdbf4c39f221798))


## v1.9.2 (2022-12-08)

### Bug Fixes

- **sessionManagerURL**: Make it path relative aware like default sessionURL
  ([`7c351a3`](https://github.com/Kitware/wslink/commit/7c351a3d7a1b0b3ecd658ea99150ccee68a688ad))

### Chores

- **release**: 1.9.2 [skip ci]
  ([`d2c7e33`](https://github.com/Kitware/wslink/commit/d2c7e33c82143aa81c800310675802a42a20985f))


## v1.9.1 (2022-11-01)

### Bug Fixes

- **clientSession**: Make reverse connection subscriptable
  ([`bb672ca`](https://github.com/Kitware/wslink/commit/bb672ca1ac5be92b015cb4479d4ac1409558de5c))

- **subscriptable**: Fix typo
  ([`13b60c5`](https://github.com/Kitware/wslink/commit/13b60c55f5e182232c8b1ced92db35ed52c92933))

### Chores

- **release**: 1.9.1 [skip ci]
  ([`9ecc683`](https://github.com/Kitware/wslink/commit/9ecc683175a1e388c27883bc1b81d1a5ad54ecab))


## v1.9.0 (2022-10-20)

### Chores

- **release**: 1.9.0 [skip ci]
  ([`ec330d0`](https://github.com/Kitware/wslink/commit/ec330d0fc17bfc2eea2188bea1cd800108a2e6e4))

### Features

- **skip_last_active_client**: Better network handling for collaboration
  ([`e4844e6`](https://github.com/Kitware/wslink/commit/e4844e6c395eb4de8b4223397108127ce24bfa25))


## v1.8.4 (2022-10-13)

### Bug Fixes

- **ws_server**: Handle client disconnection even in case of error
  ([`0fa664e`](https://github.com/Kitware/wslink/commit/0fa664e9b04599c92337e1b9547fb8534fb90eca))

### Chores

- **release**: 1.8.4 [skip ci]
  ([`e14a645`](https://github.com/Kitware/wslink/commit/e14a645d25660b9e4226cbb9a885b532f5a25dd9))


## v1.8.3 (2022-10-13)

### Bug Fixes

- **security**: Publish messages only to authenticated clients
  ([`c630baa`](https://github.com/Kitware/wslink/commit/c630baae5a4b5daea74cbb63d3ab6edfb41b8c55))

### Chores

- **release**: 1.8.3 [skip ci]
  ([`7b0f226`](https://github.com/Kitware/wslink/commit/7b0f226d8846541674044c1facf1c16f244bdd64))


## v1.8.2 (2022-08-24)

### Bug Fixes

- **ssl**: Forgot to import ssl from .ssl_context
  ([`d1f5f71`](https://github.com/Kitware/wslink/commit/d1f5f71d3aa2c2bb060e72ec5d96dbf4f8fc9c19))

### Chores

- **release**: 1.8.2 [skip ci]
  ([`d320547`](https://github.com/Kitware/wslink/commit/d3205471b339e0914633ddebfb24bb0d43e6013d))


## v1.8.1 (2022-08-24)

### Bug Fixes

- **ssl**: Make import optional for ParaView
  ([`be11056`](https://github.com/Kitware/wslink/commit/be1105641524f44127b97179924e57a29530cce6))

### Chores

- **release**: 1.8.1 [skip ci]
  ([`fc00b87`](https://github.com/Kitware/wslink/commit/fc00b871ee9b7e9a704381b30decd615dac6f104))


## v1.8.0 (2022-08-24)

### Chores

- **black**: Run black reformatting on the code
  ([`c1a20b6`](https://github.com/Kitware/wslink/commit/c1a20b698183ad193b171f0d185ff37283641520))

- **release**: 1.8.0 [skip ci]
  ([`6b14c84`](https://github.com/Kitware/wslink/commit/6b14c848cfb5d9b33420603252d3ac6f8550e88a))

### Features

- **SSL**: Support ssl context
  ([`00eed08`](https://github.com/Kitware/wslink/commit/00eed083ae6ac9679d48ba3193c727cd692a74e3))


## v1.7.0 (2022-08-11)

### Chores

- **release**: 1.7.0 [skip ci]
  ([`604a4aa`](https://github.com/Kitware/wslink/commit/604a4aa293451dac95874db8de7c4d50ee984aaf))

### Features

- **reverse-connection**: Add support for ClientWS and Relay service
  ([`f62fef3`](https://github.com/Kitware/wslink/commit/f62fef31f310bbe28ee231184f4a3f78bb482b74))


## v1.6.6 (2022-07-05)

### Bug Fixes

- **aiohttp**: Avoid newer, breaking versions
  ([`de16350`](https://github.com/Kitware/wslink/commit/de1635053ca966c3732be4a86c860efe7608f28f))

### Chores

- **release**: 1.6.6 [skip ci]
  ([`981c07b`](https://github.com/Kitware/wslink/commit/981c07bc222cee23143cde14d18937dc514cc9ec))

### Documentation

- **types**: Add optional kwargs parameter to WebsocketSession.call signature
  ([`1069d2d`](https://github.com/Kitware/wslink/commit/1069d2d36eacfaedc2650e56e49fec42b0694312))


## v1.6.5 (2022-06-03)

### Bug Fixes

- **js**: Properly handle protocol mapping
  ([`d02d41d`](https://github.com/Kitware/wslink/commit/d02d41de6755492115a8cb41fadd54662a696b60))

### Chores

- **release**: 1.6.5 [skip ci]
  ([`0064d32`](https://github.com/Kitware/wslink/commit/0064d3231b0775e12fc27cb9154921edef3d3380))


## v1.6.4 (2022-05-05)

### Bug Fixes

- **ws_server**: Pass server at initialization
  ([`758afe3`](https://github.com/Kitware/wslink/commit/758afe3a0b216fb706c9eed8af61e9b1a3135517))

### Chores

- **release**: 1.6.4 [skip ci]
  ([`efadbec`](https://github.com/Kitware/wslink/commit/efadbece75864a956f50cc6eca93eab83196b4c8))


## v1.6.3 (2022-05-04)

### Bug Fixes

- **startup-msg**: Allow user to override startup message
  ([`eda7a11`](https://github.com/Kitware/wslink/commit/eda7a11856ca719cbe54ec12c7aa10f3fa0fc25a))

### Chores

- **release**: 1.6.3 [skip ci]
  ([`847795e`](https://github.com/Kitware/wslink/commit/847795e9dc3c0a6b3e7141f9d7afb8586a83530b))


## v1.6.2 (2022-05-04)

### Bug Fixes

- **ws**: Ensure valid ws before write
  ([`3ba4e60`](https://github.com/Kitware/wslink/commit/3ba4e601e6fdcc04a5929df3e46e9ec3b26ded89))

### Chores

- **deps**: Bump async in /tests/chat-rpc-pub-sub/clients/js
  ([`9ea9fc3`](https://github.com/Kitware/wslink/commit/9ea9fc3960b4687c9979ebbd584c2667a705752e))

- **release**: 1.6.2 [skip ci]
  ([`7f17977`](https://github.com/Kitware/wslink/commit/7f179770247e4569bca7842d4b466cedd015725e))


## v1.6.1 (2022-04-28)

### Bug Fixes

- **auth,log**: Strip secret from logged messages
  ([`dec6080`](https://github.com/Kitware/wslink/commit/dec60800d55aa90e8a38d7f2a6af08023e6497d4))

### Chores

- **release**: 1.6.1 [skip ci]
  ([`ce2e1c2`](https://github.com/Kitware/wslink/commit/ce2e1c216dbd3384956536dfeba48364bb8ee7d1))


## v1.6.0 (2022-04-26)

### Chores

- **release**: 1.6.0 [skip ci]
  ([`368ebaa`](https://github.com/Kitware/wslink/commit/368ebaa6684c190a7fafa1e59e9a75ea47e5107d))

### Features

- **timeout**: Allow server without shutdown timeout
  ([`3200728`](https://github.com/Kitware/wslink/commit/3200728c535c25bd30c031c0936a2c984fe3a7f8))


## v1.5.3 (2022-04-14)

### Bug Fixes

- **security**: Allow to defer token validation to external method
  ([`06bec0d`](https://github.com/Kitware/wslink/commit/06bec0d5d4b98da90310dc5eca6fc1add09e33e4))

### Chores

- **release**: 1.5.3 [skip ci]
  ([`647dc7d`](https://github.com/Kitware/wslink/commit/647dc7d798cf71c331b46102debd5f5ff5a09016))


## v1.5.2 (2022-04-08)

### Bug Fixes

- **py3.6**: Use get_event_loop instead of get_running_loop
  ([`1b2343c`](https://github.com/Kitware/wslink/commit/1b2343c9a3ff514e79e93a45796cc2db914f129d))

### Chores

- **release**: 1.5.2 [skip ci]
  ([`37c972a`](https://github.com/Kitware/wslink/commit/37c972a805fcf2c627483c96b33e90eb0fd18417))


## v1.5.1 (2022-04-04)

### Bug Fixes

- **license**: Include LICENSE file in wheel
  ([`615b8d6`](https://github.com/Kitware/wslink/commit/615b8d6cd216388693867f58129230c84eaea782))

### Chores

- **release**: 1.5.1 [skip ci]
  ([`2e52743`](https://github.com/Kitware/wslink/commit/2e527434cbe84b848a893d7abe9d987292fc38a9))


## v1.5.0 (2022-04-01)

### Chores

- **release**: 1.5.0 [skip ci]
  ([`75fd3eb`](https://github.com/Kitware/wslink/commit/75fd3eba17bb760e9f1fda8d91c7cc704efb1bef))

### Features

- **exec_mode**: Add exec_mode to start_webserver
  ([`011d387`](https://github.com/Kitware/wslink/commit/011d387165c4859958f3f99b33227723dcf34944))


## v1.4.3 (2022-03-04)

### Bug Fixes

- **queryString**: Keep queryString for index.html redicrect
  ([`478ea09`](https://github.com/Kitware/wslink/commit/478ea096078c04b065210a55c941731be97343c7))

### Chores

- **release**: 1.4.3 [skip ci]
  ([`a6d9596`](https://github.com/Kitware/wslink/commit/a6d95967cd85155003f48e3532cd0fbfcbb80880))


## v1.4.2 (2022-03-04)

### Bug Fixes

- **relativePath**: Add support for relative sessionURL and index.html
  ([`4a53100`](https://github.com/Kitware/wslink/commit/4a5310095f1ffa23f45bbbccfe2f10a13a5e3e69))

### Chores

- **release**: 1.4.2 [skip ci]
  ([`5d7e35e`](https://github.com/Kitware/wslink/commit/5d7e35eb8312608b4aa296a7cf031edea78cc4a6))


## v1.4.1 (2022-02-09)

### Bug Fixes

- **rpc**: Better handling awaitable rpc
  ([`e7eef8a`](https://github.com/Kitware/wslink/commit/e7eef8a11010682a44a1c0b845a2fe8ea4048623))

### Chores

- **release**: 1.4.1 [skip ci]
  ([`3710c90`](https://github.com/Kitware/wslink/commit/3710c90ba5bbf3f7abc4ef9bc5ff2dbe4c625d3b))


## v1.4.0 (2022-02-08)

### Chores

- **debug**: Remove
  ([`95f8ca1`](https://github.com/Kitware/wslink/commit/95f8ca19ed444ec9f68e087bdd429d5ce74ca828))

- **release**: 1.4.0 [skip ci]
  ([`72c1848`](https://github.com/Kitware/wslink/commit/72c18485bb8e416c046513d4c27e430eee173f62))

### Features

- **heartbeat**: Control heartbeat with WSLINK_HEART_BEAT env
  ([`2348bcb`](https://github.com/Kitware/wslink/commit/2348bcbcb66d0a59932c4aabcaa5227893871dcf))


## v1.3.3 (2022-01-24)

### Bug Fixes

- **ts**: Update the type definitions for subscribe
  ([`e300fda`](https://github.com/Kitware/wslink/commit/e300fda999dd67569228f372e08949a5da08b390))

### Chores

- **release**: 1.3.3 [skip ci]
  ([`df1d133`](https://github.com/Kitware/wslink/commit/df1d133ac259d9e27ea982b6ff3c9739c5e24f87))


## v1.3.2 (2022-01-24)

### Bug Fixes

- **js**: Add more type annotations
  ([`5870064`](https://github.com/Kitware/wslink/commit/58700644712c4ed87144cf33ac086015b34bc4af))

### Chores

- **release**: 1.3.2 [skip ci]
  ([`706f188`](https://github.com/Kitware/wslink/commit/706f1884410bc33ce63153f0052029cf3f4d921a))


## v1.3.1 (2022-01-03)

### Bug Fixes

- **python**: Use print for the startup message, not log.critical
  ([`bee2f52`](https://github.com/Kitware/wslink/commit/bee2f520f010a6d2010a8039cd0b734489f10379))

### Chores

- **release**: 1.3.1 [skip ci]
  ([`9c93e5c`](https://github.com/Kitware/wslink/commit/9c93e5cbb1894933edc739014c827cae711ded93))


## v1.3.0 (2021-12-16)

### Chores

- **release**: 1.3.0 [skip ci]
  ([`99d8307`](https://github.com/Kitware/wslink/commit/99d8307def8b5676903897e28fe1e835c2cb0289))

### Features

- **connection**: Forward request+client_id to life cycle methods
  ([`6c82264`](https://github.com/Kitware/wslink/commit/6c82264261344d245e3874a30bc65dfd7bb0fa6e))


## v1.2.1 (2021-12-12)

### Bug Fixes

- **aiohttp**: Register 30s heartbeat on ws
  ([`2f0cc9a`](https://github.com/Kitware/wslink/commit/2f0cc9a212bfa5a538f5c34f62146e56fcf6fea8))

### Chores

- **release**: 1.2.1 [skip ci]
  ([`faca704`](https://github.com/Kitware/wslink/commit/faca7048f69abbaef40306caa83e8a714cf1f917))


## v1.2.0 (2021-12-06)

### Chores

- **release**: 1.2.0 [skip ci]
  ([`70ba1ff`](https://github.com/Kitware/wslink/commit/70ba1fff84514cbd4c401be20d8f2df22edb1ee0))

### Features

- **port=0**: Add infrastructure to handle dynamically assigned port
  ([`eca3e23`](https://github.com/Kitware/wslink/commit/eca3e238d86c18fd28d99869fe4bd93138727ec0))


## v1.1.1 (2021-11-19)

### Bug Fixes

- **attachments**: Better scheduleing for free
  ([`289f3df`](https://github.com/Kitware/wslink/commit/289f3dfaf186ffc72a1e3fd4eeae538c81254792))

### Chores

- **release**: 1.1.1 [skip ci]
  ([`e856180`](https://github.com/Kitware/wslink/commit/e856180e852f1b9224d9908571ec5748220c406a))


## v1.1.0 (2021-10-15)

### Chores

- **release**: 1.1.0 [skip ci]
  ([`ee13298`](https://github.com/Kitware/wslink/commit/ee13298803a60e929f88f9b6605c0e7c33fcc90f))

### Features

- **aiohttp**: Control max wslink msg with env var
  ([`a30c5b2`](https://github.com/Kitware/wslink/commit/a30c5b2df908047a99ceed9d7fb89538ba251a94))


## v1.0.7 (2021-08-25)

### Bug Fixes

- **cli**: Revert default host arg to localhost
  ([`a39d8cf`](https://github.com/Kitware/wslink/commit/a39d8cf936d414c5aad21ed7bf590f791bfdb9ea))

- **static**: Fix routes order definition for static content
  ([`60457ab`](https://github.com/Kitware/wslink/commit/60457ab41bef4f0e6d1be94a605da0f6ea33b1a6))

### Chores

- **release**: 1.0.7 [skip ci]
  ([`f8e038f`](https://github.com/Kitware/wslink/commit/f8e038f5e82fea857692fb8afea85874d3e85acd))


## v1.0.6 (2021-08-20)

### Bug Fixes

- **cli**: Update default --host arg to 0.0.0.0
  ([`ddbdda9`](https://github.com/Kitware/wslink/commit/ddbdda9af0b0cf05cfb4e660633d9c77d20f9e01))

### Chores

- **release**: 1.0.6 [skip ci]
  ([`7e578cc`](https://github.com/Kitware/wslink/commit/7e578cc5ecec36bad3a8ccf046728e9283fd47be))


## v1.0.5 (2021-08-13)

### Bug Fixes

- **python**: Prevent raise condition when sending attachements
  ([`667e68e`](https://github.com/Kitware/wslink/commit/667e68e947d4e6b6ef253cfc06891fd703e0c592))

### Chores

- **release**: 1.0.5 [skip ci]
  ([`6fbaf63`](https://github.com/Kitware/wslink/commit/6fbaf63643140918765d1a806d6caa6cff4e5aa4))

### Testing

- **chat**: Update generated files
  ([`3c3195e`](https://github.com/Kitware/wslink/commit/3c3195e74af18fb784faa0cda7547bf6ef2d3b04))


## v1.0.4 (2021-08-10)

### Bug Fixes

- **JavaScript**: SmartConnector default decorator
  ([`2973c8f`](https://github.com/Kitware/wslink/commit/2973c8f0038f6a5f4106820fae833aeea24ed281))

### Chores

- **release**: 1.0.4 [skip ci]
  ([`7df2be2`](https://github.com/Kitware/wslink/commit/7df2be2134c96c94c1c399eb5af8a075c586978f))

### Testing

- **chat**: Update to use smartconnect
  ([`e21a27c`](https://github.com/Kitware/wslink/commit/e21a27c83b3c70d659484011c2467e945856dd20))


## v1.0.3 (2021-08-10)

### Bug Fixes

- **javascript**: SmartConnect will apply a default config decorator
  ([`11ce5a6`](https://github.com/Kitware/wslink/commit/11ce5a66372bd338080a8527b2e8c8268ac8187b))

- **publish**: Only send publish msgs to each client once
  ([`65ab38d`](https://github.com/Kitware/wslink/commit/65ab38dde2851dd8a590c4a0ccc967ba86f64bb1))

### Chores

- **release**: 1.0.3 [skip ci]
  ([`f6b6b5d`](https://github.com/Kitware/wslink/commit/f6b6b5d4e58c2a3b559e9422f7e0ea32608c433f))

### Documentation

- **website**: Update online documentation
  ([`91b7cbb`](https://github.com/Kitware/wslink/commit/91b7cbb55594fe20115bda2952c77a864ff86fb6))


## v1.0.2 (2021-08-10)

### Bug Fixes

- **http**: Automatically server index.html
  ([`e43dde4`](https://github.com/Kitware/wslink/commit/e43dde43af797ed73f92d1b6a1b6adbd2078ea49))

- **scheduling**: Support scheduling tasks before server starts
  ([`17c6750`](https://github.com/Kitware/wslink/commit/17c6750cc98424ae6e28067b08a34fbb428f19c1))

### Chores

- **dep**: Update requirement syntax to fix invalid security warning
  ([`2efda5b`](https://github.com/Kitware/wslink/commit/2efda5b99056fe759bb0510e4946086f76f74d2a))

- **release**: 1.0.2 [skip ci]
  ([`3b98d06`](https://github.com/Kitware/wslink/commit/3b98d061e405490362d22aa3f12c502037d172dc))

- **test**: Update js client package.json
  ([`1aed96b`](https://github.com/Kitware/wslink/commit/1aed96bb59ef2aeb0122056eb84ab13eaf38529d))

### Testing

- **chat-rpc-pub-sub**: Fixed client
  ([`79ebbfb`](https://github.com/Kitware/wslink/commit/79ebbfbaff55dbb514a9df3f129f217afa348b44))


## v1.0.1 (2021-08-10)

### Bug Fixes

- **js**: Small code cleanup
  ([`58e025e`](https://github.com/Kitware/wslink/commit/58e025efd4f4f3f6deca3c8b88a6046d601fe183))

- **Python**: Better isolate backends implementations
  ([`457b181`](https://github.com/Kitware/wslink/commit/457b181840804831272c5820ce77dfccf16c3d6e))

### Chores

- **release**: 1.0.1 [skip ci]
  ([`e7cb752`](https://github.com/Kitware/wslink/commit/e7cb75203a51e560bc443088bee43ac229a7989a))


## v1.0.0 (2021-08-09)

### Bug Fixes

- **dependencies**: Move json5 from devDependencies to dependencies
  ([`bcb2919`](https://github.com/Kitware/wslink/commit/bcb2919a54074acd1c1f5bca11210a38381dcfce))

- **dependencies**: Update webpack for security updates.
  ([`27d6744`](https://github.com/Kitware/wslink/commit/27d674431546f106db8d5a4c67beb79c479acefa))

- **deps**: Replace twisted/autobahn with asyncio/aiohttp
  ([`2e804bb`](https://github.com/Kitware/wslink/commit/2e804bbde98c75f03a6268067ffd322c954644c2))

- **ProcessLauncher**: Allow user to provide custom http headers
  ([`e831509`](https://github.com/Kitware/wslink/commit/e831509c7766c5315be1b3baf7c1ecf37c900d4f))

- **publish**: Use manager to allow publish to all connected clients
  ([`83b94ab`](https://github.com/Kitware/wslink/commit/83b94ab715c332f5a589d8649fa8bd80e879fcab))

- **python**: Automatic version handling
  ([`964db33`](https://github.com/Kitware/wslink/commit/964db33dd806dafae2e7b7fd59e22aff521d1bb8))

- **python**: Fix exit methods
  ([`a1627d0`](https://github.com/Kitware/wslink/commit/a1627d0d9b5784ba52efa1e915a2e7d283bd55fa))

- **SmartConnect**: Provide optional config decorator method
  ([`9b6302f`](https://github.com/Kitware/wslink/commit/9b6302f68a1257cb834c1b4ab792a57853605edf))

- **twisted**: Update to 19.2.1 which is the same as PV
  ([`b732f97`](https://github.com/Kitware/wslink/commit/b732f97dec10774d51342bbbeb5696ae37d6aa08))

- **version**: Update version to 0.1.12
  ([`71f8cce`](https://github.com/Kitware/wslink/commit/71f8cced0648b0729dcc9247fa31342016e86cbe))

- **version**: Update version to 0.1.13
  ([`6cc5441`](https://github.com/Kitware/wslink/commit/6cc544151079587228760eb8ccdf2ad5a7745c0e))

- **websocket**: Allow publish before connect, as a no-op
  ([`10bef95`](https://github.com/Kitware/wslink/commit/10bef955b826ff7bf678f19dfe02972f83844ba9))

### Chores

- **deps**: Bump highlight.js in /tests/chat-rpc-pub-sub/clients/js
  ([`e349643`](https://github.com/Kitware/wslink/commit/e349643ec444f5fe95fc20a8ef106e55cb322827))

- **deps**: Bump ini from 1.3.5 to 1.3.7 in /js
  ([`7ccb78c`](https://github.com/Kitware/wslink/commit/7ccb78cddbfd5d40ad8e6494bd3998e6c975a135))

- **deps**: Bump lodash from 4.17.11 to 4.17.15 in /js
  ([`bab7db4`](https://github.com/Kitware/wslink/commit/bab7db4eca20519adeab2cd2bfa9c606492acc17))

- **deps**: Bump mixin-deep from 1.3.1 to 1.3.2 in /js
  ([`f598025`](https://github.com/Kitware/wslink/commit/f598025ad68ef4a3bb677e5e3552de6e75f987cc))

- **deps**: Bump url-parse in /tests/chat-rpc-pub-sub/clients/js
  ([`fff9792`](https://github.com/Kitware/wslink/commit/fff97924775fc1b5aba44556019068ed6e385cb3))

- **deps**: Bump websocket-extensions
  ([`cce2481`](https://github.com/Kitware/wslink/commit/cce2481d3e6426c7082a41fdfee6d4d94e74929a))

- **release**: 1.0.0 [skip ci]
  ([`b63579d`](https://github.com/Kitware/wslink/commit/b63579d723f21265256a96999c04c5aa724f4e30))

- **test**: Consolidate tests/simple
  ([`6f6dbbd`](https://github.com/Kitware/wslink/commit/6f6dbbd2cc2cc2780a0e72f44ebc131fd6c3e3e5))

- **tests**: Fix syntax issue
  ([`65b7962`](https://github.com/Kitware/wslink/commit/65b7962d957f7cba61db5a66468d8ae2eac8e367))

- **version**: Bump version
  ([`d8c3b41`](https://github.com/Kitware/wslink/commit/d8c3b41db40c4a4b0271b699bed3eab7842a3b45))

### Continuous Integration

- **ghactions**: Migrate to gh actions
  ([`67b4b9a`](https://github.com/Kitware/wslink/commit/67b4b9ac70ecc8557fe8c401ce883075aea16c7e))


## v0.1.10 (2019-04-22)

### Bug Fixes

- **debug**: Remove debug output in JS
  ([`cd9c977`](https://github.com/Kitware/wslink/commit/cd9c9776cfd7a2e2ef8771a689fd6cd94c6b7af1))

- **deps**: Add extras_require for service_identity
  ([`7378dcf`](https://github.com/Kitware/wslink/commit/7378dcf4bfbb86593d08309e96c268315ad52a36))

- **doc**: Release 1.5 for python, tweak doc.
  ([`4e229e5`](https://github.com/Kitware/wslink/commit/4e229e5755b1f9a0f7e877fa9f9fa460ffdac992))

- **launcher**: Santize potential command lines
  ([`14e8cfc`](https://github.com/Kitware/wslink/commit/14e8cfc9531e1f34d94169c95522f477b610a85a))

- **launcher.py**: Don't enforce begin/end marks in sanitize regexp
  ([`b98d0da`](https://github.com/Kitware/wslink/commit/b98d0dac0cad32bebae8dc9bda60541cdfbf4264))

- **ProcessLauncher**: Fix error handling
  ([`444db41`](https://github.com/Kitware/wslink/commit/444db412e7fa229d6d72f4b68527e7b6dc574014))

- **py**: Bump py version to 0.1.7
  ([`c0290ef`](https://github.com/Kitware/wslink/commit/c0290efeac2e57a275673c1153d3dbed1303c0f9))

- **python**: Add ability to disable timeout, send server quit msg.
  ([`f3736c2`](https://github.com/Kitware/wslink/commit/f3736c23d1577b6a37ce3e8bdbf5257be8475e30))

- **python**: Fix json.loads input for python 3.5 and lower
  ([`5a701ed`](https://github.com/Kitware/wslink/commit/5a701edd03897de0e3887c9cca9ba20dda263208))

- **session**: Support RPC with just a binary attachment result.
  ([`bc0ef5f`](https://github.com/Kitware/wslink/commit/bc0ef5fbb99a9ebd7b9e19b98a7d075287c5014b))

- **session**: Use json5 parser to handle nan/inf
  ([`faa34bc`](https://github.com/Kitware/wslink/commit/faa34bc505f23143f07fa73e6ae46d642451deae))

- **SmartConnect**: Add getter for config
  ([`9fff1ed`](https://github.com/Kitware/wslink/commit/9fff1edf7273b191dafded8833ef390381ae37e1))

- **SmartConnect**: Properly handle error message from launcher
  ([`47a591a`](https://github.com/Kitware/wslink/commit/47a591a6aba4ea6b14d299b67fe562eb580c796f))

- **websocket**: Better support for recursively finding attachments
  ([`3679d61`](https://github.com/Kitware/wslink/commit/3679d61f3344c165e9d547b6373b40f5e010c4b9))

- **websocket**: Handle getSharedObject request even without coreServer
  ([`c6f2c93`](https://github.com/Kitware/wslink/commit/c6f2c9397040f87a94585b20a03e7d9ee1a72c4e))

- **websocket.py**: Support receiving binary attachments
  ([`2522910`](https://github.com/Kitware/wslink/commit/2522910ffed22b95fa29a3c349c26f4df21088d2))

- **websocket.py**: Type check arguments when searching for attachments
  ([`2feb154`](https://github.com/Kitware/wslink/commit/2feb15410aad134b277079db76f8f42234252d57))

- **WebsocketConnection**: Support sending binary attachments
  ([`e0557c2`](https://github.com/Kitware/wslink/commit/e0557c2e62e63f8103496b82e62b3d9186e477de))

- **WebsocketConnection/session**: Rename objSearch -> objFilter
  ([`e8d82e3`](https://github.com/Kitware/wslink/commit/e8d82e36b8053cfc8a6301632c281ab66b218a54))

### Chores

- **npm**: Bump version for npm publish
  ([`11a65c9`](https://github.com/Kitware/wslink/commit/11a65c9a5b4edb88d26cc03cb276a343589f99c3))

- **version**: Bump version
  ([`79ed97d`](https://github.com/Kitware/wslink/commit/79ed97d325aaf3a37462d87494a0032eb3db9d7e))

### Features

- **C++**: Add StreamTracer and Threshold API and Launcher
  ([`4c8750a`](https://github.com/Kitware/wslink/commit/4c8750a85f8e18a19b91e761d59d5285bb5c5c9d))

- **Client**: Add a couple methods, cleanup a tad
  ([`2c47c95`](https://github.com/Kitware/wslink/commit/2c47c95764a290cfb447c16e5e0c563d2f2faeba))

- **smartconnect**: Forward error event from ws connection
  ([`8989d0b`](https://github.com/Kitware/wslink/commit/8989d0b73c355c31a9271c0640f3f40fd3239820))


## v0.1.4 (2017-09-20)

### Bug Fixes

- **python**: Latest versions of autobahn, twisted.
  ([`1d70dfa`](https://github.com/Kitware/wslink/commit/1d70dfac217087632a51dd86f8ee9b1674487121))

- **session**: Add nested attachment handling.
  ([`a3ee6e0`](https://github.com/Kitware/wslink/commit/a3ee6e000a46f5ae5ab51706a0a76c8954f7ed8f))


## v0.1.2 (2017-07-18)

- Initial Release
