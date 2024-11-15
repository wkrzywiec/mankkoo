import styles from "./Table.module.css";

import { CSSProperties } from 'react';
import { getColor } from "@/app/colors";
import { currencyFormat } from "@/utils/Formatter";

const COLOR_CIRCLE_CELL_PATTERN = "circle_#"

export interface TableData {
    data: string [][];
    currencyColumnIdx?: number;
    boldFirstRow?: boolean;
    boldLastRow?: boolean;
    colorsColumnIdx?: number;
}

export default function Table({
    input,
    style
}: {input?: TableData,
    style?: CSSProperties
    }) {

    let preparedData: string [][];

    if (input === undefined) {
        const data = [
            ["Checking accounts", "50 000 PLN", "85%"],
            ["Savings accounts", "5 000 PLN", "5%"],
            ["Treasury bonds", "10 000 PLN", "10%"],
            ["Shares & ETFs", "10 000 PLN", "10%"],
            ["Total", "54 000.45 PLN", ""],
        ]
        input = {data: data, boldLastRow: true}
        preparedData = [...data]
    }

    preparedData = [...input.data]

    const boldLastRow = input?.boldLastRow !== undefined;
    const boldFirstRow = input?.boldFirstRow !== undefined;

    addColorCircleColumn(preparedData, input?.colorsColumnIdx);
    addRowNumberColumn(preparedData, boldLastRow, boldFirstRow);

    const rows = preparedData.map((rowData, rowIndex) => 
        <tr key={rowIndex} className={(defineRowClass(preparedData, rowIndex, boldLastRow, boldFirstRow))}>
            { rowData.map((cellData, cellIndex) => {
                
                if (shouldAddColorCircleToCell(cellData, preparedData, rowIndex, boldLastRow)) {
                    return <td key={rowIndex + "_" + cellIndex}><span className={styles.dot} style={{backgroundColor: cellData.replace(COLOR_CIRCLE_CELL_PATTERN, "")}}></span></td>
                }

                if (shouldSkipAddColorCircleToCellAndLeaveItEmpty(cellData, preparedData, rowIndex, boldLastRow)) {
                    return <td key={rowIndex + "_" + cellIndex}></td>
                }

                return <td key={rowIndex + "_" + cellIndex}>{cellIndex === input?.currencyColumnIdx ? currencyFormat(cellData) : cellData}</td>
            }
                
            )}
        </tr>
    )
    return (
        <table style={style} className={styles.table}>
            <tbody>
                {rows}
            </tbody>
        </table>
    )
}

function addRowNumberColumn(data: string[][], boldLastRow: boolean, boldFirstRow: boolean): void {
    if (data !== undefined && data.length === 0) {
        return;
    }

    const rowNumberColumnIsNotPresent: boolean = boldFirstRow ? data[1][0] != '01' : data[0][0] != '01';
    
    if (rowNumberColumnIsNotPresent) {
        data.forEach((row, rowIndex) => {
            if ((rowIndex === data.length - 1 && boldLastRow) || (rowIndex === 0 && boldFirstRow)) {
                row.splice(0, 0, '');
            } else {
                row.splice(0, 0, boldFirstRow ? rowNumberAsString(rowIndex) : rowNumberAsString(rowIndex + 1));
            }
        })
    }
}

function rowNumberAsString(rowIndex: number): string {
    const rowIndexStr = rowIndex.toString();
    return rowIndexStr.length === 1 ? '0' + rowIndexStr : rowIndexStr;
}

function addColorCircleColumn(data: string[][], colorsColumnIdx: number | undefined): void {
    const colorsColumnNeedsToBeAdded = colorsColumnIdx != undefined;
    const dataWasProvided = data.length > 0;
    const colorCircleIsAlreadyPresent = data !== undefined && data[0] !== undefined && data[0].some(cell => cell.includes(COLOR_CIRCLE_CELL_PATTERN));
    
    if (colorsColumnNeedsToBeAdded && dataWasProvided && !colorCircleIsAlreadyPresent) {
        data.forEach((row, rowIndex) => {
            row.splice(colorsColumnIdx, 0, COLOR_CIRCLE_CELL_PATTERN + getColor(rowIndex))
        })
    }
}

function defineRowClass(data: string[][], rowIndex: number, boldLastRow: boolean, boldFirstRow: boolean) {
    if (shouldBoldLastRow(data, rowIndex, boldLastRow)) {
        return styles.boldedRow;
    }
    
    if (shouldBoldFirstRow(data, rowIndex, boldFirstRow)) {
        return styles.boldedFirstRow;
    }
    return styles.row;
}

function shouldBoldLastRow(data: string[][], rowIndex: number, boldLastRow: boolean): boolean {
    return boldLastRow && rowIndex + 1 == data.length;
}

function shouldBoldFirstRow(data: string[][], rowIndex: number, boldFirstRow: boolean): boolean {
    return boldFirstRow && rowIndex === 0;
}

function shouldAddColorCircleToCell(cellData?: string, data: string[][], rowIndex: number, boldLastRow: boolean) {
    return cellData?.includes(COLOR_CIRCLE_CELL_PATTERN) && !shouldBoldLastRow(data, rowIndex, boldLastRow)
}

function shouldSkipAddColorCircleToCellAndLeaveItEmpty(cellData: string, data: string[][], rowIndex: number, boldLastRow: boolean) {
    return cellData.includes(COLOR_CIRCLE_CELL_PATTERN) && shouldBoldLastRow(data, rowIndex, boldLastRow)
}

