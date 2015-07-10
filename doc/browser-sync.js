var browserSync = require('browser-sync');

browserSync({
  notify: true,
  snippetOptions: {
    rule: {
      match: '<span id="browser-sync-binding"></span>',
      fn: function (snippet) {
        return snippet;
      }
    }
  },
  server: {
    baseDir: ['app'],
    routes: {
      '/bower_components': 'bower_components'
    }
  }
});
