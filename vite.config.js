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
        shop: resolve(__dirname, 'static/src/js/pages/shop.js'),
        'admin/productimage_single_primary': resolve(__dirname, 'static/src/js/admin/productimage_single_primary.js'),
        mainStyle: resolve(__dirname, 'static/src/scss/main.scss'), // changed back to mainStyle
        adminStyle: resolve(__dirname, 'static/src/scss/admin.scss'), // changed back to adminStyle
      },
      output: {
        entryFileNames: (chunkInfo) => {
          if (chunkInfo.name === 'main' || chunkInfo.name === 'admin' || chunkInfo.name === 'shop') {
            return 'js/[name].js';
          }
          return 'js/[name].js';
        },
        assetFileNames: (assetInfo) => {
          if (assetInfo.name && assetInfo.name.endsWith('.css')) {
            return 'css/[name].css'; // ensure .css extension
          }
          return 'assets/[name]';
        },
      },
    },
  },
  plugins: [
    viteStaticCopy({
      targets: [
        // Example: copy images or fonts if needed
        // { src: 'static/assets/images', dest: 'assets' },
      ],
    }),
  ],
  css: {
    preprocessorOptions: {
      scss: {
        // Additional SCSS options if needed
      },
    },
  },
}); 