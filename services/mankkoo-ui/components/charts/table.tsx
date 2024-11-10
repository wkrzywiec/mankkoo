import styles from "./Table.module.css";

import { CSSProperties } from 'react';
import { getColor } from "@/app/colors";

const COLOR_CIRCLE_CELL_PATTERN = "circle_#"

export interface TableData {
    data: string [][]
}

export default function Table({input, style, colorsColumnIdx, boldLastRow=false}: {input?: TableData, style?: CSSProperties, colorsColumnIdx?: number, boldLastRow?: boolean}) {
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

    if (colorsColumnIdx != undefined && preparedData.length > 0) {
        addColorCircleColumn(preparedData, colorsColumnIdx)
    }

    addRowNumberColumn(preparedData, boldLastRow);

    const rows = preparedData.map((rowData, rowIndex) => 
        <tr key={rowIndex} className={shouldBoldLastRow(preparedData, rowIndex, boldLastRow) ? styles.boldedRow : styles.row}>
            { rowData.map((cellData, cellIndex) => {
                
                if (shouldAddColorCircleToCell(cellData, preparedData, rowIndex, boldLastRow)) {
                    return <td key={rowIndex + "_" + cellIndex}><span className={styles.dot} style={{backgroundColor: cellData.replace(COLOR_CIRCLE_CELL_PATTERN, "")}}></span></td>
                }

                if (shouldSkipAddColorCircleToCellAndLeaveItEmpty(cellData, preparedData, rowIndex, boldLastRow)) {
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

function addRowNumberColumn(data: string[][], boldLastRow: boolean): void {
    const rowNumberColumnIsNotPresent: boolean = data !== undefined && data[0] !== undefined && data[0][0] != '01';
    
    if (rowNumberColumnIsNotPresent) {
        data.forEach((row, rowIndex) => {
            if (data.length - 1 === rowIndex && boldLastRow) {
                row.splice(0, 0, '')
            } else {
                row.splice(0, 0, rowNumberAsString(rowIndex + 1))
            }
        })
    }
}

function rowNumberAsString(rowIndex: number): string {
    const rowIndexStr = rowIndex.toString();
    return rowIndexStr.length === 1 ? '0' + rowIndexStr : rowIndexStr;
}

function addColorCircleColumn(data: string[][], colorsColumn: number): void {
    const colorCircleIsPresent: boolean = data !== undefined && data[0] !== undefined && data[0].some(cell => cell.includes(COLOR_CIRCLE_CELL_PATTERN));

    if (!colorCircleIsPresent) {
        data.forEach((row, rowIndex) => {
            row.splice(colorsColumn, 0, COLOR_CIRCLE_CELL_PATTERN + getColor(rowIndex))
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