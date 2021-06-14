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
import Highlight, { defaultProps } from 'prism-react-renderer';
import themeGithub from 'prism-react-renderer/themes/github';
import themeDracula from 'prism-react-renderer/themes/dracula';


function themeCase(theme) {
    return theme == 'dark' ? themeDracula : themeGithub;
}


function CodeBlock({ code, language='jsx', theme='light' }) {
    return (
        <Highlight {...defaultProps} code={code} language={language} theme={themeCase(theme)}>
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
};

export default CodeBlock;
