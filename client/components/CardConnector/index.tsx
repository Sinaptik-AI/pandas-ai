import React from "react";
import { FaFileCsv } from "react-icons/fa";

const CardConnector = ({
  id,
  isSelected,
  onClick,
  pointerEvents,
}: {
  id: number;
  isSelected: boolean;
  onClick: (cardId: number) => void;
  pointerEvents: React.CSSProperties["pointerEvents"];
}) => {
  const cardStyle: React.CSSProperties = {
    backgroundColor: isSelected ? "black" : "white",
    color: isSelected ? "white" : "black",
    opacity: 0.5,
    pointerEvents: pointerEvents,
  };
  return (
    <div
      style={cardStyle}
      onClick={() => onClick(id)}
      className="border flex items-center justify-center md:h-20 md:w-24 md:p-2 py-2 px-4 rounded cursor-pointer"
    >
      <div className="flex gap-1 justify-center flex-col">
        <span className="m-auto">
          <FaFileCsv size="2em" />
        </span>
        CSV
      </div>
    </div>
  );
};
export default CardConnector;
