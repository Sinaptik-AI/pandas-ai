import React, { useEffect } from "react";
import { RiSunFill } from "react-icons/ri";
import { GoMoon } from "react-icons/go";
import { useAppStore } from "store";

const ToggleDarkModeComponent = () => {
  const dm = useAppStore((state) => state.toggleDarkMode);
  const darkmode = useAppStore((state) => state.darkMode);
  const [checked, setChecked] = React.useState<boolean | undefined>(false);

  useEffect(() => {
    const mode = localStorage.getItem("mode");
    const isDarkMode = mode === "dark";
    if (isDarkMode) {
      document.body.classList.add("dark");
    }
    dm(isDarkMode);
    setChecked(isDarkMode);
  }, [checked, darkmode]);

  const toggleDarkMode = () => {
    if (checked) {
      document.body.classList.remove("dark");
      localStorage.removeItem("mode");
      dm(false);
      setChecked(!checked);
    } else {
      document.body.classList.add("dark");
      localStorage.setItem("mode", "dark");
      dm(true);
      setChecked(checked);
    }
  };
  return (
    <div className="flex items-center justify-center">
      <input
        type="checkbox"
        className="checkbox-toggle"
        id="checkbox"
        checked={checked}
        onChange={toggleDarkMode}
      />
      <label htmlFor="checkbox" className="checkbox-label-toggle">
        <RiSunFill className="h-4 w-4 text-gray-600 dark:text-white" />
        <GoMoon className="h-4 w-4 text-gray-600 dark:text-white" />
        <span className={`ball ${darkmode ? "right" : "left"}`}></span>
      </label>
    </div>
  );
};

export default ToggleDarkModeComponent;
