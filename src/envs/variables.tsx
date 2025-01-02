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
    },
    main: {
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
