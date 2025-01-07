/**
 * Environmental variables of this side.
 * Yuchen Jin, mailto:cainmagi@gmail.com
 */

import React from "react";
import Link from "@docusaurus/Link";
import {useDocsVersion} from "@docusaurus/plugin-content-docs/client";

import InlineIcon from "../components/InlineIcon";
import mdiDot from "@iconify-icons/mdi/dot";

const variables = {
  repoURL: "https://github.com/cainmagi/sync-stream",
  rawURL: "https://raw.githubusercontent.com/cainmagi/sync-stream",
  sourceVersion: {
    "0.3.x": "v0.3.3",
    "1.2.1": "v1.2.1",
    main: "main",
  },
  sourceURIs: {
    "v0.3.3": {
      ".": "__init__.py",
      base: "base.py",
      "base.is_end_line_break": "base.py#L25",
      "base.GroupedMessage": "base.py#L37",
      file: "file.py",
      "file.LineFileBuffer": "file.py#L32",
      host: "host.py",
      "host.LineHostMirror": "host.py#L37",
      "host.LineHostBuffer": "host.py#L254",
      mproc: "mproc.py",
      "mproc.LineBuffer": "mproc.py#L37",
      "mproc.LineProcMirror": "mproc.py#L173",
      "mproc.LineProcBuffer": "mproc.py#L357",
      webtools: "webtools.py",
      "webtools.StdoutWrapper": "webtools.py#L24",
      "webtools.SafePoolManager": "webtools.py#L46",
      "webtools.SafeRequest": "webtools.py#L57",
      "webtools.clean_http_manager": "webtools.py#L71",
      "webtools.close_request_session": "webtools.py#L78",
    },
    main: {
      ".": "__init__.py",
      base: "base.py",
      "base.is_end_line_break": "base.py#L45",
      "base.SerializedMessage": "base.py#L60",
      "base.is_serialized_grouped_message": "base.py#L96",
      "base.redirect_stdout": "base.py#L124",
      "base.redirect_stderr": "base.py#L146",
      "base.GroupedMessage": "base.py#L168",
      file: "file.py",
      "file.LineFileBuffer": "file.py#L45",
      host: "host.py",
      "host.LineHostMirror": "host.py#L58",
      "host.LineHostBuffer": "host.py#L497",
      "host.LineHostReader": "host.py#L770",
      mproc: "mproc.py",
      "mproc.LineBuffer": "mproc.py#L343",
      "mproc.LineProcMirror": "mproc.py#L385",
      "mproc.LineProcBuffer": "mproc.py#L754",
      utils: "utils.py",
      "utils.cancel_type": "utils.py#L61",
      "utils.ModuleReplaceError": "utils.py#L65",
      "utils.lazy_import": "utils.py#L555",
      "utils.get_lazy_attribute": "utils.py#L614",
      "utils.is_module_invalid": "utils.py#L627",
      webtools: "webtools.py",
      "webtools.MethodApproved": "webtools.py#L62",
      "webtools.ReqLocApproved": "webtools.py#L65",
      "webtools.ReqFile": "webtools.py#L73",
      "webtools.SafePoolManager": "webtools.py#L76",
      "webtools.SafeRequest": "webtools.py#L97",
      "webtools.clean_http_manager": "webtools.py#L157",
      "webtools.close_request_session": "webtools.py#L164",
    },
  },
};

const useCurrentSourceVersion = (): string => {
  const versionHook = useDocsVersion();
  const versionLabel = versionHook?.label;
  return (
    variables.sourceVersion[versionLabel] || variables.sourceVersion["main"]
  );
};

export const rawURL = (url: string): string => {
  return variables.rawURL + "/" + url;
};

export const repoURL = (url: string | undefined = undefined): string => {
  return url ? variables.repoURL + "/" + url : variables.repoURL;
};

export const releaseURL = (ver: string | undefined = undefined): string => {
  const _ver = ver?.toLowerCase() === "next" ? "main" : ver;
  const version = variables.sourceVersion[_ver] || useCurrentSourceVersion();
  if (version === "main" || _ver === "main") {
    return variables.repoURL + "/releases/latest";
  }
  return variables.repoURL + "/releases/tag/" + version;
};

export const rootURL = (url: string): string => {
  const currentSourceVersion = useCurrentSourceVersion();
  return variables.repoURL + "/blob/" + currentSourceVersion + "/" + url;
};

const getURIByVersionPath = (path: string, ver: string): string => {
  const routes = typeof path === "string" ? path.trim() : "";
  if (routes.length === 0) {
    return path;
  }
  const currentURI = variables.sourceURIs[ver] || variables.sourceURIs["main"];
  return currentURI[path] || path;
};

export const sourceURL = (url: string): string => {
  const currentSourceVersion = useCurrentSourceVersion();
  return (
    variables.repoURL +
    "/blob/" +
    currentSourceVersion +
    "/syncstream/" +
    getURIByVersionPath(url, currentSourceVersion)
  );
};

// No demos now.
// export const demoURL = (url?: string): string => {
//   const currentSourceVersion = useCurrentSourceVersion();
//   if (!url) {
//     return variables.repoURL + "/blob/" + currentSourceVersion + "/usage.py";
//   }
//   return (
//     variables.repoURL + "/blob/" + currentSourceVersion + "/examples/" + url
//   );
// };

export type SourceLinkProps = {
  url: string;
  children: JSX.Element | string;
};

export const SourceLink = ({url, children}: SourceLinkProps): JSX.Element => {
  return (
    <Link to={sourceURL(url)} className="noline">
      {children}
    </Link>
  );
};

export type SplitterProps = {
  padx?: string;
};

export const Splitter = ({padx = "0"}: SplitterProps): JSX.Element => {
  return (
    <span style={{padding: "0 " + padx}}>
      <InlineIcon icon={mdiDot} />
    </span>
  );
};
