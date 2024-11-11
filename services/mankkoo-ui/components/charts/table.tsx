import styles from "./Table.module.css";

import { CSSProperties } from 'react';
import { getColor } from "@/app/colors";
import { currencyFormat } from "@/utils/Formatter";

const COLOR_CIRCLE_CELL_PATTERN = "circle_#"

export interface TableData {
    data: string [][];
    currencyColumnIdx: number;
    totalColumnIdx?: number;
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
            ["Total", "", "54 000.45 PLN", ""],
        ]
        preparedData = [...data]
    } else {
        preparedData = [...input.data]
    }

    const shouldAddTotalRow = input?.totalColumnIdx !== undefined;

    addColorCircleColumn(preparedData, input?.colorsColumnIdx);
    addRowNumberColumn(preparedData, shouldAddTotalRow);

    const rows = preparedData.map((rowData, rowIndex) => 
        <tr key={rowIndex} className={shouldBoldLastRow(preparedData, rowIndex, shouldAddTotalRow) ? styles.boldedRow : styles.row}>
            { rowData.map((cellData, cellIndex) => {
                
                if (shouldAddColorCircleToCell(cellData, preparedData, rowIndex, shouldAddTotalRow)) {
                    return <td key={rowIndex + "_" + cellIndex}><span className={styles.dot} style={{backgroundColor: cellData.replace(COLOR_CIRCLE_CELL_PATTERN, "")}}></span></td>
                }

                if (shouldSkipAddColorCircleToCellAndLeaveItEmpty(cellData, preparedData, rowIndex, shouldAddTotalRow)) {
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

function addRowNumberColumn(data: string[][], shouldAddTotalRow: boolean): void {
    const rowNumberColumnIsNotPresent: boolean = data !== undefined && data[0] !== undefined && data[0][0] != '01';
    
    if (rowNumberColumnIsNotPresent) {
        data.forEach((row, rowIndex) => {
            if (rowIndex === data.length - 1 && shouldAddTotalRow) {
                row.splice(0, 0, '');
            } else {
                row.splice(0, 0, rowNumberAsString(rowIndex + 1));
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

function shouldBoldLastRow(data: string[][], rowIndex: number, boldLastRow: boolean): boolean {
    return boldLastRow && rowIndex + 1 == data.length;
}

function shouldAddColorCircleToCell(cellData: string, data: string[][], rowIndex: number, boldLastRow: boolean) {
    return cellData.includes(COLOR_CIRCLE_CELL_PATTERN) && !shouldBoldLastRow(data, rowIndex, boldLastRow)
}

function shouldSkipAddColorCircleToCellAndLeaveItEmpty(cellData: string, data: string[][], rowIndex: number, boldLastRow: boolean) {
    return cellData.includes(COLOR_CIRCLE_CELL_PATTERN) && shouldBoldLastRow(data, rowIndex, boldLastRow)
}

