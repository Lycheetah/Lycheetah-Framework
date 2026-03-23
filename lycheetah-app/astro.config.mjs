import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://lycheetah.github.io',
  base: '/',
  output: 'static',
  markdown: {
    remarkPlugins: ['remark-math'],
    rehypePlugins: ['rehype-katex'],
    shikiConfig: {
      theme: 'github-dark',
    },
  },
  vite: {
    resolve: {
      alias: {
        '@': '/src',
      },
    },
  },
});
