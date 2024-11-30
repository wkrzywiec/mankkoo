import Link from 'next/link'
import classes from './MenuItem.module.css'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { IconDefinition } from '@fortawesome/fontawesome-common-types'

export default function MenuItem({text, link, icon}: {text: string, link: string, icon?: IconDefinition}) {
    const fontAwesomeIcon = (icon !== undefined) ? <FontAwesomeIcon icon={icon}/> : ""
    return (
        <li className={classes.menuItem}>
            <Link href={link}>
                {fontAwesomeIcon}
                <p>{text}</p>
            </Link>
        </li>
    )
}