import { defineConfig } from 'vite';
import { resolve } from 'path';
import { viteStaticCopy } from 'vite-plugin-static-copy';

export default defineConfig({
  root: '.',
  build: {
    outDir: 'static/dist',
    emptyOutDir: false,
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'static/src/js/main.js'),
        adminStyle: resolve(__dirname, 'static/src/scss/admin.scss'),
      },
      output: {
        entryFileNames: 'js/[name].js',
        assetFileNames: (assetInfo) => {
          if (assetInfo.names?.[0]?.endsWith('.css')) {
            return 'css/[name].css';
          }
          return 'assets/[name]';
        },
      },
    },
  },
  plugins: [
    viteStaticCopy({
      targets: [],
    }),
  ],
  css: {
    preprocessorOptions: {
      scss: {},
    },
  },
});
