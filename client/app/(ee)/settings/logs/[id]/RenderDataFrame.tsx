import React from "react";
import Card from "components/card";

interface IProps {
  table: {
    headers?: string[];
    rows?: (string | number)[][];
  };
  index: number;
}

const RenderDataFrame = ({ index, table }: IProps) => {
  return (
    <Card
      className="accordion-table overflow-auto rounded-lg style-1"
      key={index}
      extra="w-full sm:overflow-auto px-6 py-2 px-5"
    >
      <div className="min-w-80 m-auto w-full">
        <div className="!border-px !border-gray-400 uppercase">
          <p className="p-3">Dataset #{index + 1}</p>
          <div className="flex flex-wrap -mx-2">
            {table?.headers?.map((header, headerIndex) => (
              <div key={headerIndex} className="w-1/2 px-2">
                <div className="border-black-200 cursor-pointer border-b pb-2 pl-4 pr-4 pt-4 dark:border-white/30">
                  <div className="text-black-200 items-center justify-between text-xs">
                    {header ? header : ""}
                  </div>

                  <div className="border-white/0 pb-3 pr-4">
                    {table?.rows?.map((row, rowIndex) => (
                      <div
                        key={rowIndex}
                        className="border-white/0 py-1 pl-2 truncate text-sm"
                      >
                        {row[headerIndex]}

                        {row[headerIndex] === null && (
                          <span className="text-red-900">null</span>
                        )}

                        {row[headerIndex] === undefined && (
                          <span className="text-red-900">undefined</span>
                        )}

                        {row[headerIndex] === "" && (
                          <span className="text-red-900">empty</span>
                        )}

                        {row[headerIndex] === " " && (
                          <span className="text-red-900">space</span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </Card>
  );
};

export default RenderDataFrame;
