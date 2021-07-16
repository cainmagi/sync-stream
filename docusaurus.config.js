/** @type {import('@docusaurus/types').DocusaurusConfig} */
module.exports = {
  title: 'SyncStream',
  tagline: 'A python tool for synchronizing the messages from different threads, processes, or hosts.',
  url: 'https://cainmagi.github.io/sync-stream',
  baseUrl: '/sync-stream/',
  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',
  favicon: 'img/favicon.ico',
  organizationName: 'cainmagi', // Usually your GitHub org/user name.
  projectName: 'sync-stream', // Usually your repo name.
  plugins: [
    'docusaurus-plugin-sass',
    '@docusaurus/plugin-google-gtag',
    [
      '@docusaurus/plugin-sitemap',
      {
        changefreq: 'weekly',
        priority: 0.5,
        trailingSlash: false,
      },
    ],
  ],
  themeConfig: {
    prism: {
      theme: require('prism-react-renderer/themes/github'),
      darkTheme: require('prism-react-renderer/themes/dracula'),
    },
    hideableSidebar: true,
    navbar: {
      title: 'SyncStream',
      logo: {
        alt: 'SyncStream Logo',
        src: 'img/logo.svg',
      },
      items: [
        {
          type: 'doc',
          docId: 'introduction',
          position: 'left',
          label: 'Tutorial',
        },
        {
          type: 'doc',
          docId: 'apis',
          position: 'left',
          label: 'APIs',
        },
        {
          href: 'https://github.com/cainmagi/sync-stream',
          position: 'right',
          className: 'header-github-link',
          'aria-label': 'GitHub repository',
        },
        {
          href: 'https://pypi.org/project/syncstream',
          position: 'right',
          className: 'header-pypi-link',
          'aria-label': 'PyPI repository',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            {
              label: 'Tutorial',
              to: '/docs/',
            },
            {
              label: 'APIs',
              to: '/docs/apis/',
            },
          ],
        },
        {
          title: 'Contact the author',
          items: [
            {
              label: 'Website',
              href: 'https://cainmagi.github.io/',
            },
            {
              label: 'Email',
              href: 'mailto:cainmagi@gmail.com',
            },
            {
              label: 'Github',
              href: 'https://github.com/cainmagi',
            },
          ],
        },
        {
          title: 'Community',
          items: [
            {
              label: 'UH MODAL Lib',
              href: 'https://modal.ece.uh.edu/',
            },
            {
              label: 'University of Houston',
              href: 'https://www.uh.edu/',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Sync-Stream, Yuchen Jin. Built with Docusaurus.`,
    },
    gtag: {
      trackingID: 'G-T579MTMC79',
      anonymizeIP: true,
    },
  },
  presets: [
    [
      '@docusaurus/preset-classic',
      {
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          // Please change this to your repo.
          editUrl:
            'https://github.com/cainmagi/sync-stream/edit/docs/',
        },
        theme: {
          customCss: require.resolve('./src/css/custom.scss'),
        },
      },
    ],
  ],
};
