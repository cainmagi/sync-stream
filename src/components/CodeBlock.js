/**
 * Copyright (c) 2017-present, Facebook, Inc.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 *
 * @noflow
 * @emails oncall+i18n_fbt_js
 */

import React, { Component } from 'react';
import Highlight, { defaultProps } from 'prism-react-renderer';
import themeGithub from 'prism-react-renderer/themes/github';
import themeDracula from 'prism-react-renderer/themes/dracula';

import useThemeContext from '@theme/hooks/useThemeContext'; //docs: https://v2.docusaurus.io/docs/2.0.0-alpha.69/theme-classic#usethemecontext


function CodeBlock(props) {
  const { isDarkTheme } = useThemeContext();
  console.log(isDarkTheme);
  const curTheme = isDarkTheme ? themeDracula : themeGithub;
  return (
    <Highlight {...defaultProps} code={props.code} language={props.language} theme={curTheme}>
      {({ className, style, tokens, getLineProps, getTokenProps }) => (
      <pre className={className} style={{ ...style, textAlign: 'left' }}>
        {tokens.map((line, i) => (
        <div {...getLineProps({ line, key: i })}>
          {line.map((token, key) => (
          <span {...getTokenProps({ token, key })} />
          ))}
        </div>
        ))}
      </pre>
      )}
    </Highlight>
  );
}


export default CodeBlock;
