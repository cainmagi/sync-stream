/**
 * Environmental variables of this side.
 * Yuchen Jin, mailto:cainmagi@gmail.com
 */

import React from 'react';
import Link from '@docusaurus/Link';

const variables = {
  sourceURL: 'https://github.com/cainmagi/sync-stream/blob/b3cd6607bcd0119dddd0b40164164637b7be6108/syncstream'
};

function SourceURL(props) {
  let url = variables.sourceURL + '/' + props.url;
  return (
    <Link to={ url } className="noline">{ props.children }</Link>
  );
};

function Splitter(props) {
  return (
    <span style={{ 'padding': '0 ' + props.padx }}>·</span>
  );
};

Splitter.defaultProps = {
    padx: '1ex'
};

export {SourceURL, Splitter};
