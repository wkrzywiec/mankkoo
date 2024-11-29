import styles from "./Table.module.css";

import { CSSProperties } from 'react';
import { getColor } from "@/app/colors";
import { currencyFormat } from "@/utils/Formatter";

const COLOR_CIRCLE_CELL_PATTERN = "circle_#"

export interface TableData {
    data: string [][];
    currencyColumnIdx: number;
    boldFirstRow: boolean;
    boldLastRow: boolean;
    colorsColumnIdx: number;
}

export default function Table({
    data=[],
    boldFirstRow=false,
    boldLastRow=false,
    currencyColumnIdx=-1,
    colorsColumnIdx=-1,
    style
}: {
    data: string [][];
    currencyColumnIdx: number;
    boldFirstRow: boolean;
    boldLastRow: boolean;
    colorsColumnIdx: number;
    style?: CSSProperties
    }) {

    let preparedData: string [][];

    if (data.length === 0) {
        const data = [
            ["Checking accounts", "50 000 PLN", "85%"],
            ["Savings accounts", "5 000 PLN", "5%"],
            ["Treasury bonds", "10 000 PLN", "10%"],
            ["Shares & ETFs", "10 000 PLN", "10%"],
            ["Total", "54 000.45 PLN", ""],
        ]
        preparedData = [...data]
        boldLastRow = true
        colorsColumnIdx = 2;
    } else {
        preparedData = [...data]
    }

    addRowNumberColumn(preparedData, boldFirstRow, boldLastRow)
    addColorCircleColumn(preparedData, colorsColumnIdx, boldFirstRow, boldLastRow)

    const rows = preparedData.map((rowData, rowIndex) => 
        <tr key={rowIndex} className={(defineRowClass(preparedData, rowIndex, boldLastRow, boldFirstRow))}>
            { rowData.map((cellData, cellIndex) => {
                
                if (shouldAddColorCircleToCell(cellData, preparedData, rowIndex, boldLastRow)) {
                    return <td key={rowIndex + "_" + cellIndex}><span className={styles.dot} style={{backgroundColor: cellData.replace(COLOR_CIRCLE_CELL_PATTERN, "")}}></span></td>
                }

                if (shouldSkipAddColorCircleToCellAndLeaveItEmpty(cellData, preparedData, rowIndex, boldLastRow)) {
                    return <td key={rowIndex + "_" + cellIndex}></td>
                }

                return <td key={rowIndex + "_" + cellIndex}>{cellIndex === currencyColumnIdx ? currencyFormat(cellData) : cellData}</td>
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

function addColorCircleColumn(data: string[][], colorsColumnIdx: number, skipFirstRow: boolean, skipLastRow: boolean): void {
    if (colorsColumnIdx === -1) return
    
    // const colorCircleIsAlreadyPresent = data[0][colorsColumnIdx + 1].includes(COLOR_CIRCLE_CELL_PATTERN)
    const colorCircleIsAlreadyPresent = data[0].some(cell => cell.includes(COLOR_CIRCLE_CELL_PATTERN))
    
    if (!colorCircleIsAlreadyPresent) {
        data.forEach((row, rowIndex) => {
            if ((skipLastRow && rowIndex === data.length - 1) || (skipFirstRow && rowIndex === 0)) {
                row.splice(colorsColumnIdx, 0, '')
            } else {
                row.splice(colorsColumnIdx, 0, COLOR_CIRCLE_CELL_PATTERN + getColor(rowIndex))
            }
        })
    }
}

function addRowNumberColumn(data: string[][], skipFirstRow: boolean, skipLastRow: boolean): void {
    if (data.length === 0) return

    const rowNumberColumnIsNotPresent = skipFirstRow ? data[1][0] != '01' : data[0][0] != '01';
    
    if (rowNumberColumnIsNotPresent) {
        data.forEach((row, rowIndex) => {
            if ((skipLastRow && rowIndex === data.length - 1) || (skipFirstRow && rowIndex === 0)) {
                row.splice(0, 0, '')
            } else {
                row.splice(0, 0, skipFirstRow ? rowNumberAsString(rowIndex) : rowNumberAsString(rowIndex + 1));
            }
        })
    }
}

function rowNumberAsString(rowIndex: number): string {
    const rowIndexStr = rowIndex.toString()
    return rowIndexStr.length === 1 ? '0' + rowIndexStr : rowIndexStr
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
    return cellData?.includes(COLOR_CIRCLE_CELL_PATTERN) && shouldBoldLastRow(data, rowIndex, boldLastRow)
}

