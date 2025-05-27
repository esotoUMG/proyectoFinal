//Importando librerias
import { src, dest, watch } from 'gulp';
import * as dartSass from 'sass';
import gulpSass from 'gulp-sass';

const sass = gulpSass(dartSass);

export function css(done) {
    src('static/scss/app.scss', { sourcemaps: true }) // Solo compila el archivo principal
        .pipe(
            sass({
                includePaths: ['static/scss', 'static/scss/base', 'static/scss/layout']
            }).on('error', sass.logError)
        )
        .pipe(dest('static/css', { sourcemaps: '.' }));
    done();
}

export function dev() {
    // Observa todos los cambios en los archivos SCSS
    watch('static/scss/**/*.scss', css);
}
