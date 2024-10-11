import classes from './menu.module.css'
import MenuItem from '@/components/menu-item/menu-item'

export default function Menu() {
    return (
        <div className={classes.menu}>
            <nav>
                <ul>
                    <MenuItem text="Mankkoo" link="/" />
                    <MenuItem text="Overview" link="/" />
                    <MenuItem text="Accounts" link="/accounts" />
                    <MenuItem text="Investments" link="/investments" />
                    <MenuItem text="Financial Fortress" link="/fortress" />
                    <MenuItem text="Real Estate" link="/estate" />
                    <MenuItem text="Streams" link="/streams" />
                </ul>
            </nav>  
        </div>
    )
}