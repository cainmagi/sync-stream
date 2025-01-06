import React from "react";
import clsx from "clsx";
import styles from "./index.module.scss";

import CodeBlock from "@theme/CodeBlock";

import {indexCodes} from "../../constants/indexCodes";

import Translate, {translate} from "@docusaurus/Translate";

const Feature = (props) => {
  return (
    <div className={clsx("col col--4")}>
      <div className="text--left padding-horiz--md">
        <h3 className="text--center">{props.title}</h3>
        <div>{props.children}</div>
      </div>
    </div>
  );
};

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          <Feature
            title={translate(
              {
                id: "index.features.installBasic.title",
                description: "Sub-title of the feature: installBasic.",
                message: "Installation",
              },
              {}
            )}
          >
            <p>
              <Translate
                id="index.features.installBasic.descr"
                description="Description of the feature: installBasic."
              >
                Run the following command for a basic installation:
              </Translate>
            </p>
            <CodeBlock language="shell" children={indexCodes.installBasic} />
            <p>
              <Translate
                id="index.features.installFull.descr"
                description="Description of the feature: installFull."
              >
                Or the command for a full installation:
              </Translate>
            </p>
            <CodeBlock language="shell" children={indexCodes.installFull} />
          </Feature>
          <Feature
            title={translate(
              {
                id: "index.features.exPlain.title",
                description: "Sub-title of the feature: exPlain.",
                message: "Catch the stdout",
              },
              {}
            )}
          >
            <p>
              <Translate
                id="index.features.exPlain.descr"
                description="Description of the feature: exPlain."
              >
                The following codes provide an example of catching the python
                stdout:
              </Translate>
            </p>
            <CodeBlock language="python" children={indexCodes.exPlain} />
          </Feature>
          <Feature
            title={translate(
              {
                id: "index.features.exProc.title",
                description: "Sub-title of the feature: exProc.",
                message: "Catch the stdout of a sub-process",
              },
              {}
            )}
          >
            <p>
              <Translate
                id="index.features.exProc.descr"
                description="Description of the feature: exProc."
              >
                The following codes provide an example of catching the python
                stdout:
              </Translate>
            </p>
            <CodeBlock language="python" children={indexCodes.exProc} />
          </Feature>
        </div>
      </div>
    </section>
  );
}
