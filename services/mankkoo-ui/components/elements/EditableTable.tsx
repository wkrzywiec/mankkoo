import { Dispatch, SetStateAction } from "react";

import classes from '@/components/elements/EditableTable.module.css'

import Button from "./Button";
import Input from "./Input";

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
    <div className={classes.tableContainer}>
      <table className={classes.editableTable}>
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
                <Input
                  type="text"
                  value={row.property}
                  onChange={(e) => handleChange(row.id, "property", e.target.value)}
                />
              </td>
              <td>
                <Input
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