import styles from "./Table.module.css";

import { getColor } from "@/app/colors";
import { currencyFormat } from "@/utils/Formatter";

const COLOR_CIRCLE_CELL_PATTERN = "circle_#"

//remove it? 
//add headers props
export interface TableData {
    data: string [][];
    hasHeader: boolean;
    boldLastRow: boolean;
    currencyColumnIdx: number;
    colorsColumnIdx: number;
}

export default function Table({
    data=[],
    onRowClick=()=>{},
    rowIds=[],
    hasHeader=false,
    hasRowNumber=true,
    boldLastRow=false,
    currencyColumnIdx=-1,
    colorsColumnIdx=-1,
    style={}
}: {
    data?: string [][];
    onRowClick?: (id:string) => void,
    rowIds?: string[];
    hasHeader?: boolean;
    hasRowNumber?: boolean;
    boldLastRow?: boolean;
    currencyColumnIdx?: number;
    colorsColumnIdx?: number;
    style?: React.CSSProperties;
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

    addRowNumberColumn(preparedData, hasRowNumber, hasHeader, boldLastRow)
    addColorCircleColumn(preparedData, colorsColumnIdx, hasHeader, boldLastRow)

    const rows = preparedData.map((rowData, rowIndex) => 
        <tr key={rowIndex} className={(defineRowClass(preparedData, rowIndex, boldLastRow, hasHeader))} onClick={() => onRowClick(rowIds[rowIndex-1])}>
            { rowData.map((cellData, cellIndex) => {
                
                if (shouldAddColorCircleToCell(preparedData, rowIndex, boldLastRow, cellData)) {
                    return <td key={rowIndex + "_" + cellIndex}><span className={styles.dot} style={{backgroundColor: cellData.replace(COLOR_CIRCLE_CELL_PATTERN, "")}}></span></td>
                }

                if (shouldSkipAddColorCircleToCellAndLeaveItEmpty(cellData, preparedData, rowIndex, boldLastRow)) {
                    return <td key={rowIndex + "_" + cellIndex}></td>
                }

                return <td key={rowIndex + "_" + cellIndex}>{cellIndex === currencyColumnIdx ? currencyFormat(cellData) : String(cellData)}</td>
            }
                
            )}
        </tr>
    )
    return (
        <table className={styles.table} style={style}>
            <tbody>
                {rows}
            </tbody>
        </table>
    )
}

function addColorCircleColumn(data: string[][], colorsColumnIdx: number, skipFirstRow: boolean, skipLastRow: boolean): void {
    if (colorsColumnIdx === -1) return
    
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

function addRowNumberColumn(data: string[][], hasRowNumber: boolean, skipFirstRow: boolean, skipLastRow: boolean): void {
    if (data.length === 0) return
    if (hasRowNumber === false) return
    if (skipFirstRow && data.length === 1) return

    const rowNumberColumnIsNotPresent = skipFirstRow ? data[1][0] != '01' : data[0][0] != '01'
    
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



function defineRowClass(data: string[][], rowIndex: number, boldLastRow: boolean, hasHeader: boolean) {
    if (shouldBoldLastRow(data, rowIndex, boldLastRow)) {
        return styles.boldedRow;
    }
    
    if (shouldBoldFirstRow(data, rowIndex, hasHeader)) {
        return styles.boldedFirstRow;
    }
    return styles.row;
}

function shouldBoldLastRow(data: string[][], rowIndex: number, boldLastRow: boolean): boolean {
    return boldLastRow && rowIndex + 1 == data.length;
}

function shouldBoldFirstRow(data: string[][], rowIndex: number, hasHeader: boolean): boolean {
    return hasHeader && rowIndex === 0;
}

function shouldAddColorCircleToCell(data: string[][], rowIndex: number, boldLastRow: boolean, cellData?: string) {
    if (typeof cellData !== "string") {
        cellData = String(cellData ?? "")
    }
    return cellData.includes(COLOR_CIRCLE_CELL_PATTERN) && !shouldBoldLastRow(data, rowIndex, boldLastRow)
}

function shouldSkipAddColorCircleToCellAndLeaveItEmpty(cellData: string, data: string[][], rowIndex: number, boldLastRow: boolean) {
    if (typeof cellData !== "string") {
        cellData = String(cellData ?? "")
    }
    return cellData.includes(COLOR_CIRCLE_CELL_PATTERN) && shouldBoldLastRow(data, rowIndex, boldLastRow)
}

