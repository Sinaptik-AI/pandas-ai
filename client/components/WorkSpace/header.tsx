import React from "react";
import LogoDark from "components/Icons/LogoDark";
import SettingsMenu from "components/SettingsMenu";

const WorkSpaceHeader = () => {
  return (
    <div className="flex items-center justify-between px-10 pt-4">
      <div className="flex items-center justiy-center font-poppins text-[26px] text-navy-700 dark:text-white cursor-pointer">
        <LogoDark />
      </div>
      <SettingsMenu />
    </div>
  );
};

export default WorkSpaceHeader;
