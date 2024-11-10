import styles from "./Table.module.css";

import { CSSProperties } from 'react';
import { getColor } from "@/app/colors";
import { currencyFormat } from "@/utils/Formatter";

const COLOR_CIRCLE_CELL_PATTERN = "circle_#"

export interface TableData {
    data: string [][]
}

export default function Table({
    input,
    style,
    colorsColumnIdx,
    totalColumnIdx
}: {input?: TableData,
    style?: CSSProperties,
    colorsColumnIdx?: number,
    totalColumnIdx?: number}) {

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

    const shouldAddTotalRow = totalColumnIdx !== undefined;

    
    addColorCircleColumn(preparedData, colorsColumnIdx)
    addRowNumberColumn(preparedData);
    
    if (shouldAddTotalRow) {
        addTotalRow(preparedData, totalColumnIdx)
    } 

    const rows = preparedData.map((rowData, rowIndex) => 
        <tr key={rowIndex} className={shouldBoldLastRow(preparedData, rowIndex, shouldAddTotalRow) ? styles.boldedRow : styles.row}>
            { rowData.map((cellData, cellIndex) => {
                
                if (shouldAddColorCircleToCell(cellData, preparedData, rowIndex, shouldAddTotalRow)) {
                    return <td key={rowIndex + "_" + cellIndex}><span className={styles.dot} style={{backgroundColor: cellData.replace(COLOR_CIRCLE_CELL_PATTERN, "")}}></span></td>
                }

                if (shouldSkipAddColorCircleToCellAndLeaveItEmpty(cellData, preparedData, rowIndex, shouldAddTotalRow)) {
                    return <td key={rowIndex + "_" + cellIndex}></td>
                }

                return <td key={rowIndex + "_" + cellIndex}>{cellData}</td>
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

function addRowNumberColumn(data: string[][]): void {
    const rowNumberColumnIsNotPresent: boolean = data !== undefined && data[0] !== undefined && data[0][0] != '01';
    
    if (rowNumberColumnIsNotPresent) {
        data.forEach((row, rowIndex) => {
            row.splice(0, 0, rowNumberAsString(rowIndex + 1))
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

function addTotalRow(data: string[][], totalColumnIdx: number | undefined) {
    if (totalColumnIdx !== undefined && data[0] !== undefined) {
        const totalRow = Array(data[0].length).fill("");
        
        totalRow.splice(1, 1, "Total");
        totalRow.splice(totalColumnIdx, 1, "0 000 zł");
        data.splice(data.length, 0, totalRow);
    }
}
