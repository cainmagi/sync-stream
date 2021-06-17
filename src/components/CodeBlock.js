/**
 * Copyright (c) 2017-present, Facebook, Inc.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 *
 * @noflow
 * @emails oncall+i18n_fbt_js
 */

import React from 'react';
import Highlight, { Prism } from 'prism-react-renderer';

import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import useThemeContext from '@theme/hooks/useThemeContext'; //docs: https://v2.docusaurus.io/docs/2.0.0-alpha.69/theme-classic#usethemecontext


function CodeBlock(props) {
  const { siteConfig } = useDocusaurusContext();
  const { isDarkTheme } = useThemeContext();
  const curTheme = isDarkTheme ? siteConfig.themeConfig.prism.darkTheme : siteConfig.themeConfig.prism.theme;
  return (
    <Highlight Prism={Prism} code={props.code} language={props.language} theme={curTheme}>
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
