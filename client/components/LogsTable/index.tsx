"use client";
import React from "react";
import { useRouter } from "next/navigation";
import { MdAvTimer, MdCancel, MdCheckCircle } from "react-icons/md";
import { useTheme } from "@table-library/react-table-library/theme";
import { getTheme } from "@table-library/react-table-library/baseline";
import {
  Table,
  Header,
  HeaderRow,
  Body,
  Row,
  HeaderCell,
  Cell,
} from "@table-library/react-table-library/table";
import { LogData } from "@/app/(ee)/settings/logs/logs-interface";

const LogList: React.FC<{ data: LogData[] }> = ({
  data,
}: {
  data: LogData[];
}) => {
  const router = useRouter();

  const theme = useTheme([
    getTheme(),
    {
      Table: `
        --data-table-library_grid-template-columns: 70px 50% 120px 90px minmax(150px, 1fr);
      `,
      HeaderCell: `
        font-weight: 600;
        .dark & {
          color: #fff;
        }
        &:nth-of-type(1) {
          left: 0px;
          z-index: 100;
        }

        &:nth-of-type(2) {
          left: 70px;
          z-index: 100;
        }
      `,
      BaseRow: `
        cursor: pointer;
        .dark & {
          background-color: #191919 !important;
        }
        .dark &:hover {
          color: #fff !important;
          background-color: #2d2d2d !important;
        }
      `,
      BaseCell: `
        border: none !important;
        &:nth-of-type(1) {
          left: 0px;
          position: sticky;
          z-index: 100;
        }

        &:nth-of-type(2) {
          left: 70px;
          position: sticky;
          z-index: 100;
        }
      `,
    },
  ]);

  const handleRowClick = (item) => {
    router.push(`/settings/logs/${item.id}`);
  };

  return (
    <Table
      data={{ nodes: data }}
      theme={theme}
      layout={{ custom: true, horizontalScroll: true }}
    >
      {() => (
        <>
          <Header>
            <HeaderRow>
              <HeaderCell>Id</HeaderCell>
              <HeaderCell resize pinLeft>
                Query
              </HeaderCell>
              <HeaderCell resize pinLeft>
                Latency
              </HeaderCell>
              <HeaderCell resize pinLeft>
                Success
              </HeaderCell>
              <HeaderCell>User</HeaderCell>
            </HeaderRow>
          </Header>
          <Body>
            {data.map((item) => (
              <Row
                key={item.id}
                //@ts-expect-error expected error
                item={item}
                onClick={() => handleRowClick(item)}
              >
                <Cell>{item.id}</Cell>
                <Cell>{item.query}</Cell>
                <Cell>
                  <MdAvTimer
                    className={`mr-1 inline-block ${
                      parseFloat(item.execution_time) < 8
                        ? "text-green-500"
                        : parseFloat(item.execution_time) < 12
                        ? "text-yellow-500"
                        : "text-red-500"
                    }`}
                  />
                  <span
                    className={`${
                      parseFloat(item.execution_time) < 8
                        ? "text-green-500"
                        : parseFloat(item.execution_time) < 12
                        ? "text-yellow-500"
                        : "text-red-500"
                    }`}
                  >
                    {parseFloat(item.execution_time).toFixed(2)} s
                  </span>
                </Cell>
                <Cell>
                  {item.success ? (
                    <MdCheckCircle className="me-1 text-green-500 dark:text-green-300" />
                  ) : (
                    <MdCancel className="me-1 text-red-500 dark:text-red-300" />
                  )}
                </Cell>
                <Cell>
                  {`${item.first_name || ""} ${item.last_name || ""}`}
                </Cell>
              </Row>
            ))}
          </Body>
        </>
      )}
    </Table>
  );
};

export default LogList;
