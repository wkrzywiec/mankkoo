import classes from './menu.module.css'

export default function Menu() {
    return (
        <div className={classes.menu}>
            <nav>
                <ul>
                <li>Mankkoo</li>
                <li>Overview</li>
                <li>Investments</li>
                <li>Financial Fortress</li>
                <li>Real Estate</li>
                <li>Streams</li>
                </ul>
            </nav>  
        </div>
    )
}