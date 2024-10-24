import styles from "./table.module.css";

import { CSSProperties } from 'react';

function shouldBoldLastRow(data: string[][], rowIndex: number, boldLastRow: boolean): boolean {
    return boldLastRow && rowIndex + 1 == data.length;
}

export default function Table({style, boldLastRow=false}: {style?: CSSProperties, boldLastRow?: boolean}) {
    const data = [
        ["01", "Checking accounts", "50 000 PLN", "85%"],
        ["02", "Savings accounts", "5 000 PLN", "5%"],
        ["03", "Treasury bonds", "10 000 PLN", "10%"],
        ["04", "Shares & ETFs", "10 000 PLN", "10%"],
        ["Total", "", "54 000.45 PLN", ""],
    ]

    const rows = data.map((rowData, rowIndex) => 
        <tr key={rowIndex} className={shouldBoldLastRow(data, rowIndex, boldLastRow) ? styles.boldedRow : styles.row}>
            { rowData.map((cellData, cellIndex) => 
                <td key={rowIndex + "_" + cellIndex}>{cellData}</td>
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