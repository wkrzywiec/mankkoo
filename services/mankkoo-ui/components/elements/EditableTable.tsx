import { Dispatch, SetStateAction } from "react";

import "./EditableTable.css";
import Button from "./Button";

export interface Row {
  id: number;
  property: string;
  value: string;
}

export default function EditableTable(
    {rows = [{id: 0, property: "", value: ""}], setRows}:
    {rows?: Row[], setRows: Dispatch<SetStateAction<Row[]>>}
) {
  
  const handleChange = (id: number, field: string, value: string) => {
    setRows((prevRows) =>
      prevRows.map((row) =>
        row.id === id ? { ...row, [field]: value } : row
      )
    );
  };

  const addRow = () => {
    setRows([...rows, { id: rows.length + 1, property: "", value: "" }]);
  };

  return (
    <div className="table-container">
      <table className="editable-table">
        <thead>
          <tr>
            <th>Value</th>
            <th>Property</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.id}>
              <td>
                <input
                  type="text"
                  value={row.property}
                  onChange={(e) => handleChange(row.id, "property", e.target.value)}
                />
              </td>
              <td>
                <input
                  type="text"
                  value={row.value}
                  onChange={(e) => handleChange(row.id, "value", e.target.value)}
                />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <Button onClick={addRow}>Add Row</Button>
    </div>
  );
}