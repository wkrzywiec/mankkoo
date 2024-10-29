import styles from "./Table.module.css";

import { CSSProperties } from 'react';
import { getColor } from "@/app/colors";

const COLOR_CIRCLE_CELL_PATTERN = "circle_#"

export default function Table({style, colorsColumn, boldLastRow=false}: {style?: CSSProperties, colorsColumn?:number, boldLastRow?: boolean}) {
    const data = [
        ["01", "Checking accounts", "50 000 PLN", "85%"],
        ["02", "Savings accounts", "5 000 PLN", "5%"],
        ["03", "Treasury bonds", "10 000 PLN", "10%"],
        ["04", "Shares & ETFs", "10 000 PLN", "10%"],
        ["Total", "", "54 000.45 PLN", ""],
    ]

    const preparedData = [...data]

    if (colorsColumn != undefined) {
        addColorCircleColumn(preparedData, colorsColumn)
    }

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

function addColorCircleColumn(data: string[][], colorsColumn: number): void {
    data.forEach((row, rowIndex) => {
        row.splice(colorsColumn, 0, COLOR_CIRCLE_CELL_PATTERN + getColor(rowIndex))
    })
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