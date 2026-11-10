// Serve the installed, pinned, unmodified Playwright Trace Viewer. This is the
// same server/redirect used by `playwright show-trace --host ... --port ...`.
// The caller opens its own headed browser; no default user browser is opened.
const { server } = require(process.argv[2]);
const path = require('path');
(async () => {
  const trace = path.resolve(process.argv[3]);
  const http = await server.startTraceViewerServer({
    host: '127.0.0.1', port: 0, allowedFileRoots: () => [path.dirname(trace)]
  });
  await server.installRootRedirect(http, 'file?path=' + encodeURIComponent(trace), {});
  console.log(http.urlPrefix('precise'));
})().catch(error => { console.error(error); process.exitCode = 1; });
