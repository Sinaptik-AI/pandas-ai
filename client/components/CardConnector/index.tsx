import React from "react";
import { BiLogoPostgresql } from "react-icons/bi";
import { FaFileCsv, FaSnowflake } from "react-icons/fa";
import { SiAirtable, SiSqlite } from "react-icons/si";
import {
  TbBrandDatabricks,
  TbBrandMysql,
  TbBrandGoogleBigQuery,
} from "react-icons/tb";

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
      {id === 1 && (
        <div className="flex gap-1 justify-center flex-col">
          <span className="m-auto">
            <FaFileCsv size="2em" />
          </span>
          CSV
        </div>
      )}
      {id === 2 && (
        <div className="flex gap-1 justify-center flex-col">
          <span className="m-auto">
            <BiLogoPostgresql size="2em" />
          </span>
          PostgreSql
        </div>
      )}
      {id === 3 && (
        <div className="flex gap-1 justify-center flex-col">
          <span className="m-auto">
            <TbBrandMysql size="2em" />
          </span>
          MySQL
        </div>
      )}
      {id === 4 && (
        <div className="flex gap-1 justify-center flex-col">
          <span className="m-auto">
            <SiSqlite size="2em" />
          </span>
          Sqlite
        </div>
      )}
      {id === 5 && (
        <div className="flex gap-1 justify-center flex-col">
          <span className="m-auto">
            <FaSnowflake size="2em" />
          </span>
          Snowflake
        </div>
      )}
      {id === 6 && (
        <div className="flex gap-1 justify-center flex-col">
          <span className="m-auto">
            <TbBrandDatabricks size="2em" />
          </span>
          Databricks
        </div>
      )}
      {id === 7 && (
        <div className="flex gap-1 justify-center flex-col">
          <span className="m-auto">
            <TbBrandGoogleBigQuery size="2em" />
          </span>
          BigQuery
        </div>
      )}
      {id === 8 && (
        <div className="flex gap-1 justify-center flex-col">
          <span className="m-auto">
            <SiAirtable size="2em" />
          </span>
          Airtable
        </div>
      )}
    </div>
  );
};
export default CardConnector;
