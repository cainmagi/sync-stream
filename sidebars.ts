import type {SidebarsConfig} from "@docusaurus/plugin-content-docs";

/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */

const sidebars: SidebarsConfig = {
  // By default, Docusaurus generates a sidebar from the docs folder structure
  tutorial: [
    "introduction",
    {
      type: "category",
      label: "Getting Started",
      collapsed: false,
      link: {
        type: "generated-index",
        title: "Getting Started",
        slug: "/category/getting-started",
        description: "Starter guides for using syncstream.",
      },
      items: [
        "guides/installation",
        "guides/sync-basic",
        "guides/sync-thread",
        "guides/sync-proc",
        "guides/sync-file",
        "guides/sync-host",
      ],
    },
    {
      type: "category",
      label: "Advanced Usages",
      collapsed: false,
      link: {
        type: "generated-index",
        title: "Advanced Usages",
        slug: "/category/advanced-usages",
        description:
          "Advanced usage guides for customizing the behavior of syncstream.",
      },
      items: ["guides/derivation", "guides/daemon-buffer"],
    },
    "license",
  ],
  apis: [
    "apis",
    {
      type: "category",
      label: "base",
      collapsed: true,
      link: {
        type: "doc",
        id: "apis/base/index",
      },
      items: [
        "apis/base/is_end_line_break",
        "apis/base/is_serialized_grouped_message",
        "apis/base/redirect_stdout",
        "apis/base/redirect_stderr",
        "apis/base/SerializedMessage",
        "apis/base/GroupedMessage",
      ],
    },
    {
      type: "category",
      label: "mproc",
      collapsed: true,
      link: {
        type: "doc",
        id: "apis/mproc/index",
      },
      items: [
        "apis/mproc/LineBuffer",
        "apis/mproc/LineProcMirror",
        "apis/mproc/LineProcBuffer",
      ],
    },
    {
      type: "category",
      label: "file",
      collapsed: true,
      link: {
        type: "doc",
        id: "apis/file/index",
      },
      items: ["apis/file/LineFileBuffer"],
    },
    {
      type: "category",
      label: "host",
      collapsed: true,
      link: {
        type: "doc",
        id: "apis/host/index",
      },
      items: [
        "apis/host/LineHostMirror",
        "apis/host/LineHostBuffer",
        "apis/host/LineHostReader",
      ],
    },
    {
      type: "category",
      label: "webtools",
      collapsed: true,
      link: {
        type: "doc",
        id: "apis/webtools/index",
      },
      items: [
        "apis/webtools/MethodApproved",
        "apis/webtools/ReqLocApproved",
        "apis/webtools/ReqFile",
        "apis/webtools/SafePoolManager",
        "apis/webtools/SafeRequest",
        "apis/webtools/clean_http_manager",
        "apis/webtools/close_request_session",
      ],
    },
    {
      type: "category",
      label: "utils",
      collapsed: true,
      link: {
        type: "doc",
        id: "apis/utils/index",
      },
      items: [
        "apis/utils/ModuleReplaceError",
        "apis/utils/cancel_type",
        "apis/utils/lazy_import",
        "apis/utils/get_lazy_attribute",
        "apis/utils/is_module_invalid",
      ],
    },
  ],
};

export default sidebars;
