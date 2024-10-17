import classes from './menu.module.css'
import MenuItem from '@/components/menu/menu-item'

import { 
    faGaugeHigh, faMoneyBillWave, faChartLine,
    faChessRook, faBuildingUser, faServer } from '@fortawesome/free-solid-svg-icons'

export default function Menu() {
    return (
        <div className={classes.menu}>
            <nav>
                <ul>
                    <MenuItem text="Mankkoo" link="/" icon={undefined}/>
                    <MenuItem text="Overview" link="/" icon={faGaugeHigh}/>
                    <MenuItem text="Accounts" link="/accounts" icon={faMoneyBillWave}/>
                    <MenuItem text="Investments" link="/investments" icon={faChartLine}/>
                    <MenuItem text="Financial Fortress" link="/fortress" icon={faChessRook}/>
                    <MenuItem text="Real Estate" link="/estate" icon={faBuildingUser}/>
                    <MenuItem text="Streams" link="/streams" icon={faServer}/>
                </ul>
            </nav>  
        </div>
    )
}