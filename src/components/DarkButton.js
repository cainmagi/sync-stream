import React from 'react';

import Link from '@docusaurus/Link';
import { Icon, InlineIcon } from "@iconify/react";
import useThemeContext from '@theme/hooks/useThemeContext'; //docs: https://v2.docusaurus.io/docs/2.0.0-alpha.69/theme-classic#usethemecontext

function DarkButton(props) {
  const { isDarkTheme } = useThemeContext();
  const curStyle = isDarkTheme ? "button--secondary button--outline" : "button--secondary";
  return (
     <Link
      className={`button ${curStyle} button--lg`}
      to={props.to}>
      {props.icon &&
        <InlineIcon icon={props.icon} width='1.35rem' style={{"verticalAlign": "-0.3rem", "marginRight": "1ex"}} />
      }{props.children}
    </Link>
  );
}

export default DarkButton;
