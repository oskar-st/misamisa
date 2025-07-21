# Frontend Build (JS & SCSS)

We use [Vite](https://vitejs.dev/) for all frontend asset building.

## Development

```
npm install
npm run dev
```
- This starts the Vite dev server with hot reload for both JS and SCSS.

## Production Build

```
npm run build
```
- This compiles and bundles all JS and SCSS from `static/src/` to `static/dist/`.

## Notes

- All SCSS is compiled using Dart Sass via Vite.
- All JS is bundled and output to `static/dist/js/`.
- No need to run `sass` or copy JS manually.
- Place your source files in `static/src/js/` and `static/src/scss/`.
- Output files will be in `static/dist/`. 