import { useEffect } from "react";
import PropTypes from "prop-types";

const Intercom = ({ appID, ...userProps }) => {
  useEffect(() => {
    (function () {
      const w = window;
      const ic = w.Intercom;
      if (typeof ic === "function") {
        ic("reattach_activator");
        ic("update", w.intercomSettings);
      } else {
        const d = document;
        const i = function () {
          // eslint-disable-next-line prefer-rest-params
          i.c(arguments);
        };
        i.q = [];
        i.c = function (args) {
          i.q.push(args);
        };
        w.Intercom = i;

        const l = function () {
          const s = d.createElement("script");
          s.type = "text/javascript";
          s.async = true;
          s.src = `https://widget.intercom.io/widget/${appID}`;
          const x = d.getElementsByTagName("script")[0];
          x.parentNode.insertBefore(s, x);
        };

        if (d.readyState === "complete") {
          l();
        } else if (w.attachEvent) {
          w.attachEvent("onload", l);
        } else {
          w.addEventListener("load", l, false);
        }
      }

      window.intercomSettings = {
        app_id: appID,
        ...userProps,
      };
    })();
  }, [appID, userProps]);

  return null;
};

Intercom.propTypes = {
  appID: PropTypes.string.isRequired,
};

export default Intercom;
