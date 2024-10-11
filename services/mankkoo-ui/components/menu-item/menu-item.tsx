import Link from 'next/link'
import classes from './menu-item.module.css'

export default function MenuItem({text, link}: {text: string, link: string}) {
    return (
        <li className={classes.menuItem}>
            <Link href={link}>{text}</Link>
        </li>
    )
}