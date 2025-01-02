import React from "react";

import {IconifyIcon, InlineIcon} from "@iconify/react";

export type InlineIconMProps = {
  icon: IconifyIcon | string;
  vspace?: number;
  text?: string;
};

/**
 * InlineIconM is a modified InlineIcon.
 *
 * @param props - The properties of the icon, it only supports the customizations of
 *   the icon content and the vertical space.
 * @returns The <InlineIcon/> component with the customization.
 */
const InlineIconM = (props: InlineIconMProps): JSX.Element => {
  const vspace =
    typeof props.vspace === "undefined"
      ? "-0.4rem"
      : typeof props.vspace === "number" && Math.abs(props.vspace) > 0.001
      ? `${props.vspace}rem`
      : "0";

  return props.text ? (
    <>
      <InlineIcon
        icon={props.icon}
        width="1.35rem"
        style={{verticalAlign: vspace}}
      />
      <span style={{marginLeft: "0.3rem"}}>{props.text}</span>
    </>
  ) : (
    <InlineIcon
      icon={props.icon}
      width="1.35rem"
      style={{verticalAlign: vspace}}
    />
  );
};

export default InlineIconM;
