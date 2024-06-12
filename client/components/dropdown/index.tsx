import React from "react";

function useOutsideAlerter(
  ref: React.RefObject<HTMLElement>,
  setX: React.Dispatch<React.SetStateAction<boolean>>
): void {
  React.useEffect(() => {
    /**
     * Alert if clicked on outside of element
     */
    // function handleClickOutside(event: React.MouseEvent<HTMLElement>) {
    function handleClickOutside(event: MouseEvent) {
      if (ref.current && !ref.current.contains(event["target"] as Node)) {
        setX(false);
      }
    }
    // Bind the event listener
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      // Unbind the event listener on clean up
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [ref, setX]);
}

const Dropdown = (props: {
  button: React.ReactNode;
  children: React.ReactNode;
  classNames: string;
  animation?: string;
}) => {
  const { button, children, classNames, animation } = props;
  const wrapperRef = React.useRef<HTMLDivElement | null>(null);
  const [openWrapper, setOpenWrapper] = React.useState<boolean>(false);
  useOutsideAlerter(wrapperRef, setOpenWrapper);

  const closeDropdown = () => {
    setOpenWrapper(false);
  };

  return (
    <div ref={wrapperRef} className="relative flex">
      <div
        className="flex items-center justify-center h-10"
        onMouseDown={() => setOpenWrapper(!openWrapper)}
      >
        {button}
      </div>
      <div
        className={`${classNames} absolute z-10 ${
          animation
            ? animation
            : "origin-top-right transition-all duration-300 ease-in-out"
        } ${openWrapper ? "scale-100" : "scale-0"}`}
      >
        {React.Children.map(children, (child: any) =>
          React.cloneElement(child, { onClick: closeDropdown })
        )}
      </div>
    </div>
  );
};

export default Dropdown;
