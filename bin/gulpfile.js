'use strict';

var fs = require('fs');
var gulp = require('gulp');
var data = require('gulp-data');
var extReplace = require('gulp-ext-replace');
var nunjucksRender = require('gulp-nunjucks-render');  // Templating engine
var toml = require('toml');
var path = require('path');

nunjucksRender.nunjucks.configure({
  watch: false
});


gulp.task('build-config', function () {
  return gulp.src('../*.ini.nunjucks')
          .pipe(data(function () {
            var config = toml.parse(fs.readFileSync('../config.toml', 'utf-8'));
            config.template.app_version = new Date().getTime();
            config.template.install_directory = path.join(__dirname, '..');

            return config.template;
          }))
          .pipe(nunjucksRender())
          .pipe(extReplace('.ini', '.ini.html'))
          .pipe(gulp.dest('..'));
});
