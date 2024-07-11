import React from "react";
import {
  MdAvTimer,
  MdCalendarMonth,
  MdComputer,
  MdPerson,
} from "react-icons/md";

const ExecutionDetails = ({
  executionTime,
  executionDate,
  instance,
  user,
}: {
  executionTime: string;
  executionDate: string;
  instance: string;
  user: string;
}) => {
  return (
    <div className="flex justify-between max-w-[800px] gap-3">
      <div className="flex-1 p-4 bg-white shadow-md rounded-lg dark:!bg-darkMain">
        <div className="flex items-center">
          <MdAvTimer className="h-5 w-5 mr-2" />
          <span className="font-semibold text-sm">Execution time</span>
        </div>
        <span className="text-sm">{executionTime}</span>
      </div>
      <div className="flex-1 p-4 bg-white shadow-md rounded-lg dark:!bg-darkMain">
        <div className="flex items-center">
          <MdCalendarMonth className="h-5 w-5 mr-2" />
          <span className="font-semibold text-sm">Execution Date</span>
        </div>
        <span className="text-sm">{executionDate}</span>
      </div>
      <div className="flex-1 p-4 bg-white shadow-md rounded-lg dark:!bg-darkMain">
        <div className="flex items-center">
          <MdComputer className="h-5 w-5 mr-2" />
          <span className="font-semibold text-sm">Instance</span>
        </div>
        <span className="text-sm">{instance}</span>
      </div>
      <div className="flex-1 p-4 bg-white shadow-md rounded-lg dark:!bg-darkMain">
        <div className="flex items-center">
          <MdPerson className="h-5 w-5 mr-2" />
          <span className="font-semibold text-sm">User</span>
        </div>
        <span className="text-sm">{user}</span>
      </div>
    </div>
  );
};

export default ExecutionDetails;
