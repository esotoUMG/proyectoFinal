import { src, dest, watch } from 'gulp';
import * as dartSass from 'sass';
import gulpSass from 'gulp-sass';

const sass = gulpSass(dartSass);

export function css(done) {
    // Asegúrate de que la ruta sea correcta
    src('static/sass/**/*.scss')  // Busca todos los archivos SCSS
        .pipe(sass().on('error', sass.logError))
        .pipe(dest('static/css'));  // Genera el archivo en static/css/
    done();
}

export function dev() {
    // Observa todos los cambios en los archivos SCSS
    watch('static/sass/**/*.scss', css);
}
