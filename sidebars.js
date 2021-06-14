/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */

module.exports = {
  // By default, Docusaurus generates a sidebar from the docs folder structure
  docs: [
    'introduction',
    {
      type: 'category',
      label: 'Getting Started',
      collapsed: false,
      items: ['guides/installation', 'guides/sync-basic', 'guides/sync-thread', 'guides/sync-proc', 'guides/sync-file', 'guides/sync-host'],
    },
    {
      type: 'category',
      label: 'Advanced Usages',
      collapsed: false,
      items: ['guides/derivation', 'guides/daemon-buffer'],
    },
  ],
  apis: [
    'apis'
  ]

  // But you can create a sidebar manually
  /*
  tutorialSidebar: [
    {
      type: 'category',
      label: 'Tutorial',
      items: ['hello'],
    },
  ],
   */
};
