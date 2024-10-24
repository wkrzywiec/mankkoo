
export default function Table() {
    const withSummary = true;
    const data = [
        ["01", "Checking accounts", "50 000 PLN", "85%"],
        ["02", "Savings accounts", "5 000 PLN", "5%"],
        ["03", "Treasury bonds", "10 000 PLN", "10%"],
        ["04", "Shares & ETFs", "10 000 PLN", "10%"],
        ["Total", "", "54 000.45 PLN", ""],
    ]

    const rows = data.map((rowData, rowIndex) => 
        <tr key={rowIndex}>
            { rowData.map(
                (cellData, cellIndex) => <td key={rowIndex + "_" + cellIndex}>{cellData}</td>)
            }
        </tr>  
    )
    return (
        <table>
            {rows}
        </table>
    )
}