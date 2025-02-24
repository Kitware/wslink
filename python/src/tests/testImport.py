import unittest


class TestImport(unittest.TestCase):
    def test_import_root(self):
        import wslink

    def test_import_chunking(self):
        import wslink.chunking

    def test_import_emitter(self):
        import wslink.emitter

    def test_import_launcher(self):
        import wslink.launcher

    def test_import_protocol(self):
        import wslink.protocol

    def test_import_publish(self):
        import wslink.publish

    def test_import_relay(self):
        import wslink.relay

    def test_import_server(self):
        import wslink.server

    def test_import_ssl(self):
        import wslink.ssl_context

    def test_import_uri(self):
        import wslink.uri

    def test_import_websocket(self):
        import wslink.websocket

    def test_import_backends(self):
        import wslink.backends

    def test_import_backends_aiohttp(self):
        import wslink.backends.aiohttp

    def test_import_backends_generic(self):
        import wslink.backends.generic

    @unittest.skip("ipython is not a dependency of wslink")
    def test_import_backends_jupyter(self):
        import wslink.backends.jupyter

    @unittest.skip("tornado is not a dependency of wslink")
    def test_import_backends_tornado(self):
        import wslink.backends.tornado


if __name__ == "__main__":
    unittest.main()
